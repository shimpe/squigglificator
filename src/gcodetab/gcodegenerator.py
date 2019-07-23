import datetime
import os


class GCodeGenerator(object):
    def __init__(self, pageheight, xscale, yscale, xoffset, yoffset, home_at_begin, pen_up_cmd, pen_down_cmd, drawing_speed, pen_down_speed):
        self.ph = pageheight
        self.xscale = xscale
        self.yscale = yscale
        self.xo = xoffset
        self.yo = yoffset
        self.home_at_begin = home_at_begin
        self.pen_up_cmd = pen_up_cmd.strip()
        self.pen_down_cmd = pen_down_cmd.strip()
        self.drawing_speed = drawing_speed
        self.pen_down_speed = pen_down_speed
        self.state = "up"
        self.code = ""
        self.add_drawing_speed = True
        self.add_header()

    def corr_y(self, y):
        return self.yscale*(self.ph - (y + self.yo))

    def corr_x(self, x):
        return self.xscale*(x + self.xo)

    def corr_radius(self, r):
        return self.xscale*r

    def add_header(self):
        self.code += """%
( File created using Squigglificator )
( https://github.com/shimpe/squigglificator )
( File created:  {0} )

G21 (All units in mm)
""".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        if self.home_at_begin:
            self.pen_up()
            self.code += "G28 X0 Y0 (Home machine)" + os.linesep
        else:
            self.pen_up()

    def footer(self):
        self.code += "%" + os.linesep

    def pen_up(self):
        self.state = "up"
        self.code += "G00 " + self.pen_up_cmd + " (pen up)" + os.linesep

    def pen_down(self):
        self.state = "down"
        self.code += "G01 " + self.pen_down_cmd + " F{0:.2f}".format(self.pen_down_speed) + " (pen down)" + os.linesep
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

    def circle(self, ellipseitem, clockwise=True):
        rect = ellipseitem.rect()
        center = rect.center()
        xradius = rect.width() / 2.0
        yradius = rect.height() / 2.0
        fast = False
        if self.state == "up":
            fast = True
        if xradius != yradius:
            print("Sorry!! Ellipses are future work.")
        else:
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
