import math

from bpy.types import Context, Operator

from .. import constants
from ..gn.assign import get_applied_modifier
from ..utils.context import active_curve_object


def _input_socket_map(modifier):
    if modifier is None or modifier.node_group is None:
        return {}
    sock_map = {}
    for item in modifier.node_group.interface.items_tree:
        if getattr(item, "item_type", None) != "SOCKET":
            continue
        if item.in_out != "INPUT":
            continue
        sock_map[item.name] = item
    return sock_map


def _curve_length(curve_obj) -> float:
    total = 0.0
    world_scale = curve_obj.matrix_world.to_scale()
    avg_scale = max((abs(world_scale.x) + abs(world_scale.y) + abs(world_scale.z)) / 3.0, 1e-9)

    for spline in curve_obj.data.splines:
        try:
            total += float(spline.calc_length())
            continue
        except Exception:
            pass

        # Fallback: control-polygon approximation
        if spline.type == "BEZIER":
            points = [bp.co for bp in spline.bezier_points]
        else:
            points = [p.co.xyz for p in spline.points]

        if len(points) < 2:
            continue
        for idx in range(len(points) - 1):
            total += (points[idx + 1] - points[idx]).length
        if getattr(spline, "use_cyclic_u", False):
            total += (points[0] - points[-1]).length

    # Use world-space estimate so tile length remains stable for non-applied object scale.
    return total * avg_scale


def _material_aspect_ratio(material) -> float:
    if material is None or not material.use_nodes or material.node_tree is None:
        return 1.0

    for node in material.node_tree.nodes:
        if node.bl_idname != "ShaderNodeTexImage":
            continue
        image = node.image
        if image is None or len(image.size) < 2:
            continue
        width, height = image.size[0], image.size[1]
        if width > 0 and height > 0:
            return float(width) / float(height)
    return 1.0


def _snapped_tile_length(path_length: float, base_tile: float) -> tuple[float, int]:
    repeats = path_length / max(base_tile, 1e-9)
    mode = (constants.AUTO_TILE_REPEAT_ROUND_MODE or "round").lower()
    if mode == "floor":
        count = int(math.floor(repeats))
    elif mode == "ceil":
        count = int(math.ceil(repeats))
    else:
        count = int(round(repeats))
    count = max(1, count)
    return path_length / count, count


def _force_viewport_refresh(context: Context, curve_obj, modifier, tile_identifier: str, tile_value: float) -> None:
    # Nudge value to ensure depsgraph marks change in all contexts.
    modifier[tile_identifier] = tile_value + 1e-6
    modifier[tile_identifier] = tile_value

    # Toggle viewport flag to guarantee geometry re-evaluation.
    viewport_state = modifier.show_viewport
    modifier.show_viewport = not viewport_state
    modifier.show_viewport = viewport_state

    # Mark IDs dirty for redraw/evaluation.
    try:
        curve_obj.data.update()
    except Exception:
        pass

    try:
        curve_obj.update_tag(refresh={"DATA"})
    except Exception:
        curve_obj.update_tag()

    context.view_layer.update()

    wm = context.window_manager
    for window in wm.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            area.tag_redraw()


def _format_snap_info(enabled: bool, repeats: int | None) -> str:
    if not enabled or repeats is None:
        return ""
    return f", repeats {repeats:d}"


class CUG_OT_auto_tile_length(Operator):
    bl_idname = "curve_uv_generator.auto_tile_length"
    bl_label = "Auto Tile Length"
    bl_description = "Estimate Tile Length from profile curve perimeter and texture aspect ratio"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        curve_obj = active_curve_object(context)
        if curve_obj is None:
            return False
        modifier = get_applied_modifier(curve_obj)
        if modifier is None:
            return False
        sock_map = _input_socket_map(modifier)
        return "Tile Length" in sock_map and "Profile Curve" in sock_map

    def execute(self, context: Context):
        curve_obj = active_curve_object(context)
        if curve_obj is None:
            self.report({"ERROR"}, "No active curve object.")
            return {"CANCELLED"}

        modifier = get_applied_modifier(curve_obj)
        if modifier is None:
            self.report({"ERROR"}, "Apply setup first to this curve.")
            return {"CANCELLED"}

        sock_map = _input_socket_map(modifier)
        tile_sock = sock_map.get("Tile Length")
        profile_sock = sock_map.get("Profile Curve")
        material_sock = sock_map.get("Set Material")

        if tile_sock is None or profile_sock is None:
            self.report({"ERROR"}, "Required modifier inputs missing (Tile Length/Profile Curve).")
            return {"CANCELLED"}

        profile_obj = modifier.get(profile_sock.identifier)
        if profile_obj is None:
            self.report({"ERROR"}, "Set Profile Curve first.")
            return {"CANCELLED"}
        if getattr(profile_obj, "type", None) != "CURVE":
            self.report({"ERROR"}, "Profile Curve must be a Curve object.")
            return {"CANCELLED"}

        perimeter = _curve_length(profile_obj)
        if perimeter <= 1e-9:
            self.report({"ERROR"}, "Profile Curve length is zero.")
            return {"CANCELLED"}

        material = modifier.get(material_sock.identifier) if material_sock else None
        aspect = _material_aspect_ratio(material)
        tile_length = max(perimeter * aspect, 1e-6)

        repeats = None
        if constants.AUTO_TILE_SNAP_REPEATS:
            path_length = _curve_length(curve_obj)
            if path_length > 1e-9:
                tile_length, repeats = _snapped_tile_length(path_length, tile_length)

        modifier[tile_sock.identifier] = tile_length
        _force_viewport_refresh(context, curve_obj, modifier, tile_sock.identifier, tile_length)

        snap_info = _format_snap_info(constants.AUTO_TILE_SNAP_REPEATS, repeats)
        self.report(
            {"INFO"},
            (
                f"Tile Length set to {tile_length:.6f} "
                f"(profile {perimeter:.6f}, aspect {aspect:.3f}{snap_info})."
            ),
        )
        return {"FINISHED"}
