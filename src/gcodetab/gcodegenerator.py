import datetime
import os
from gcodetab.gcodestatistics import GcodeStatistics

class GCodeGenerator(object):
    def __init__(self, pageheight, xscale, yscale, xoffset, yoffset, home_at_begin, home_at_end, pen_up_cmd, pen_down_cmd, drawing_speed, pen_down_speed):
        self.statistics = GcodeStatistics()
        self.ph = pageheight
        self.xscale = xscale
        self.yscale = yscale
        self.xo = xoffset
        self.yo = yoffset
        self.home_at_begin = home_at_begin
        self.home_at_end = home_at_end
        self.pen_up_cmd = pen_up_cmd.strip()
        self.pen_down_cmd = pen_down_cmd.strip()
        self.drawing_speed = drawing_speed
        self.pen_down_speed = pen_down_speed
        self.state = "up"
        self.code = ""
        self.add_drawing_speed = True
        self.add_header()

    def add_statistics(self):
        self.code = self.statistics.summarize() + self.code

    def corr_y(self, y):
        value = (self.ph - self.yscale*(y + self.yo))
        if value < 0:
            print("GCODE GENERATION WARNING! Negative y value generated?!")
        return value

    def corr_x(self, x):
        value = self.xscale*(x + self.xo)
        if value < 0:
            print("GCODE GENERATION WARNING! Negative x value generated?!")
        return value

    def corr_radius(self, r):
        return self.xscale*r

    def add_header(self):
        self.code += """
( File created using Squigglificator )
( https://github.com/shimpe/squigglificator )
( File created:  {0} )

G21 (All units in mm)
""".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if self.home_at_begin:
            self.pen_up()
            self.move_to(0, 0, "Go fast to 0,0 position")
            self.code += "G28 X0 Y0 (Home machine)" + os.linesep
            self.statistics.home += 1
        else:
            self.pen_up()

    def footer(self):
        self.pen_up()
        self.move_to(0, 0, "Go fast to 0,0 position")
        if self.home_at_end:
            self.code += "G28 X0 Y0 (Home machine)" + os.linesep
            self.statistics.home += 1
        self.code += "%" + os.linesep

    def pen_up(self):
        self.state = "up"
        self.code += "G00 " + self.pen_up_cmd + " (pen up)" + os.linesep
        self.statistics.penup += 1

    def pen_down(self):
        self.state = "down"
        self.code += "G01 " + self.pen_down_cmd + " F{0:.2f}".format(self.pen_down_speed) + " (pen down)" + os.linesep
        self.statistics.pendown += 1
        self.add_drawing_speed = True

    def move_to(self, x, y, comment=""):
        fast = False
        if self.state == "up":
            fast = True
        if self.add_drawing_speed:
            self.code += "G0{0} X{1:.2f} Y{2:.2f} F{3} {4}{5}".format("0" if fast else "1",
                                                                      self.corr_x(x),
                                                                      self.corr_y(y),
                                                                      self.pen_down_speed if fast else self.drawing_speed,
                                                                      "(" + comment + ")" if comment else "",
                                                                      os.linesep)
            self.add_drawing_speed = False
        else:
            self.code += "G0{0} X{1:.2f} Y{2:.2f} {3}{4}".format("0" if fast else "1",
                                                                 self.corr_x(x),
                                                                 self.corr_y(y),
                                                                 "(" + comment + ")" if comment else "",
                                                                 os.linesep)

        if fast:
            self.statistics.movetofast += 1
        else:
            self.statistics.movetoslow += 1

    def circle(self, ellipseitem, clockwise=True):
        rect = ellipseitem.rect()
        center = rect.center()
        xradius = rect.width() / 2.0
        yradius = rect.height() / 2.0
        fast = False
        if self.state == "up":
            fast = True
        if xradius != yradius:
            print("Sorry!! Ellipses are future work. Converting into circles...")
            xradius = min(xradius, yradius)
            yradius = xradius

        self.pen_up()
        self.move_to(center.x() + xradius, center.y(), "goto first point on circle")
        self.pen_down()
        if self.add_drawing_speed:
            self.code += "G0{0} X{1:.2f} Y{2:.2f} I{3:.2f} J0 F{4} {5}{6}".format("2" if clockwise else "3",
                                                                                self.corr_x(center.x() + xradius),
                                                                                self.corr_y(center.y()),
                                                                                self.corr_radius(-xradius),
                                                                                self.pen_down_speed if fast else self.drawing_speed,
                                                                                "(circle w/ radius {0:.2f})".format(
                                                                                    self.corr_radius(xradius)),
                                                                                os.linesep)
        else:
            self.code += "G0{0} X{1:.2f} Y{2:.2f} I{3:.2f} J0 {4}{5}".format("2" if clockwise else "3",
                                                                             self.corr_x(center.x() + xradius),
                                                                             self.corr_y(center.y()),
                                                                             self.corr_radius(-xradius),
                                                                             "(circle w/ radius {0:.2f})".format(
                                                                                 self.corr_radius(xradius)),
                                                                             os.linesep)
        self.statistics.circles += 1

    def path(self, pathitem):
        self.statistics.subpaths += 1
        self.statistics.paths += 1
