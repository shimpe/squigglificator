import numpy as np


class Line(object):
    """
    class to represent a line
    (and it's abused a bit to also represent a line segment :( )
    """
    def __init__(self):
        self.p = None
        self.m = None
        self.origp1 = None
        self.origp2 = None

    def from_points(self, p1, p2):
        """
        initialize data members from two points
        the two points are remembered as a poor man's line segment definition
        :param p1: start point
        :param p2: end point
        :return:
        """

        newline = self.from_point_slope(p1, self.slope(p1, p2))
        newline.origp1 = p1 # origp1 and origp2 are kept because Line is also abused to represent a line segment
        newline.origp2 = p2
        return newline

    def from_point_slope(self, p, m):
        """
        initialize data members from a point and slope: origp2 is set to None since it's not known.
        this method cannot be used to represent a line segment, only a complete line
        :param p: point
        :param m: slope
        :return:
        """
        self.origp1 = p
        self.origp2 = None
        self.p = p
        self.m = m
        return self

    def intersection(self, line):
        """
        calculate intersection of this line with another line
        :param line: the other line
        :return:
        """
        if np.isnan(self.m):
            return self.vertical_intersection(line)
        elif np.isnan(line.m):
            return self.vertical_intersection(self)
        else:
            x = (self.m * self.p[0][0] - line.m * line.p[0][0] - self.p[1][0] + line.p[1][0]) / (self.m - line.m)
            y = self.m * x - self.m * self.p[0][0] + self.p[1][0]
            return np.array([[x, ], [y, ]])

    def vertical_intersection(self, line):
        """
        helper method to calculate intersection with vertical line
        :param line: a vertical line
        :return:
        """
        x = self.p[0][0]
        y = line.m * (x - line.p[0][0]) + line.p[1][0]
        return np.array([[x, ], [y, ]])

    @staticmethod
    def create_perpendicular_at(p, p1):
        """
        create new line perpendicular to line defined by points p, p1
        :param p:
        :param p1:
        :return:
        """
        m = Line.slope(p, p1)
        if m == 0:
            return Line().from_point_slope(p, np.nan)
        elif np.isnan(m):
            return Line().from_point_slope(p, 0)
        else:
            return Line().from_point_slope(p, -1 / m)

    @staticmethod
    def slope(p1, p2):
        """
        calculate slope from two points on line
        :param p1:
        :param p2:
        :return:
        """
        if p2[0][0] == p1[0][0]:
            return np.nan
        else:
            return (p2[1][0] - p1[1][0]) / (p2[0][0] - p1[0][0])
