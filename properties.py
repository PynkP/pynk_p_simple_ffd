# SPDX-License-Identifier: GPL-3.0-or-later
"""Per-object pending grid settings."""
import bpy
from bpy.props import IntProperty


class SIMPLEFFD_PG_settings(bpy.types.PropertyGroup):
    """Pending counts; editing these never changes lattice geometry."""

    points_x: IntProperty(name='X', default=4, min=2, max=16)
    points_y: IntProperty(name='Y', default=4, min=2, max=16)
    points_z: IntProperty(name='Z', default=4, min=2, max=16)


def requested_resolution(target):
    settings = target.simple_ffd_settings
    return (settings.points_x, settings.points_y, settings.points_z)
