# SPDX-License-Identifier: GPL-3.0-or-later
"""Simple FFD extension registration entry point."""
import bpy
from bpy.props import PointerProperty

from .operators import (
    SIMPLEFFD_OT_create,
    SIMPLEFFD_OT_edit,
    SIMPLEFFD_OT_finish,
    SIMPLEFFD_OT_reset,
    SIMPLEFFD_OT_update,
)
from .panels import SIMPLEFFD_PT_panel
from .properties import SIMPLEFFD_PG_settings


CLASSES = (
    SIMPLEFFD_PG_settings,
    SIMPLEFFD_OT_create,
    SIMPLEFFD_OT_update,
    SIMPLEFFD_OT_edit,
    SIMPLEFFD_OT_finish,
    SIMPLEFFD_OT_reset,
    SIMPLEFFD_PT_panel,
)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Object.simple_ffd_owner = PointerProperty(type=bpy.types.Object)
    bpy.types.Object.simple_ffd_settings = PointerProperty(type=SIMPLEFFD_PG_settings)


def unregister():
    del bpy.types.Object.simple_ffd_settings
    del bpy.types.Object.simple_ffd_owner
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
