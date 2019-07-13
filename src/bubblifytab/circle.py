from ..utils import dist


class Circle(object):
    def __init__(self, x, y, r, ):
        self.x = x
        self.y = y
        self.r = r
        self.growspeed = 1
        self.growing = True

    def cangrow(self):
        return self.growing

    def grow(self):
        oldval = self.r
        if self.cangrow():
            self.r = self.r + self.growspeed
        return oldval

    def edges(self, width, height):
        return self.x + self.r >= width or self.x - self.r <= 0 or self.y + self.r >= height or self.y - self.r <= 0

    def overlaps(self, othercircle):
        return dist(self.x, self.y, othercircle.x, othercircle.y) - 2 <= (self.r + othercircle.r)
