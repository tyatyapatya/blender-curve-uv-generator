import bpy

from .operators.apply_uv_gn import CUG_OT_apply_uv_setup
from .operators.auto_tile_length import CUG_OT_auto_tile_length
from .properties import CUG_PG_Settings, register_properties, unregister_properties
from .ui.panel_main import CUG_PT_main, CUG_PT_object_props

CLASSES = (
    CUG_PG_Settings,
    CUG_OT_apply_uv_setup,
    CUG_OT_auto_tile_length,
    CUG_PT_main,
    CUG_PT_object_props,
)


def _menu_func(self, context):
    self.layout.separator()
    self.layout.operator(
        "curve_uv_generator.apply_uv_setup",
        text="Apply Curve UV Setup",
        icon="GEOMETRY_NODES",
    )


def register() -> None:
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    register_properties()
    bpy.types.VIEW3D_MT_object.append(_menu_func)


def unregister() -> None:
    if hasattr(bpy.types, "VIEW3D_MT_object"):
        try:
            bpy.types.VIEW3D_MT_object.remove(_menu_func)
        except Exception:
            pass
    unregister_properties()
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)
