# File Guide

This document explains each file in the add-on, why it exists, and how data flows through the project.

## High-level flow

1. User selects one or more curve objects.
2. User clicks **Apply Curve UV Setup** in the panel.
3. Operator resolves an existing managed node group or appends it from `resources/gn_assets.blend`.
4. Operator applies that node group to selected curves through a Geometry Nodes modifier.

## Folder layout

```text
curve_uv_generator/
  __init__.py
  constants.py
  registration.py
  properties.py
  operators/
    __init__.py
    apply_uv_gn.py
  ui/
    __init__.py
    panel_main.py
  gn/
    __init__.py
    resolver.py
    loader.py
    assign.py
  utils/
    __init__.py
    context.py
    logging.py
  resources/
    README.txt
```

## File-by-file explanation

### `curve_uv_generator/__init__.py`

- Contains `bl_info` metadata Blender uses for add-on listing.
- Exposes `register()` / `unregister()` by importing from `registration.py`.
- Keep this file small and declarative.

### `curve_uv_generator/constants.py`

- Central place for stable identifiers and paths.
- Defines:
  - Node group name expected in resource blend (`Curve_UV.002`)
  - Internal UID property keys/values used to mark managed assets
  - Modifier naming/UID constants
  - Resource file location (`resources/gn_assets.blend`)
- Why: avoids string duplication and makes updates predictable.

### `curve_uv_generator/registration.py`

- Single place that defines class registration order.
- Registers classes in forward order and unregisters in reverse.
- Calls property attach/detach helpers.
- Why: Blender class registration order can break add-ons if spread across modules.

### `curve_uv_generator/properties.py`

- Defines `CUG_PG_Settings` (`PropertyGroup`) attached to `Scene`.
- Current field:
  - `node_group_name` (default `Curve_UV.002`)
- Why: keeps user-configurable settings structured and Blender-native.

### `curve_uv_generator/operators/__init__.py`

- Package marker only.
- Keeps import boundaries explicit.

### `curve_uv_generator/operators/apply_uv_gn.py`

- Main operator (`curve_uv_generator.apply_uv_setup`).
- Responsibilities:
  - Validate context (selected curves)
  - Resolve existing managed node group
  - Append from resource if missing
  - Apply node group modifier to selected curves
  - Report success/failure in Blender UI
- Why: all user-triggered action logic lives in one operator module.

### `curve_uv_generator/ui/__init__.py`

- Package marker only.

### `curve_uv_generator/ui/panel_main.py`

- Sidebar panel in View3D (`Curve UV` tab).
- Draws:
  - `node_group_name` field
  - Apply operator button
- Why: keeps UI concerns separate from data and operator logic.

### `curve_uv_generator/gn/__init__.py`

- Package marker for Geometry Nodes-specific services.

### `curve_uv_generator/gn/resolver.py`

- Finds node groups already in current `.blend`.
- Lookup order:
  1. UID-marked managed group
  2. Name match fallback
- If name match is used, it tags group with managed UID.
- Why: robust behavior across name collisions and duplicated groups.

### `curve_uv_generator/gn/loader.py`

- Appends node group from bundled `gn_assets.blend`.
- Uses `bpy.data.libraries.load(..., link=False)`.
- Validates missing file and missing group with clear errors.
- Tags appended group with managed UID.
- Why: this is the release-grade packaging strategy for public add-ons.

### `curve_uv_generator/gn/assign.py`

- Finds/creates a Geometry Nodes modifier on target curve object.
- Prefers managed modifier by UID; otherwise reuses named modifier; otherwise creates new.
- Assigns resolved node group to modifier.
- Why: keeps modifier lifecycle logic isolated and testable.

### `curve_uv_generator/utils/__init__.py`

- Package marker only.

### `curve_uv_generator/utils/context.py`

- Small context helpers:
  - active curve object lookup
  - selected curve objects list
- Why: avoids repeating context filtering in operators/UI.

### `curve_uv_generator/utils/logging.py`

- Minimal logger accessor.
- Keeps logging setup centralized.

### `curve_uv_generator/resources/README.txt`

- Documents required bundled file and required node group name.
- This folder is where `gn_assets.blend` must be stored for release.

## Naming conventions used

- Prefix `CUG_` for Blender classes:
  - `CUG_PG_` = PropertyGroup
  - `CUG_OT_` = Operator
  - `CUG_PT_` = Panel
- Lowercase snake_case for module names.
- Stable UID constants in `constants.py` for managed data-block identification.

## Why this architecture is maintainable

- UI, operators, GN data access, and assignment are isolated by responsibility.
- All hard-coded identifiers are centralized.
- Runtime dependency (`gn_assets.blend`) is explicit and documented.
- Extension points are clear:
  - Add new operators under `operators/`
  - Add additional panels under `ui/`
  - Add GN migration/version logic under `gn/`
