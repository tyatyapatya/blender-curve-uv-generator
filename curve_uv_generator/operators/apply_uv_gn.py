from bpy.types import Context, Operator

from ..gn.assign import apply_node_group
from ..gn.loader import NodeGroupLoadError, append_node_group_from_resource
from ..gn.resolver import resolve_existing_node_group
from ..utils.context import target_curve_objects


class CUG_OT_apply_uv_setup(Operator):
    bl_idname = "curve_uv_generator.apply_uv_setup"
    bl_label = "Apply Curve UV Setup"
    bl_description = "Append the bundled Geometry Nodes group and apply it to selected curves"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context: Context) -> bool:
        # Keep button visible in panel; validate concrete targets in execute().
        return context.scene is not None

    def execute(self, context: Context):
        curves = target_curve_objects(context)
        if not curves:
            self.report({"ERROR"}, "Select or activate a curve object.")
            return {"CANCELLED"}

        settings = context.scene.cug_settings
        target_group_name = settings.node_group_name.strip()
        if not target_group_name:
            self.report({"ERROR"}, "Node group name is empty.")
            return {"CANCELLED"}

        node_group = resolve_existing_node_group(target_group_name)
        if node_group is None:
            try:
                node_group = append_node_group_from_resource(target_group_name)
            except NodeGroupLoadError as exc:
                self.report({"ERROR"}, str(exc))
                return {"CANCELLED"}

        for curve_obj in curves:
            apply_node_group(curve_obj, node_group)

        self.report(
            {"INFO"},
            f"Applied '{node_group.name}' to {len(curves)} curve object(s).",
        )
        return {"FINISHED"}
