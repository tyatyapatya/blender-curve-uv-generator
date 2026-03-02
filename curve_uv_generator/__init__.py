bl_info = {
    "name": "Curve UV Generator",
    "author": "scryi",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Curve UV",
    "description": "Apply a bundled Geometry Nodes UV setup to selected path curves.",
    "category": "Object",
}

from .registration import register, unregister
