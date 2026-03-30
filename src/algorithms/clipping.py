from typing import Optional, Tuple
from model.primitives import Point

OUTCODE = {'LEFT': 1, 'RIGHT': 2, 'BOTTOM': 4, 'TOP': 8}

def compute_outcode(x: float, y: float, x_min: float, y_min: float, x_max: float, y_max: float) -> int:
    outcode = 0
    if x < x_min: outcode |= OUTCODE['LEFT']
    elif x > x_max: outcode |= OUTCODE['RIGHT']
    if y < y_min: outcode |= OUTCODE['BOTTOM']
    elif y > y_max: outcode |= OUTCODE['TOP']
    return outcode

def cohen_sutherland(x1: float, y1: float, x2: float, y2: float,
                     x_min: float, y_min: float, x_max: float, y_max: float) -> Optional[Tuple[Point, Point]]:
    outcode1 = compute_outcode(x1, y1, x_min, y_min, x_max, y_max)
    outcode2 = compute_outcode(x2, y2, x_min, y_min, x_max, y_max)
    
    accept = False
    while True:
        if outcode1 == 0 and outcode2 == 0:
            accept = True
            break
        elif (outcode1 & outcode2) != 0:
            break
        else:
            outcode_out = outcode1 if outcode1 != 0 else outcode2
            x, y = 0.0, 0.0
            
            if outcode_out & OUTCODE['TOP']:
                x = x1 + (x2 - x1) * (y_max - y1) / (y2 - y1) if y2 != y1 else x1
                y = y_max
            elif outcode_out & OUTCODE['BOTTOM']:
                x = x1 + (x2 - x1) * (y_min - y1) / (y2 - y1) if y2 != y1 else x1
                y = y_min
            elif outcode_out & OUTCODE['RIGHT']:
                y = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1) if x2 != x1 else y1
                x = x_max
            elif outcode_out & OUTCODE['LEFT']:
                y = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1) if x2 != x1 else y1
                x = x_min
            
            if outcode_out == outcode1:
                x1, y1 = x, y
                outcode1 = compute_outcode(x1, y1, x_min, y_min, x_max, y_max)
            else:
                x2, y2 = x, y
                outcode2 = compute_outcode(x2, y2, x_min, y_min, x_max, y_max)

    if accept:
        return Point(int(round(x1)), int(round(y1))), Point(int(round(x2)), int(round(y2)))
    return None

def liang_barsky(x1: float, y1: float, x2: float, y2: float,
                 x_min: float, y_min: float, x_max: float, y_max: float) -> Optional[Tuple[Point, Point]]:
    dx = x2 - x1
    dy = y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]
    u1, u2 = 0.0, 1.0
    
    for i in range(4):
        if p[i] == 0:
            if q[i] < 0: return None
        else:
            t = q[i] / p[i]
            if p[i] < 0:
                u1 = max(u1, t)
            else:
                u2 = min(u2, t)
                
    if u1 > u2:
        return None
        
    nx1 = x1 + u1 * dx
    ny1 = y1 + u1 * dy
    nx2 = x1 + u2 * dx
    ny2 = y1 + u2 * dy
    
    return Point(int(round(nx1)), int(round(ny1))), Point(int(round(nx2)), int(round(ny2)))