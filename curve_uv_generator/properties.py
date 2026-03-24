import bpy
from bpy.props import PointerProperty, StringProperty
from bpy.types import PropertyGroup

from . import constants


class CUG_PG_Settings(PropertyGroup):
    node_group_name: StringProperty(
        name="Node Group",
        description="Node group name inside bundled gn_assets.blend",
        default=constants.NODE_GROUP_NAME,
    )


def register_properties() -> None:
    bpy.types.Scene.cug_settings = PointerProperty(type=CUG_PG_Settings)


def unregister_properties() -> None:
    if hasattr(bpy.types.Scene, "cug_settings"):
        del bpy.types.Scene.cug_settings
