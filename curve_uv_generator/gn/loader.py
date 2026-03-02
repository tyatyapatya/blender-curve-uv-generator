from pathlib import Path

import bpy
from bpy.types import NodeTree

from .. import constants


class NodeGroupLoadError(RuntimeError):
    pass


def _validate_resource_path(path: Path) -> None:
    if not path.exists():
        raise NodeGroupLoadError(
            f"Missing bundled resource file: {path}. "
            "Ship resources/gn_assets.blend with the add-on."
        )


def append_node_group_from_resource(node_group_name: str) -> NodeTree:
    resource_path = constants.resource_blend_path()
    _validate_resource_path(resource_path)

    with bpy.data.libraries.load(str(resource_path), link=False) as (data_from, data_to):
        if node_group_name not in data_from.node_groups:
            raise NodeGroupLoadError(
                f"Node group '{node_group_name}' not found in {resource_path.name}."
            )
        data_to.node_groups = [node_group_name]

    appended = data_to.node_groups[0]
    if appended is None:
        raise NodeGroupLoadError(f"Failed to append node group '{node_group_name}'.")

    appended[constants.NODE_GROUP_UID_PROP] = constants.NODE_GROUP_UID_VALUE
    return appended
