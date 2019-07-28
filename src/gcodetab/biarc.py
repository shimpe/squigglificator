import numpy as np

from gcodetab.arc import Arc
from gcodetab.line import Line


class Biarc(object):
    """
    class to represent a biarc, i.e. two circular arcs that are smootly connected
    """
    def __init__(self, p1, t1, p2, t2, t):
        """

        :param p1: start point
        :param t1: tangent vector in p1
        :param p2: end point
        :param t2: tangent vector in p2
        :param t: transition point
        """
        self.p1 = p1
        self.t1 = t1
        self.p2 = p2
        self.t2 = t2
        self.t = t
        the_sum = 0
        the_sum += (self.t[0][0] - self.p1[0][0]) * (self.t[1][0] + self.p1[1][0])
        the_sum += (self.p2[0][0] - self.t[0][0]) * (self.p2[1][0] + self.t[1][0])
        the_sum += (self.p1[0][0] - self.p2[0][0]) * (self.p1[1][0] + self.p2[1][0])
        cw = the_sum < 0
        # Calculate perpendicular lines to the tangent at P1 and P2
        tl1 = Line.create_perpendicular_at(self.p1, self.p1 + self.t1)
        tl2 = Line.create_perpendicular_at(self.p2, self.p2 + self.t2)
        # Calculate the perpendicular bisector of P1T and P2T
        p1_t2 = (self.p1 + self.t) / 2
        pb_p1_t = Line.create_perpendicular_at(p1_t2, self.t)
        p2_t2 = (self.p2 + self.t) / 2
        pb_p2_t = Line.create_perpendicular_at(p2_t2, self.t)
        # The origo of the circles are at the intersection points
        c1 = tl1.intersection(pb_p1_t)
        c2 = tl2.intersection(pb_p2_t)
        # Calculate the radii
        r1 = np.linalg.norm(c1 - self.p1)
        r2 = np.linalg.norm(c2 - self.p2)
        # Calculate start and sweep angles
        start_vector1 = self.p1 - c1
        end_vector1 = self.t - c1
        start_angle1 = np.arctan2(start_vector1[1][0], start_vector1[0][0])
        sweep_angle1 = np.arctan2(end_vector1[1][0], end_vector1[0][0]) - start_angle1
        start_vector2 = self.t - c2
        end_vector2 = self.p2 - c2
        start_angle2 = np.arctan2(start_vector2[1][0], start_vector2[0][0])
        sweep_angle2 = np.arctan2(end_vector2[1][0], end_vector2[0][0]) - start_angle2
        # Adjust angles according to the orientation of the curve
        if cw and sweep_angle1 < 0:
            sweep_angle1 = 2 * np.pi + sweep_angle1
        if not cw and sweep_angle1 > 0:
            sweep_angle1 = sweep_angle1 - 2 * np.pi
        if cw and sweep_angle2 < 0:
            sweep_angle2 = 2 * np.pi + sweep_angle2
        if not cw and sweep_angle2 > 0:
            sweep_angle2 = sweep_angle2 - 2 * np.pi
        self.a1 = Arc(c1, r1, start_angle1, sweep_angle1, self.p1, self.t)
        self.a2 = Arc(c2, r2, start_angle2, sweep_angle2, self.t, self.p2)

    def point_at(self, t):
        """
        evaluate x,y on biarc at t
        :param t: 0 <= t <= 1
        :return: 2x1 np.array containing x,y
        """
        s = self.a1.length() / (self.a1.length() + self.a2.length())
        if t <= s:
            return self.a1.point_at(t / s)
        else:
            return self.a2.point_at((t - s) / (1 - s))

    def length(self):
        """
        total length of biarc
        :return: float
        """
        return self.a1.length() + self.a2.length()
