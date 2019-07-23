import numpy as np


class Arc(object):
    def __init__(self, c, r, start_angle, sweep_angle, p1, p2):
        self.c = c
        self.r = r
        self.start_angle = start_angle
        self.sweep_angle = sweep_angle
        self.p1 = p1
        self.p2 = p2

    def is_clockwise(self):
        return self.sweep_angle > 0

    def point_at(self, t):
        x = self.c[0][0] + self.r * np.cos(self.start_angle + t * self.sweep_angle)
        y = self.c[1][0] + self.r * np.sin(self.start_angle + t * self.sweep_angle)
        return np.array([[x, ], [y, ]])

    def length(self):
        return self.r * np.abs(self.sweep_angle)
