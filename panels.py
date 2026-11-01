# SPDX-License-Identifier: GPL-3.0-or-later
"""Simple FFD sidebar presentation."""
import bpy

from .lattice_service import managed_cage


class SIMPLEFFD_PT_panel(bpy.types.Panel):
    bl_label = 'Simple FFD'
    bl_idname = 'SIMPLEFFD_PT_panel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'pynk_p'

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        cage = managed_cage(obj)
        target = cage.simple_ffd_owner if cage else obj
        if target and target.type == 'MESH':
            layout.label(text='Control Points (Local Axes)')
            row = layout.row(align=True)
            row.prop(target.simple_ffd_settings, 'points_x')
            row.prop(target.simple_ffd_settings, 'points_y')
            row.prop(target.simple_ffd_settings, 'points_z')
        if cage:
            layout.label(text=cage.name, icon='MOD_LATTICE')
            data = cage.data
            layout.label(text=f'Current Grid: {data.points_u} x {data.points_v} x {data.points_w}')
            layout.operator('simple_ffd.update', icon='FILE_REFRESH')
            layout.label(text='Update Grid resets deformation', icon='INFO')
            if data.shape_keys or data.animation_data:
                layout.label(text='Grid update unavailable: shape keys or animation')
            layout.separator()
            layout.operator('simple_ffd.edit', icon='EDITMODE_HLT')
            layout.operator('simple_ffd.finish', icon='CHECKMARK')
            layout.separator()
            layout.operator('simple_ffd.reset', icon='LOOP_BACK')
            layout.separator()
            layout.label(text='Select points, then G / S / R')
            layout.label(text='Reopen editing at any time')
        else:
            layout.label(text='Select one mesh in Object Mode')
            column = layout.column(align=True)
            column.scale_y = 1.4
            column.operator('simple_ffd.create')
            if obj and obj.type == 'MESH' and any(m.type == 'LATTICE' for m in obj.modifiers):
                layout.label(text='Existing Lattice modifier found.', icon='INFO')
                layout.label(text='Disable unwanted modifiers first.')

        layout.separator()
        footer = layout.row()
        footer.enabled = False
        footer.label(text='Created by pynk_p')
