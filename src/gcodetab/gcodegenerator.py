import datetime
import os

import numpy as np

from gcodetab.bezierapproximator import BezierApproximator
from gcodetab.beziercurve import BezierCurve
from gcodetab.biarc import Biarc
from gcodetab.gcodestatistics import GcodeStatistics
from gcodetab.line import Line

from PyQt5.QtWidgets import QGraphicsPathItem, QGraphicsEllipseItem

FORCE_PRINT = True

class GCodeGenerator(object):
    def __init__(self, pageheight,
                 xscale, yscale,
                 xoffset, yoffset,
                 home_at_begin, home_at_end,
                 pen_up_cmd, pen_down_cmd,
                 drawing_speed, pen_down_speed,
                 sampling_step, tolerance):
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
        self.pen_state = "up"
        self.code = ""
        self.add_drawing_speed = True
        self.sampling_step = sampling_step
        self.tolerance = tolerance
        self.add_header()

    def process_item(self, item):
        if item.isVisible():
            if item.__class__ == QGraphicsEllipseItem:
                self.ellipse(item)
            elif item.__class__ == QGraphicsPathItem:
                self.path(item)
            else:
                print("Unknown QGraphicsItem type?! Please extend GCodeGenerator.process_item for class {0}".format(item.__class__))

    def add_comment(self, comment, force_print=False):
        if force_print:
            print(comment)
        self.code += "({0}){1}".format(comment, os.linesep)

    def add_statistics(self):
        self.code = self.statistics.summarize() + self.code

    def corr_y(self, y):
        # yoffset calculation already took yscale into account; don't apply twice
        value = (self.ph - (self.yscale * y + self.yo))
        if value < 0:
            self.add_comment("GCODE GENERATION WARNING! Negative y value generated?!", FORCE_PRINT)
        return value

    def corr_x(self, x):
        # xoffset calculation already took yscale into account; don't apply twice
        value = self.xscale * x + self.xo
        if value < 0:
            self.add_comment("GCODE GENERATION WARNING! Negative x value generated?!", FORCE_PRINT)
        return value

    def corr_radius(self, r):
        return self.xscale * r

    def add_header(self):
        self.code += """
( File created using Squigglificator )
( https://github.com/shimpe/squigglificator )
( File created:  {0} )

G21 (All units in mm)
G01 {1} F{2} (start from known state: pen up)
""".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), self.pen_up_cmd, self.pen_down_speed)

        if self.home_at_begin:
            self.pen_up()
            self.move_to_nocorrection(0, 0, "Go fast to 0,0 position")
            self.code += "G28 X0 Y0 (Home machine)" + os.linesep
            self.statistics.home += 1
        else:
            self.pen_up()

    def footer(self):
        self.pen_up()
        self.move_to_nocorrection(0, 0, "Go fast to 0,0 position")
        if self.home_at_end:
            self.code += "G28 X0 Y0 (Home machine)" + os.linesep
            self.statistics.home += 1
        self.code += "%" + os.linesep

    def pen_up(self):
        if self.pen_state != "up":
            self.pen_state = "up"
            self.code += "G00 " + self.pen_up_cmd + " (pen up)" + os.linesep
            self.statistics.penup += 1

    def pen_down(self):
        if self.pen_state != "down":
            self.pen_state = "down"
            self.code += "G01 " + self.pen_down_cmd + " F{0:.3f}".format(
                self.pen_down_speed) + " (pen down)" + os.linesep
            self.statistics.pendown += 1
            self.add_drawing_speed = True

    def move_to_nocorrection(self, x, y, comment=""):
        fast = False
        if self.pen_state == "up":
            fast = True
        if self.add_drawing_speed:
            self.code += "G0{0} X{1:.3f} Y{2:.3f} F{3} {4}{5}".format(
                "0" if fast else "1",
                x,
                y,
                self.pen_down_speed if fast else self.drawing_speed,
                "(" + comment + ")" if comment else "",
                os.linesep)
            self.add_drawing_speed = False
        else:
            self.code += "G0{0} X{1:.3f} Y{2:.3f} {3}{4}".format("0" if fast else "1",
                                                                 x,
                                                                 y,
                                                                 "(" + comment + ")" if comment else "",
                                                                 os.linesep)

        if fast:
            self.statistics.movetofast += 1
        else:
            self.statistics.movetoslow += 1


    def move_to(self, x, y, comment=""):
        fast = False
        if self.pen_state == "up":
            fast = True
        if self.add_drawing_speed:
            self.code += "G0{0} X{1:.3f} Y{2:.3f} F{3} {4}{5}".format(
                "0" if fast else "1",
                self.corr_x(x),
                self.corr_y(y),
                self.pen_down_speed if fast else self.drawing_speed,
                "(" + comment + ")" if comment else "",
                os.linesep)
            self.add_drawing_speed = False
        else:
            self.code += "G0{0} X{1:.3f} Y{2:.3f} {3}{4}".format("0" if fast else "1",
                                                                 self.corr_x(x),
                                                                 self.corr_y(y),
                                                                 "(" + comment + ")" if comment else "",
                                                                 os.linesep)

        if fast:
            self.statistics.movetofast += 1
        else:
            self.statistics.movetoslow += 1

    def ellipse(self, ellipseitem, clockwise=True):
        rect = ellipseitem.rect()
        center = rect.center()
        xradius = rect.width() / 2.0
        yradius = rect.height() / 2.0
        fast = False
        if self.pen_state == "up":
            fast = True
        if xradius != yradius:
            print("Sorry!! Ellipses are future work. Converting into circles...")
            xradius = min(xradius, yradius)
            yradius = xradius

        self.pen_up()
        self.move_to(center.x() + xradius, center.y(), "goto first point on circle")
        self.pen_down()
        if self.add_drawing_speed:
            self.code += "G0{0} X{1:.3f} Y{2:.3f} I{3:.3f} J0 F{4} {5}{6}".format(
                "2" if clockwise else "3",
                self.corr_x(center.x() + xradius),
                self.corr_y(center.y()),
                self.corr_radius(-xradius),
                self.pen_down_speed if fast else self.drawing_speed,
                "(circle w/ radius {0:.3f})".format(self.corr_radius(xradius)),
                os.linesep)
        else:
            self.code += "G0{0} X{1:.3f} Y{2:.3f} I{3:.3f} J0 {4}{5}".format(
                "2" if clockwise else "3",
                self.corr_x(center.x() + xradius),
                self.corr_y(center.y()),
                self.corr_radius(-xradius),
                "(circle w/ radius {0:.3f})".format(
                    self.corr_radius(xradius)),
                os.linesep)
        self.statistics.circles += 1

    def path(self, pathitem):
        path = pathitem.path()
        if path.isEmpty():
            return
        prev_position = (0, 0)
        accumulated_data_points = []
        for idx in range(path.elementCount()):
            element = path.elementAt(idx)

            # at start of new path, update previous position to first element of new path
            if idx == 0:
                prev_position = element.x, element.y
                self.pen_up()
                self.move_to(prev_position[0], prev_position[1])

            if (element.isMoveTo() or element.isLineTo() or element.isCurveTo()) and accumulated_data_points:
                prev_position = self.gen_curve(prev_position, accumulated_data_points)
                accumulated_data_points = []

            if element.isMoveTo() and idx != (path.elementCount() - 1):
                # last element of a path is a moveto? ignore it as the next path will start with a move to as well
                self.pen_up()
                x = element.x
                y = element.y
                prev_position = (x, y)
                self.move_to(x, y, "move to {0},{1}".format(x, y))
            elif element.isLineTo():
                x = element.x
                y = element.y
                prev_position = (x, y)
                self.pen_down()
                self.move_to(x, y, "Subpath: line to {0},{1}".format(x, y))
                self.statistics.subpaths += 1
            elif element.isCurveTo():
                accumulated_data_points = [(element.x, element.y)]
            else:
                accumulated_data_points.append((element.x, element.y))

        if accumulated_data_points:
            # generate last curve
            self.gen_curve(prev_position, accumulated_data_points)
            prev_position = accumulated_data_points[-1]

        self.statistics.paths += 1

    def gen_arc(self, arc, comment):
        self.add_comment(comment)
        center = arc.c
        cx = self.corr_x(center[0][0])
        cy = self.corr_y(center[1][0])
        beginp = arc.point_at(0)
        bx = self.corr_x(beginp[0][0])
        by = self.corr_y(beginp[1][0])
        endp = arc.point_at(1)
        ex = self.corr_x(endp[0][0])
        ey = self.corr_y(endp[1][0])
        radius = arc.r
        clockwise = arc.is_clockwise()
        fast = self.pen_state == "up"
        self.pen_down()
        if self.add_drawing_speed:
            self.code += "G0{0} X{1:.3f} Y{2:.3f} I{3:.3f} J{4:.3f} F{5} {6}{7}".format(
                "2" if clockwise else "3",
                ex,
                ey,
                cx - bx,
                cy - by,
                self.pen_down_speed if fast else self.drawing_speed,
                "(arc w/ radius {0:.3f} from {1:.3f},{2:.3f} to {3:.3f},{4:.3f} around center {5:.3f},{6:.3f})".format(
                    self.corr_radius(radius), bx, by, ex, ey, cx, cy),
                os.linesep)
            self.add_drawing_speed = False
        else:
            self.code += "G0{0} X{1:.3f} Y{2:.3f} I{3:.3f} J{4:.3f} {5}{6}".format(
                "2" if clockwise else "3",
                ex,
                ey,
                cx - bx,
                cy - by,
                "(arc w/ radius {0:.3f} from {1:.3f},{2:.3f} to {3:.3f},{4:.3f} around center {5:.3f},{6:.3f})".format(
                    self.corr_radius(radius), bx, by, ex, ey, cx, cy),
                os.linesep)
        self.statistics.subpaths += 1

    def gen_curve(self, prev_position, accumulated_data_points):
        if len(accumulated_data_points) != 3 and len(accumulated_data_points) != 2:
            print(
                "Error! Skipping unsupported curve type with {0} control points.".format(len(accumulated_data_points)))
        else:
            c = None
            if len(accumulated_data_points) == 3:
                p1 = np.array([[prev_position[0], ], [prev_position[1], ]])
                c1 = np.array([[accumulated_data_points[0][0], ], [accumulated_data_points[0][1], ]])
                c2 = np.array([[accumulated_data_points[1][0], ], [accumulated_data_points[1][1], ]])
                p2 = np.array([[accumulated_data_points[2][0], ], [accumulated_data_points[2][1], ]])
                c = BezierCurve().from_cubic_bezier(p1, c1, c2, p2)
            elif len(accumulated_data_points) == 2:
                p1 = np.array([[prev_position[0], ], [prev_position[1], ]])
                c = np.array([[accumulated_data_points[0][0], ], [accumulated_data_points[0][1], ]])
                p2 = np.array([[accumulated_data_points[1][0], ], [accumulated_data_points[1][1], ]])
                c = BezierCurve().from_quadratic_bezier(p1, c, p2)
                p1 = c.p1
                c1 = c.c1
                c2 = c.c2
                p2 = c.p2
            else:
                print("Unknown curve type ignored. Keeping fingers crossed...")

            b = BezierApproximator()
            biarcs = b.approx_cubic_bezier(c, self.sampling_step, self.tolerance)
            self.add_comment("bezier curve approximated in {0} biarcs".format(len(biarcs)))
            for biarc in biarcs:
                if biarc.__class__ == Line:
                    # self.pen_down()
                    assert (biarc.origp2 is not None)
                    newx = biarc.origp2[0][0]
                    newy = biarc.origp2[1][0]
                    self.pen_down()
                    self.move_to(newx, newy, "Subpath line segment")
                    prev_position = (newx, newy)
                    self.statistics.subpaths += 1
                elif biarc.__class__ == Biarc:
                    self.pen_down()
                    self.gen_arc(biarc.a1, "Subpath arc1 of biarc")
                    endpos = biarc.a1.point_at(1)
                    prev_position = (endpos[0][0], endpos[1][0])
                    self.gen_arc(biarc.a2, "Subpath arc2 of biarc")
                    endpos = biarc.a2.point_at(1)
                    prev_position = (endpos[0][0], endpos[1][0])

        return prev_position
