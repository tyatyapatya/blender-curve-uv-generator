from bpy.types import NodeTree
import bpy

from .. import constants


def find_node_group_by_uid() -> NodeTree | None:
    for group in bpy.data.node_groups:
        if group.get(constants.NODE_GROUP_UID_PROP) == constants.NODE_GROUP_UID_VALUE:
            return group
    return None


def find_node_group_by_name(name: str) -> NodeTree | None:
    return bpy.data.node_groups.get(name)


def resolve_existing_node_group(preferred_name: str) -> NodeTree | None:
    group = find_node_group_by_uid()
    if group is not None:
        return group

    group = find_node_group_by_name(preferred_name)
    if group is None:
        return None

    group[constants.NODE_GROUP_UID_PROP] = constants.NODE_GROUP_UID_VALUE
    return group
