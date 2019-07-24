import numpy as np


class BezierCurve(object):
    def __init__(self, p1=None, c1=None, c2=None, p2=None):
        self.p1 = None
        self.c1 = None
        self.c2 = None
        self.p2 = None
        self.from_cubic_bezier(p1, c1, c2, p2)

    def from_cubic_bezier(self, p1, c1, c2, p2):
        self.p1 = p1
        self.c1 = c1
        self.c2 = c2
        self.p2 = p2
        return self

    def from_quadratic_bezier(self, p1, c, p2):
        self.p1 = p1
        self.p2 = p2
        self.c1 = p1 + 2 / 3 * (c - p1)
        self.c2 = p2 + 2 / 3 * (c - p2)
        return self

    def point_at(self, t):
        return np.power(1 - t, 3) * self.p1 + (3 * np.power(1 - t, 2) * t) * self.c1 + (
                3 * (1 - t) * np.power(t, 2)) * self.c2 + np.power(t, 3) * self.p2

    def split(self, t):
        p0 = self.p1 + t * (self.c1 - self.p1)
        p1 = self.c1 + t * (self.c2 - self.c1)
        p2 = self.c2 + t * (self.p2 - self.c2)
        p01 = p0 + t * (p1 - p0)
        p12 = p1 + t * (p2 - p1)
        dp = p01 + t * (p12 - p01)
        return BezierCurve(self.p1, p0, p01, dp), BezierCurve(dp, p12, p2, self.p2)

    def is_clockwise(self):
        the_sum = 0
        the_sum += (self.c1[0][0] - self.p1[0][0]) * (self.c1[1][0] + self.p1[1][0])
        the_sum += (self.c2[0][0] - self.c1[0][0]) * (self.c2[1][0] + self.c1[1][0])
        the_sum += (self.p2[0][0] - self.c2[0][0]) * (self.p2[1][0] + self.c2[1][0])
        the_sum += (self.p1[0][0] - self.p2[0][0]) * (self.p1[1][0] + self.p2[1][0])
        return the_sum < 0

    def inflexion_points(self):
        big_a = self.c1 - self.p1
        big_b = self.c2 - self.c1 - big_a
        big_c = self.p2 - self.c2 - big_a - 2 * big_b
        a = big_b[0][0] * big_c[1][0] - big_b[1][0] * big_c[0][0] + 0j
        b = big_a[0][0] * big_c[1][0] - big_a[1][0] * big_c[0][0] + 0j
        c = big_a[0][0] * big_b[1][0] - big_a[1][0] * big_b[0][0] + 0j

        if a == 0:
            # don't divide by zero
            return None, None

        if (b * b - 4 * a * c) < 0:
            # we're only interested in real inflexion points
            return None, None

        t1 = (-b + np.sqrt(b * b - 4 * a * c)) / (2 * a)
        t2 = (-b - np.sqrt(b * b - 4 * a * c)) / (2 * a)

        return t1, t2
