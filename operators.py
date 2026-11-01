# SPDX-License-Identifier: GPL-3.0-or-later
"""User actions, context validation and operator reports."""
import bpy

from .context_utils import edit_cage, select_only
from .lattice_service import (
    build_cage,
    managed_cage,
    reset_control_points,
    update_grid,
)
from .properties import requested_resolution


def can_update_grid(context, cage):
    if cage is None:
        return False
    owner = cage.simple_ffd_owner
    return (
        context.mode in {'OBJECT', 'EDIT_LATTICE'}
        and cage.name in context.view_layer.objects
        and cage.is_editable
        and cage.data.is_editable
        and owner is not None
        and owner.is_editable
        and cage.data.shape_keys is None
        and cage.data.animation_data is None
    )


class SIMPLEFFD_OT_create(bpy.types.Operator):
    bl_idname = 'simple_ffd.create'
    bl_label = 'Create Grid'
    bl_description = 'Fit an FFD cage to the active mesh and start editing control points'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (context.mode == 'OBJECT' and obj is not None
                and obj.type == 'MESH' and obj.is_editable
                and len(context.selected_objects) == 1
                and managed_cage(obj) is None)

    def execute(self, context):
        try:
            target = context.active_object
            cage = build_cage(context, target, requested_resolution(target))
        except Exception as error:
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        try:
            edit_cage(context, cage)
        except RuntimeError:
            self.report({'WARNING'}, 'Cage created. Click Edit Control Points to start editing.')
        return {'FINISHED'}


class SIMPLEFFD_OT_update(bpy.types.Operator):
    bl_idname = 'simple_ffd.update'
    bl_label = 'Update Grid'
    bl_description = 'Apply X/Y/Z counts and reset FFD deformation, keeping the cage position and size'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return can_update_grid(context, managed_cage(context.active_object))

    def execute(self, context):
        cage = managed_cage(context.active_object)
        was_editing = context.mode == 'EDIT_LATTICE'
        try:
            # Flush edit-mode points before copying or replacing lattice data.
            select_only(context, cage)
            update_grid(cage, requested_resolution(cage.simple_ffd_owner))
        except Exception as error:
            if was_editing:
                edit_cage(context, cage)
            self.report({'ERROR'}, str(error))
            return {'CANCELLED'}
        context.view_layer.update()
        try:
            edit_cage(context, cage)
        except RuntimeError:
            self.report({'WARNING'}, 'Grid updated. Click Edit Control Points to start editing.')
        return {'FINISHED'}


class SIMPLEFFD_OT_edit(bpy.types.Operator):
    bl_idname = 'simple_ffd.edit'
    bl_label = 'Edit Control Points'
    bl_description = 'Edit the linked FFD control points'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        cage = managed_cage(context.active_object)
        return (context.mode in {'OBJECT', 'EDIT_LATTICE'} and cage is not None
                and cage.name in context.view_layer.objects)

    def execute(self, context):
        edit_cage(context, managed_cage(context.active_object))
        return {'FINISHED'}


class SIMPLEFFD_OT_finish(bpy.types.Operator):
    bl_idname = 'simple_ffd.finish'
    bl_label = 'Finish Editing'
    bl_description = 'Keep the deformation, hide the cage, and select the mesh without applying the modifier'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        cage = managed_cage(context.active_object)
        owner = cage.simple_ffd_owner if cage else None
        return (context.mode in {'OBJECT', 'EDIT_LATTICE'} and owner is not None
                and owner.name in context.view_layer.objects)

    def execute(self, context):
        cage = managed_cage(context.active_object)
        select_only(context, cage.simple_ffd_owner)
        cage.hide_set(True)
        return {'FINISHED'}


class SIMPLEFFD_OT_reset(bpy.types.Operator):
    bl_idname = 'simple_ffd.reset'
    bl_label = 'Reset Deformation'
    bl_description = 'Reset this FFD deformation while keeping the cage position and size'
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        cage = managed_cage(context.active_object)
        return (context.mode in {'OBJECT', 'EDIT_LATTICE'} and cage is not None
                and cage.data.shape_keys is None
                and cage.name in context.view_layer.objects)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        cage = managed_cage(context.active_object)
        select_only(context, cage)
        reset_control_points(cage.data)
        context.view_layer.update()
        edit_cage(context, cage)
        return {'FINISHED'}
