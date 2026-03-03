import bpy
from bpy.types import Panel

from .. import constants
from ..gn.assign import get_applied_modifier
from ..gn.interface import CANONICAL_SOCKET_ALIASES, resolve_canonical_inputs
from ..utils.context import active_curve_object

DESIRED_INPUT_ORDER = (
    "profile_curve",
    "set_material",
    "path_resolution",
    "profile_resolution",
    "tile_length",
    "seam_rotate",
    "seam_offset",
)


def _display_name(key: str) -> str:
    return CANONICAL_SOCKET_ALIASES[key][0]


def _draw_modifier_inputs(layout, modifier):
    resolved = resolve_canonical_inputs(modifier)

    for key in DESIRED_INPUT_ORDER:
        name = _display_name(key)
        item = resolved.get(key)
        if item is None:
            layout.label(text=f"Missing input: {name}", icon="ERROR")
            continue

        prop_path = f'["{item.identifier}"]'

        if key == "tile_length":
            row = layout.row(align=True)
            row.prop(modifier, prop_path, text=name)
            row.operator("curve_uv_generator.auto_tile_length", text="Auto", icon="FILE_REFRESH")
            continue

        if key == "profile_curve":
            try:
                layout.prop_search(modifier, prop_path, bpy.data, "objects", text=name, icon="OUTLINER_OB_CURVE")
            except Exception:
                layout.prop(modifier, prop_path, text=name)
        elif key == "set_material":
            try:
                layout.prop_search(modifier, prop_path, bpy.data, "materials", text=name, icon="MATERIAL")
            except Exception:
                layout.prop(modifier, prop_path, text=name)
        else:
            layout.prop(modifier, prop_path, text=name)


class CUG_PT_main(Panel):
    bl_label = "Curve UV Generator"
    bl_idname = "CUG_PT_main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Curve UV"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cug_settings
        active_curve = active_curve_object(context)
        modifier = get_applied_modifier(active_curve)

        box = layout.box()
        row = box.row()
        row.scale_y = 1.2
        row.operator("curve_uv_generator.apply_uv_setup", text="Generate UV", icon="GEOMETRY_NODES")

        if constants.SHOW_SETTINGS_BOX:
            box2 = layout.box()
            box2.label(text="Settings")
            box2.prop(settings, "node_group_name", text="Node Group")

        box3 = layout.box()
        box3.label(text="Parameters")
        if active_curve is None:
            box3.label(text="No active curve selected.", icon="INFO")
            return
        if modifier is None:
            box3.label(text="Apply setup first to this curve.", icon="INFO")
            return

        _draw_modifier_inputs(box3, modifier)


class CUG_PT_object_props(Panel):
    bl_label = "Curve UV Generator"
    bl_idname = "CUG_PT_object_props"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        settings = context.scene.cug_settings
        active_curve = active_curve_object(context)
        modifier = get_applied_modifier(active_curve)

        layout.operator("curve_uv_generator.apply_uv_setup", text="Generate UV", icon="GEOMETRY_NODES")

        if constants.SHOW_SETTINGS_BOX:
            layout.prop(settings, "node_group_name", text="Node Group")

        box = layout.box()
        box.label(text="Parameters")
        if active_curve is None:
            box.label(text="No active curve selected.", icon="INFO")
            return
        if modifier is None:
            box.label(text="Apply setup first to this curve.", icon="INFO")
            return

        _draw_modifier_inputs(box, modifier)
