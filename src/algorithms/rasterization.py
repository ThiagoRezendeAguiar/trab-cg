def dda(x0: int, y0:int , x1: int, y1: int):
    dx = x1 - x0
    dy = y1 - y0

    steps = max(abs(dx), abs(dy))

    if steps == 0:
        return [(round(x0), round(y0))]

    xinc = dx/steps
    yinc = dy/steps

    x = float(x0)
    y = float(y0)

    points = []

    for i in range(steps):
        points.append((round(x), round(y)))
        x = x + xinc
        y = y + yinc

    return points

def line_bresenham(x0: int, y0:int , x1: int, y1: int):
    points = []
    dx = x1 - x0
    dy = y1 - y0

    if dx >= 0:
        xincr = 1
    else:
        xincr = -1
        dx = -dx

    if dy >= 0:
        yincr = 1
    else:
        yincr = -1
        dy = -dy

    x, y = x0, y0
    points.append((x, y))

    if dx > dy:
        p = 2 * dy - dx
        c1 = 2 * dy
        c2 = 2 * (dy - dx)
        
        for i in range(0, dx):
            x += xincr
            if p < 0:
                p += c1
            else:
                y += yincr
                p += c2
            points.append((x, y))
    else:
        p = 2 * dx - dy
        c1 = 2 * dx
        c2 = 2 * (dx - dy)
        for i in range(0, dy):
            y += yincr
            if p < 0:
                p += c1
            else:
                x += xincr
                p += c2
            points.append((x, y))

    return points
        
def circle_bresenham(xc: int, yc: int, r: int):
    points = []
    p = 3 - 2 * r
    x = 0
    y = r

    def add_symmetric_points(xc, yc, x, y):
        points.append((xc + x, yc + y))
        points.append((xc - x, yc + y))
        points.append((xc + x, yc - y))
        points.append((xc - x, yc - y))
        points.append((xc + y, yc + x))
        points.append((xc - y, yc + x))
        points.append((xc + y, yc - x))
        points.append((xc - y, yc - x))

    add_symmetric_points(xc, yc, x, y)

    while x < y:
        if p < 0:
            p += 4 * x + 6
        else:
            p += 4 * (x - y) + 10
            y -= 1
        x += 1
        add_symmetric_points(xc, yc, x, y)

    return points