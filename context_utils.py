# SPDX-License-Identifier: GPL-3.0-or-later
"""Selection and mode transitions for Blender operators."""
import bpy


def select_only(context, obj):
    if context.object and context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    obj.hide_set(False)
    obj.hide_select = False
    for selected in list(context.selected_objects):
        selected.select_set(False)
    obj.select_set(True)
    context.view_layer.objects.active = obj


def edit_cage(context, cage):
    select_only(context, cage)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.lattice.select_all(action='DESELECT')
