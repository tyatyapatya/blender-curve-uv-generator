from typing import Iterable, List

from bpy.types import Context, Object


def selected_curve_objects(context: Context) -> List[Object]:
    objects: Iterable[Object] = context.selected_objects or []
    return [obj for obj in objects if obj and obj.type == "CURVE"]


def active_curve_object(context: Context) -> Object | None:
    obj = context.active_object or context.object
    if obj and obj.type == "CURVE":
        return obj
    return None


def target_curve_objects(context: Context) -> List[Object]:
    curves = selected_curve_objects(context)
    if curves:
        return curves
    active = active_curve_object(context)
    if active is not None:
        return [active]
    return []
