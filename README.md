# Blender Curve UV Generator

Sweep a profile along a path curve and generate UVs for repeating textures. The add-on includes its Geometry Nodes setup and applies it to selected curves as a modifier. Controls for the profile, material, texture tiling, and UV seam are available in Blender's interface.

## Install

Requires Blender 5.0 or later.

Download the add-on ZIP from the [latest release](https://github.com/tyatyapatya/blender-curve-uv-generator/releases/latest). Choose the ZIP under **Assets**, not the source code archive.

In Blender, go to **Edit → Preferences → Add-ons → Install from Disk** and select the ZIP.

## Use

1. Create a path curve and a separate curve for its cross-section. Select the path in Object Mode.
2. In the 3D Viewport, press **N**, open the **Curve UV** tab, and click **Generate UV**. This adds the **CurveUV** Geometry Nodes modifier. If you select several path curves, the button applies the setup to all of them.
3. In **Parameters**, choose the cross-section under **Profile Curve** and assign your material under **Set Material**.
4. Set **Tile Length** directly or click **Auto**. Auto uses the profile perimeter and the aspect ratio of the first usable Image Texture in the material, then adjusts the length to fit a whole number of repeats along the path.
5. Use **Path Resolution** and **Profile Resolution** to adjust the mesh density. Use **Seam Rotate** and **Seam Offset** to place the UV seam.

The same controls are available under **Object Properties → Curve UV Generator**.
