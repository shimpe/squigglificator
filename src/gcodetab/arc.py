import numpy as np


class Arc(object):
    """
    class to model a circular arc
    """
    def __init__(self, c, r, start_angle, sweep_angle, p1, p2):
        self.c = c
        self.r = r
        self.start_angle = start_angle
        self.sweep_angle = sweep_angle
        self.p1 = p1
        self.p2 = p2

    def is_clockwise(self):
        """
        checks if arc is clockwise
        :return:
        """
        return self.sweep_angle > 0

    def point_at(self, t):
        """
        get values for x, y at parameter value t
        :param t: between 0-1
        :return: 2x1 np.array containing x,y
        """
        x = self.c[0][0] + self.r * np.cos(self.start_angle + t * self.sweep_angle)
        y = self.c[1][0] + self.r * np.sin(self.start_angle + t * self.sweep_angle)
        return np.array([[x, ], [y, ]])

    def length(self):
        """
        arc length
        :return: float
        """
        return self.r * np.abs(self.sweep_angle)
