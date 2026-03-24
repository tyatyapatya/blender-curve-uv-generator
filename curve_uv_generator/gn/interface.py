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

    items = getattr(interface, "items_tree", None)
    if items is None:
        items = getattr(interface, "items", None)
    if items is None:
        return

    for item in items:
        # Blender API changed shape over versions; check capability instead of exact enum.
        if getattr(item, "in_out", None) != "INPUT":
            continue
        if not getattr(item, "identifier", ""):
            continue
        yield item


def _socket_type_names(item: object) -> set[str]:
    values = {
        getattr(item, "socket_type", ""),
        getattr(item, "bl_socket_idname", ""),
        getattr(item, "type", ""),
        item.__class__.__name__,
    }
    return {_normalized(v) for v in values if isinstance(v, str) and v}


def _matches_socket_type(item: object, expected: str | None) -> bool:
    if expected is None:
        return True

    expected_norm = _normalized(expected)
    names = _socket_type_names(item)
    if expected_norm in names:
        return True

    # Cross-version fallback:
    # NodeSocketObject <-> Object, NodeSocketMaterial <-> Material, etc.
    if expected_norm.startswith("nodesocket"):
        bare = expected_norm.removeprefix("nodesocket")
        return bare in names

    return f"nodesocket{expected_norm}" in names


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
        if not _matches_socket_type(item, socket_type):
            continue
        if _normalized(item.name) in alias_norm:
            return item

    for item in items:
        if not _matches_socket_type(item, socket_type):
            continue
        norm_name = _normalized(item.name)
        if any(alias in norm_name for alias in alias_norm):
            return item

    if socket_type:
        typed = [item for item in items if _matches_socket_type(item, socket_type)]
        if len(typed) == 1:
            return typed[0]

    return None


def input_socket_map(modifier: Modifier) -> dict[str, object]:
    return {item.name: item for item in _iter_input_sockets(modifier)}


def resolve_named_socket(modifier: Modifier, aliases: tuple[str, ...], socket_type: str | None = None):
    node_group = None if modifier is None else modifier.node_group
    return _resolve_named_socket_in_node_group(node_group, aliases, socket_type=socket_type)


def resolve_canonical_inputs(modifier: Modifier) -> dict[str, object]:
    node_group = None if modifier is None else modifier.node_group
    ensure_legacy_profile_material_inputs(node_group)

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


def _find_group_input_node(node_group: NodeTree | None):
    if node_group is None:
        return None
    for node in node_group.nodes:
        if node.bl_idname == "NodeGroupInput":
            return node
    return None


def _find_node_by_type(node_group: NodeTree | None, bl_idname: str):
    if node_group is None:
        return None
    for node in node_group.nodes:
        if node.bl_idname == bl_idname:
            return node
    return None


def _find_socket_by_name(sockets, name: str):
    target = _normalized(name)
    for sock in sockets:
        if _normalized(getattr(sock, "name", "")) == target:
            return sock
    return None


def _create_input_socket(node_group: NodeTree | None, name: str, socket_type: str):
    if node_group is None:
        return None
    interface = getattr(node_group, "interface", None)
    if interface is None:
        return None
    create = getattr(interface, "new_socket", None)
    if create is None:
        return None

    # Blender changed signature ordering/keywords across versions.
    attempts = (
        {"name": name, "in_out": "INPUT", "socket_type": socket_type},
        {"name": name, "socket_type": socket_type, "in_out": "INPUT"},
        {"name": name, "in_out": "INPUT"},
    )
    for kwargs in attempts:
        try:
            return create(**kwargs)
        except TypeError:
            continue
        except Exception:
            return None
    return None


def _ensure_link_from_group_input(node_group: NodeTree | None, input_name: str, target_node, target_input_name: str) -> bool:
    if node_group is None or target_node is None:
        return False

    group_input = _find_group_input_node(node_group)
    if group_input is None:
        return False

    target_input = _find_socket_by_name(target_node.inputs, target_input_name)
    if target_input is None:
        return False
    if target_input.is_linked:
        return True

    source_output = _find_socket_by_name(group_input.outputs, input_name)
    if source_output is None:
        return False

    try:
        node_group.links.new(source_output, target_input)
        return True
    except Exception:
        return False


def ensure_legacy_profile_material_inputs(node_group: NodeTree | None) -> bool:
    """
    Some shipped node-group revisions accidentally hid Profile/Material interface sockets
    while still containing internal Object Info / Set Material nodes.
    Restore those interface inputs and links so panel selectors and Auto Tile work.
    """
    if node_group is None:
        return False

    changed = False
    profile_item = _resolve_named_socket_in_node_group(
        node_group,
        CANONICAL_SOCKET_ALIASES["profile_curve"],
        socket_type="NodeSocketObject",
    )
    material_item = _resolve_named_socket_in_node_group(
        node_group,
        CANONICAL_SOCKET_ALIASES["set_material"],
        socket_type="NodeSocketMaterial",
    )

    object_info = _find_node_by_type(node_group, "GeometryNodeObjectInfo")
    set_material = _find_node_by_type(node_group, "GeometryNodeSetMaterial")

    if profile_item is None and object_info is not None:
        created = _create_input_socket(node_group, CANONICAL_SOCKET_ALIASES["profile_curve"][0], "NodeSocketObject")
        if created is not None:
            changed = True

    if material_item is None and set_material is not None:
        created = _create_input_socket(node_group, CANONICAL_SOCKET_ALIASES["set_material"][0], "NodeSocketMaterial")
        if created is not None:
            changed = True

    # Resolve again after potential creation.
    profile_item = _resolve_named_socket_in_node_group(
        node_group,
        CANONICAL_SOCKET_ALIASES["profile_curve"],
        socket_type="NodeSocketObject",
    )
    material_item = _resolve_named_socket_in_node_group(
        node_group,
        CANONICAL_SOCKET_ALIASES["set_material"],
        socket_type="NodeSocketMaterial",
    )

    if profile_item is not None and object_info is not None:
        if _ensure_link_from_group_input(node_group, profile_item.name, object_info, "Object"):
            changed = True

    if material_item is not None and set_material is not None:
        if _ensure_link_from_group_input(node_group, material_item.name, set_material, "Material"):
            changed = True

    return changed
