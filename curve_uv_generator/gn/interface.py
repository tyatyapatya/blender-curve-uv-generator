from __future__ import annotations

from bpy.types import Modifier, NodeTree

CANONICAL_SOCKET_ALIASES = {
    "profile_curve": ("Profile Curve", "Profile", "Profile Object"),
    "set_material": ("Set Material", "Material"),
    "path_resolution": ("Path Resolution", "Curve Resolution", "Path Res"),
    "profile_resolution": ("Profile Resolution", "Profile Res"),
    "tile_length": ("Tile Length", "Tile", "UV Tile Length"),
    "seam_rotate": ("Seam Rotate", "Rotate Seam", "UV Rotate"),
    "seam_offset": ("Seam Offset", "Offset Seam", "UV Offset"),
}


def _normalized(text: str) -> str:
    return "".join(ch for ch in text.lower() if ch.isalnum())


def _iter_input_sockets_from_node_group(node_group: NodeTree | None):
    if node_group is None:
        return
    interface = getattr(node_group, "interface", None)
    if interface is None:
        return

    for item in interface.items_tree:
        # Blender API changed shape over versions; check capability instead of exact enum.
        if getattr(item, "in_out", None) != "INPUT":
            continue
        if not getattr(item, "identifier", ""):
            continue
        yield item


def _iter_input_sockets(modifier: Modifier):
    node_group = None if modifier is None else modifier.node_group
    yield from _iter_input_sockets_from_node_group(node_group)


def _resolve_named_socket_in_node_group(
    node_group: NodeTree | None, aliases: tuple[str, ...], socket_type: str | None = None
):
    items = list(_iter_input_sockets_from_node_group(node_group))
    if not items:
        return None

    alias_norm = {_normalized(name) for name in aliases}

    for item in items:
        if socket_type and getattr(item, "socket_type", "") != socket_type:
            continue
        if _normalized(item.name) in alias_norm:
            return item

    for item in items:
        if socket_type and getattr(item, "socket_type", "") != socket_type:
            continue
        norm_name = _normalized(item.name)
        if any(alias in norm_name for alias in alias_norm):
            return item

    if socket_type:
        typed = [item for item in items if getattr(item, "socket_type", "") == socket_type]
        if len(typed) == 1:
            return typed[0]

    return None


def input_socket_map(modifier: Modifier) -> dict[str, object]:
    return {item.name: item for item in _iter_input_sockets(modifier)}


def resolve_named_socket(modifier: Modifier, aliases: tuple[str, ...], socket_type: str | None = None):
    node_group = None if modifier is None else modifier.node_group
    return _resolve_named_socket_in_node_group(node_group, aliases, socket_type=socket_type)


def resolve_canonical_inputs(modifier: Modifier) -> dict[str, object]:
    return {
        "profile_curve": resolve_named_socket(
            modifier,
            CANONICAL_SOCKET_ALIASES["profile_curve"],
            socket_type="NodeSocketObject",
        ),
        "set_material": resolve_named_socket(
            modifier,
            CANONICAL_SOCKET_ALIASES["set_material"],
            socket_type="NodeSocketMaterial",
        ),
        "path_resolution": resolve_named_socket(
            modifier,
            CANONICAL_SOCKET_ALIASES["path_resolution"],
        ),
        "profile_resolution": resolve_named_socket(
            modifier,
            CANONICAL_SOCKET_ALIASES["profile_resolution"],
        ),
        "tile_length": resolve_named_socket(
            modifier,
            CANONICAL_SOCKET_ALIASES["tile_length"],
        ),
        "seam_rotate": resolve_named_socket(
            modifier,
            CANONICAL_SOCKET_ALIASES["seam_rotate"],
        ),
        "seam_offset": resolve_named_socket(
            modifier,
            CANONICAL_SOCKET_ALIASES["seam_offset"],
        ),
    }


def node_group_has_required_inputs(node_group: NodeTree | None) -> bool:
    # Required for the add-on UI/ops to be fully usable.
    required = (
        ("profile_curve", "NodeSocketObject"),
        ("set_material", "NodeSocketMaterial"),
        ("path_resolution", None),
        ("profile_resolution", None),
        ("tile_length", None),
        ("seam_rotate", None),
        ("seam_offset", None),
    )
    for key, socket_type in required:
        item = _resolve_named_socket_in_node_group(
            node_group,
            CANONICAL_SOCKET_ALIASES[key],
            socket_type=socket_type,
        )
        if item is None:
            return False
    return True
