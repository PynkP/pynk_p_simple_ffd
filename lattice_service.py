# SPDX-License-Identifier: GPL-3.0-or-later
"""Lattice geometry and ownership operations, independent of panel state."""
import bpy
from mathutils import Matrix, Vector

from .constants import MARKER


def reset_control_points(data):
    for point in data.points:
        point.co_deform = point.co.copy()
    data.update_tag()


def configure_grid(data, resolution):
    """Set topology and neutral B-Spline points, independent of UI context."""
    data.points_u, data.points_v, data.points_w = resolution
    data.interpolation_type_u = 'KEY_BSPLINE'
    data.interpolation_type_v = 'KEY_BSPLINE'
    data.interpolation_type_w = 'KEY_BSPLINE'
    reset_control_points(data)


def resolution_label(resolution):
    return 'x'.join(str(count) for count in resolution)


def rest_frame(data):
    """Map a unit box to the lattice's undeformed local bounds."""
    lower = Vector(tuple(min(point.co[i] for point in data.points) for i in range(3)))
    upper = Vector(tuple(max(point.co[i] for point in data.points) for i in range(3)))
    extent = upper - lower
    return Matrix.Translation((lower + upper) * 0.5) @ Matrix.Diagonal((*extent, 1.0))


def update_grid(cage, resolution):
    """Prepare a private data copy before replacing the existing grid.

    The cage object, world-space rest bounds, parenting and modifiers stay intact.
    Copying also prevents changes to other objects sharing the old data.
    """
    old_data = cage.data
    old_basis = cage.matrix_basis.copy()
    old_frame = rest_frame(old_data)
    new_data = old_data.copy()
    try:
        configure_grid(new_data, resolution)
        # Blender can change the neutral coordinate range when resizing data.
        # Compensate in object space so the physical cage box stays unchanged.
        new_basis = old_basis @ old_frame @ rest_frame(new_data).inverted()
        cage.data = new_data
        cage.matrix_basis = new_basis
    except Exception:
        cage.data = old_data
        cage.matrix_basis = old_basis
        bpy.data.lattices.remove(new_data)
        raise
    if old_data.users == 0 and not old_data.use_fake_user:
        bpy.data.lattices.remove(old_data)


def managed_cage(obj):
    if obj and obj.type == 'LATTICE' and obj.get(MARKER):
        return obj
    if obj and obj.type == 'MESH':
        for mod in reversed(obj.modifiers):
            if mod.type == 'LATTICE' and mod.object and mod.object.get(MARKER):
                return mod.object
    return None


def build_cage(context, target, resolution):
    """Fit a neutral cage to evaluated geometry in the target's local frame.

    Only object transforms perform fitting. co_deform is explicitly set to co,
    so adding the modifier cannot inherit an accidental edit-mode deformation.
    """
    if abs(target.matrix_world.determinant()) < 1e-12:
        raise ValueError("The mesh transform is singular. Set all scale axes to nonzero values.")
    evaluated = target.evaluated_get(context.evaluated_depsgraph_get())
    if not evaluated.data.vertices:
        raise ValueError("Select a mesh with vertices.")
    bounds = [Vector(corner) for corner in evaluated.bound_box]
    lower = Vector(tuple(min(p[i] for p in bounds) for i in range(3)))
    upper = Vector(tuple(max(p[i] for p in bounds) for i in range(3)))
    center = (lower + upper) * 0.5
    extent = upper - lower
    minimum = max(max(extent) * 0.001, 0.0001)
    size = Vector(tuple(max(value * 1.02, minimum) for value in extent))
    data = bpy.data.lattices.new("Simple FFD Grid")
    cage = None
    modifier = None
    try:
        configure_grid(data, resolution)
        rest = [p.co.copy() for p in data.points]
        rest_lower = Vector(tuple(min(p[i] for p in rest) for i in range(3)))
        rest_upper = Vector(tuple(max(p[i] for p in rest) for i in range(3)))
        rest_center = (rest_lower + rest_upper) * 0.5
        factors = size / 1.0
        for i in range(3):
            factors[i] = size[i] / (rest_upper[i] - rest_lower[i])
        cage = bpy.data.objects.new(f"FFD_{resolution_label(resolution)}_{target.name}", data)
        context.collection.objects.link(cage)
        cage[MARKER] = True
        cage.simple_ffd_owner = target
        cage.parent = target
        cage.matrix_parent_inverse = Matrix.Identity(4)
        cage.matrix_basis = (Matrix.Translation(center)
                             @ Matrix.Diagonal((*factors, 1.0))
                             @ Matrix.Translation(-rest_center))
        cage.show_in_front = True
        cage.display_type = 'WIRE'
        cage.hide_render = True
        modifier = target.modifiers.new('Simple FFD', 'LATTICE')
        modifier.object = cage
        modifier.strength = 1.0
        context.view_layer.update()
        return cage
    except Exception:
        if modifier:
            target.modifiers.remove(modifier)
        if cage:
            bpy.data.objects.remove(cage, do_unlink=True)
        if data.users == 0:
            bpy.data.lattices.remove(data)
        raise
