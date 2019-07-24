class GcodeStatistics(object):
    def __init__(self):
        self.circles = 0
        self.paths=0
        self.subpaths=0
        self.penup=0
        self.pendown=0
        self.home=0
        self.movetofast=0
        self.movetoslow=0

    def summarize(self):
        return """%
(Overview of generated code)
(**************************)
(homings: {0})
(penups: {1})
(pendowns: {2})
(circles: {3})
(paths: {4}, subpaths {5})
(moveto fast: {6})
(moveto slow: {7})
""".format(self.home, self.penup, self.pendown, self.circles, self.paths, self.subpaths, self.movetofast,
                   self.movetoslow)