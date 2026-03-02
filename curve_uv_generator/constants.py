from pathlib import Path

ADDON_ID = "curve_uv_generator"
ADDON_LABEL = "Curve UV Generator"

# Source node group name inside resources/gn_assets.blend
NODE_GROUP_NAME = "Curve_UV_Generator"

# Toggle developer settings UI section (Node Group override field).
SHOW_SETTINGS_BOX = False

# Auto Tile Length behavior.
# If True, snap repeat count along path to a whole number to avoid partial/cut tile at the end.
AUTO_TILE_SNAP_REPEATS = True
# 'round' gives closest count, 'floor' avoids overshooting, 'ceil' avoids undershooting.
AUTO_TILE_REPEAT_ROUND_MODE = "round"

# Internal marker used to identify this add-on managed group.
NODE_GROUP_UID_PROP = "curve_uv_generator_uid"
NODE_GROUP_UID_VALUE = "com.scryi.curve_uv_generator.curve_uv_002.v1"

MODIFIER_NAME = "CurveUV"
MODIFIER_UID_PROP = "curve_uv_generator_modifier_uid"
MODIFIER_UID_VALUE = "com.scryi.curve_uv_generator.modifier.v1"

RESOURCE_SUBDIR = "resources"
RESOURCE_BLEND_FILENAME = "curve-uv-generator.blend"


def addon_root() -> Path:
    return Path(__file__).resolve().parent


def resource_blend_path() -> Path:
    return addon_root() / RESOURCE_SUBDIR / RESOURCE_BLEND_FILENAME
