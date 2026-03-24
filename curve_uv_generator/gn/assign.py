from bpy.types import Modifier, NodeTree, Object

from .. import constants


def _find_managed_modifier(obj: Object) -> Modifier | None:
    for mod in obj.modifiers:
        if mod.type != "NODES":
            continue
        if mod.get(constants.MODIFIER_UID_PROP) == constants.MODIFIER_UID_VALUE:
            return mod
    return None


def _find_reusable_nodes_modifier(obj: Object) -> Modifier | None:
    for mod in obj.modifiers:
        if mod.type == "NODES" and mod.name == constants.MODIFIER_NAME:
            return mod
    return None


def ensure_uv_modifier(obj: Object) -> Modifier:
    mod = _find_managed_modifier(obj)
    if mod is None:
        mod = _find_reusable_nodes_modifier(obj)
    if mod is None:
        mod = obj.modifiers.new(name=constants.MODIFIER_NAME, type="NODES")
    mod[constants.MODIFIER_UID_PROP] = constants.MODIFIER_UID_VALUE
    return mod


def apply_node_group(obj: Object, node_group: NodeTree) -> Modifier:
    mod = ensure_uv_modifier(obj)
    mod.node_group = node_group
    return mod


def get_applied_modifier(obj: Object | None) -> Modifier | None:
    if obj is None:
        return None
    mod = _find_managed_modifier(obj)
    if mod is not None:
        return mod
    # Fallback for older files where modifier uid may not be set yet.
    for candidate in obj.modifiers:
        if candidate.type == "NODES" and candidate.node_group is not None:
            if candidate.node_group.get(constants.NODE_GROUP_UID_PROP) == constants.NODE_GROUP_UID_VALUE:
                return candidate
            if candidate.node_group.name == constants.NODE_GROUP_NAME:
                return candidate
    return None
