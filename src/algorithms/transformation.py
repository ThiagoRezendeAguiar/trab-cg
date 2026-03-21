import math
from typing import Dict

import numpy as np

from model.primitives import Point, Primitive, PrimitiveType

def translation(tx: int, ty: int):
    return np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ])

def scaling(sx: float, sy: float):
    return np.array([
        [sx, 0.0, 0.0],
        [0.0, sy, 0.0],
        [0.0, 0.0, 1.0]
    ])

def rotation(angle_degrees: float):
    rad = math.radians(angle_degrees)
    c, s = math.cos(rad), math.sin(rad)
    return np.array([
        [c, -s, 0.0],
        [s, c, 0.0],
        [0.0, 0.0, 1.0]
    ])

def reflection(axis: str):
    sx, sy = 1.0, 1.0
    if axis in ["X", "XY"]: sy = -1.0
    if axis in ["Y", "XY"]: sx = -1.0
    return scaling(sx, sy)

def apply_transformations(prim: Primitive, transforms: Dict[str, any]):
    cx = sum(pt.x for pt in prim.p) / len(prim.p)
    cy = sum(pt.y for pt in prim.p) / len(prim.p)

    M = np.eye(3)

    if 'translate' in transforms:
        dx, dy = transforms['translate']
        M = M @ translation(dx, dy)

    is_relative = any(k in transforms for k in ['rotate', 'scale', 'reflect'])
    
    if is_relative:
        M = M @ translation(cx, cy)

        if 'reflect' in transforms:
            M = M @ reflection(transforms['reflect'])
        if 'scale' in transforms:
            sx, sy = transforms['scale']
            M = M @ scaling(sx, sy)
        if 'rotate' in transforms:
            M = M @ rotation(transforms['rotate'])

        M = M @ translation(-cx, -cy)

    new_points = []
    for pt in prim.p:
        vec = np.array([pt.x, pt.y, 1.0])
        res = M @ vec
        new_points.append(Point(int(round(res[0])), int(round(res[1]))))

    prim.p = new_points

    if prim.type == PrimitiveType.CIRCLE and 'scale' in transforms:
        sx, sy = transforms['scale']
        prim.radius = int(prim.radius * (sx + sy) / 2.0)