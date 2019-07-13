from math import sqrt


def frange(x, y, jump):
    while x < y:
        yield x
        x += jump


def distsq(x1, y1, x2, y2):
    return (x1 - x2) ** 2 + (y1 - y2) ** 2


def dist(x1, y1, x2, y2):
    return sqrt(distsq(x1, y1, x2, y2))
