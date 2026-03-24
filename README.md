# Blender Curve UV Generator

Blender add-on that applies an existing Geometry Nodes setup (`Curve_UV.002`) to selected path curves.

## What this implementation does

- Uses a bundled resource file: `curve_uv_generator/resources/gn_assets.blend`
- Appends the existing node group at runtime
- Applies the group to selected curve objects via a Geometry Nodes modifier
- Identifies managed node groups/modifiers with internal UID properties to avoid name-collision issues

## Install for testing

1. Zip the `curve_uv_generator` folder.
2. Install zip in Blender:
   - `Edit > Preferences > Add-ons > Install...`

## Learn the code structure

See `docs/FILE_GUIDE.md` for a file-by-file explanation.
