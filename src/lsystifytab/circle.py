from utils import dist


class Circle(object):
    """
    class to represent a circle object
    """
    def __init__(self, x, y, r, ):
        self.x = x
        self.y = y
        self.r = r
        self.growspeed = 1
        self.growing = True

    def cangrow(self):
        """
        check if circle is allowed to be enlarged
        :return: boolean
        """
        return self.growing

    def grow(self):
        """
        enlarge the circle (typically used to iterate towards some circle packing)
        :return: returns old radius
        """
        oldval = self.r
        if self.cangrow():
            self.r = self.r + self.growspeed
        return oldval

    def edges(self, width, height):
        """
        check if circle goes outside bitmap edges
        :param width: bitmap width
        :param height: bitmap height
        :return: boolean
        """
        return self.x + self.r >= width or self.x - self.r <= 0 or self.y + self.r >= height or self.y - self.r <= 0

    def overlaps(self, othercircle):
        """
        checks if circle overlaps with other circle
        :param othercircle:
        :return: boolean
        """
        return dist(self.x, self.y, othercircle.x, othercircle.y) - 2 <= (self.r + othercircle.r)
