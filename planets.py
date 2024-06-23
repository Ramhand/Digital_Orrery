from api_requests import position_recall
import datetime as dt
import math


class Orrery():
    def __init__(self):
        global df, phase
        if 'df' not in globals():
            df, phase = position_recall()
        self.df = df

    def location_return(self):
        loc = {}
        for k in self.df.columns:
            rs = []
            for v in self.df.loc[3, k]:
                rs.append(dt.datetime.strptime(v, '%H:%M').time())
            if rs[0] < dt.datetime.now().time() < rs[1]:
                progress = self.dt_calculations(rs)
            else:
                progress = None
            loc[k] = progress
        return loc

    def dt_calculations(self, rs):
        rs1 = dt.datetime.combine(dt.date.min, rs[0])
        rs2 = dt.datetime.combine(dt.date.min, rs[1])
        span = rs2 - rs1
        span = span.seconds
        now = dt.datetime.combine(dt.date.min, dt.datetime.now().time())
        progress = now - rs1
        progress = (progress.seconds / span)
        return progress

    def center_rotate(self, point, origin, angle):
        px, py = point
        ox, oy = origin
        rad = math.radians(-angle)
        cos = math.cos(rad)
        sin = math.sin(rad)
        adj_x, adj_y = ox - px, py - oy
        new_point = [(adj_x * cos) - (adj_y * sin) + ox, (adj_x * sin) + (adj_y * cos) + oy]
        return new_point
