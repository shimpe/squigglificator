# from collections import namedtuple
#
# import numpy as np
# from bezier.curve import Curve
#
# from utils import frange
#
#
# def circle_slope(t, axis='x'):
#     if axis == 'x':
#         return -1.0 / np.tan(t)
#     elif axis == 'y':
#         return -np.tan(t)
#
#
# def bezier_slope(eq, t, axis='x'):
#     p0x = eq.p0[0][0]
#     p0y = eq.p0[1][0]
#     p1x = eq.p1[0][0]
#     p1y = eq.p1[1][0]
#     p2x = eq.p2[0][0]
#     p2y = eq.p2[1][0]
#     p3x = eq.p3[0][0]
#     p3y = eq.p3[1][0]
#     if axis == 'x':
#         return (p1y - 3 * p1y * t * t + t * (p2y * (2 - 3 * t) + (-p0y + p3y) * t)) / (
#                 p1x - 3 * p1x * t * t + t * (p2x * (2 - 3 * t) + (-p0x + p3x) * t))
#     else:
#         return (p1x - 3 * p1x * t * t + t * (p2x * (2 - 3 * t) + (-p0x + p3x) * t)) / (
#                 p1y - 3 * p1y * t * t + t * (p2y * (2 - 3 * t) + (-p0y + p3y) * t))
#
#
# def circle_concavity(t, axis='x'):
#     sign = 0
#     if axis == 'x':
#         sinus = np.sin(t)
#         if sinus < 0:
#             sign = -1
#         elif sinus > 0:
#             sign = 1
#         return (-1) * sign
#     else:
#         cosinus = np.cos(t)
#         if cosinus < 0:
#             sign = -1
#         elif cosinus > 0:
#             sign = 1
#         return (-1) * sign
#     return 0
#
#
# def bezier_concavity(eq, t, axis='x'):
#     p0x = eq.p0[0][0]
#     p0y = eq.p0[1][0]
#     p1x = eq.p1[0][0]
#     p1y = eq.p1[1][0]
#     p2x = eq.p2[0][0]
#     p2y = eq.p2[1][0]
#     p3x = eq.p3[0][0]
#     p3y = eq.p3[1][0]
#     sign = 0
#     if axis == 'x':
#         secondderiv = ((2 * (-p1y * (-p0x * t + p3x * t + 3 * p2x * t * t - 3 * p2x * t + p2x) + t * t * (
#                 p0x * p2y - p3x * p2y + p3y * p2x - p0y * p2x) + p1x * (
#                                      3 * p2y * t * t - 3 * p2y * t + p2y + p3y * t - p0y * t)))) / (
#                               3 * (t * (t * (p3x - p0x) + p2x * (2 - 3 * t)) - 3 * p1x * t * t + p1x) * (
#                           -t * (t * (p0x - p3x) + p2x * (3 * t - 2)) - p1x * (3 * t * t - 1)) ** 2)
#         if secondderiv < 0:
#             return -1
#         elif secondderiv > 0:
#             return 1
#     else:
#         secondderiv = (2 * (p1y * (-p0x * t + p3x * t + 3 * p2x * t * t - 3 * p2x * t + p2x) + t * t * (
#                 -p0x * p2y + p2y * p3x - p3y * p2x + p0y * p2x) - p1x * (
#                                     3 * p2y * t * t - 3 * p2y * t + p2y + p3y * t - p0y * t))) / (
#                               3 * (-3 * p1y * t * t + p1y + t * (p2y * (2 - 3 * t) + (p3y - p0y) * t)) * (
#                               -p1y * (3 * t * t - 1) - t * (p2y * (3 * t - 2) + (p0y - p3y) * t)) ** 2)
#         if secondderiv < 0:
#             return -1
#         elif secondderiv > 0:
#             return 1
#     return 0
#
#
# Circle = namedtuple('Circle', 'x, y, r')
# ParametricEquation = namedtuple('ParametricEquation', 'cx, cy, t0, t1, radius, px, py, qx, qy')
# ParametricEquation.__str__ = lambda eq: "({0} + {1}*cos(t), {2} + {1}*sin(t)) {3} <= t <= {4}".format(eq.cx, eq.radius,
#                                                                                                       eq.cy,
#                                                                                                       min(eq.t0, eq.t1),
#                                                                                                       max(eq.t0, eq.t1))
# BiarcHelper = namedtuple('BiarcHelper', 'l0, chi0, l1, chi1, xstar, ystar, thetastar')
# CubicBezier = namedtuple("CubicBezier", 'p0, p1, p2, p3')
# CubicBezier.nodes = lambda eq: np.asfortranarray(
#     [[eq.p0[0][0], eq.p1[0][0], eq.p2[0][0], eq.p3[0][0]], [eq.p0[1][0], eq.p1[1][0], eq.p2[1][0], eq.p3[1][0]]])
# CubicBezier.slope = lambda eq, t, axis='x': bezier_slope(eq, t, axis)
#
# Biarc = namedtuple("Biarc", 'eq1, eq2')
# Error = namedtuple("Error", 'bt, t, bx, by, cx, cy, error, eq, dir')
#
#
# def sinc(x):
#     return np.sinc(x / np.pi)
#
#
# def cosc(x):
#     if np.abs(x) < 0.002:
#         return x ** 2 * (1 + x ** 2 / 12 * (1 - x ** 2 / 30))
#     return (1 - np.cos(x)) / x
#
#
# def solve2x2(A, b):
#     return np.linalg.pinv(A) * b
#
# def normalize_angle(angle):
#     while angle > np.pi:
#         angle = angle - 2 * np.pi
#     while angle < -np.pi:
#         angle = angle + 2 * np.pi
#     return angle
#
# def biarc_helper(x0, y0, th0, x1, y1, th1):
#     # transform to standard problem
#     dx, dy = x1 - x0, y1 - y0
#     d = np.hypot(dx, dy)
#     omega = np.arctan2(dy, dx)
#     theta0, theta1 = omega + normalize_angle(th0 - omega), omega + normalize_angle(th1 - omega)
#     dt = (th1 - th0) / 2
#     t = d * np.sinc(dt/2)/np.sinc(dt)
#     thetas = 2*omega - (theta0 + theta1)/2
#     dt0 = (thetas-theta0)/2
#     dt1 = (thetas-theta1)/2
#     l0 = t/(2*np.sinc(dt0))
#     l1 = t/(2*np.sinc(dt1))
#     kappa0 = 4 * np.sin(dt0) / t
#     kappa1 = -4 * np.sin(dt1) / t
#     xs = x0 + (t / 2) * np.cos((thetas + theta0) / 2)
#     ys = y0 + (t / 2) * np.sin((thetas + theta0) / 2)
#     return BiarcHelper(l0=l0, chi0=kappa0, l1=l1, chi1=kappa1, xstar=xs, ystar=ys, thetastar=thetas)
#
#
# def circles_from_p1p2r(p1, p2, r):
#     'Following explanation at http://mathforum.org/library/drmath/view/53027.html'
#     if r == 0.0:
#         raise ValueError('radius of zero')
#     (x1, y1), (x2, y2) = (p1[0][0], p1[1][0]), (p2[0][0], p2[1][0])
#     if np.array_equal(p1, p2):
#         raise ValueError('coincident points gives infinite number of Circles')
#     # delta x, delta y between points
#     dx, dy = x2 - x1, y2 - y1
#     # dist between points
#     q = np.hypot(dx, dy)
#     if q > 2.0 * r:
#         raise ValueError('separation of points > diameter')
#     # halfway point
#     x3, y3 = (x1 + x2) / 2, (y1 + y2) / 2
#     # distance along the mirror line
#     d = np.sqrt(r ** 2 - (q / 2) ** 2)
#     # One answer
#     c1 = Circle(x=x3 - d * dy / q,
#                 y=y3 + d * dx / q,
#                 r=abs(r))
#     # The other answer
#     c2 = Circle(x=x3 + d * dy / q,
#                 y=y3 - d * dx / q,
#                 r=abs(r))
#     return c1, c2
#
#
# def circle_parametric_equation_given_two_points(p, q, radius):
#     # px,py and qx, qy are just returned for informational purposes
#     # resulting parametric equation members translate to circle segment as follows:
#     # (cx + radius*cos(t), cy + radius*sin(t)) for t0 <= t <= t1
#     circles = circles_from_p1p2r(p, q, radius)
#     px, py = p[0][0], p[1][0]
#     qx, qy = q[0][0], q[1][0]
#     results = []
#     for c in circles:
#         t0 = 2 * np.arctan2((py - c.y), (px - c.x + radius))
#         t1 = 2 * np.arctan2((qy - c.y), (qx - c.x + radius))
#         results.append(ParametricEquation(cx=c.x, cy=c.y, t0=t0, t1=t1, radius=radius, px=px, py=py, qx=qx, qy=qy))
#         if (t0 < t1):
#             results.append(ParametricEquation(cx=c.x, cy=c.y, t0=t0+2*np.pi, t1=t1, radius=radius, px=px, py=py, qx=qx, qy=qy))
#         else:
#             results.append(ParametricEquation(cx=c.x, cy=c.y, t0=t0, t1=t1 + 2 * np.pi, radius=radius, px=px, py=py, qx=qx, qy=qy))
#     return results
#
#
# def vector_to_quadrant(v):
#     vx = v[0][0]
#     vy = v[1][0]
#     if vx > 0 and vy > 0:
#         return 1
#     elif vx > 0 and vy <= 0:
#         return 4
#     elif vx <= 0 and vy > 0:
#         return 2
#     elif vx <= 0 and vy <= 0:
#         return 3
#
#
# def differs_at_most_one_quadrant(q1, q2):
#     if (q1, q2) in ((1, 3), (3, 1), (2, 4), (4, 2)):
#         return False
#     return True
#
#
# def biarc_from_bezier(cubicbezier):
#     p0x = cubicbezier.p0[0][0]
#     p0y = cubicbezier.p0[1][0]
#     p1x = cubicbezier.p1[0][0]
#     p1y = cubicbezier.p1[1][0]
#     p2x = cubicbezier.p2[0][0]
#     p2y = cubicbezier.p2[1][0]
#     p3x = cubicbezier.p3[0][0]
#     p3y = cubicbezier.p3[1][0]
#     theta0 = np.arctan2(p1y - p0y, p1x - p0x)
#     # print("expected tangential angle in x0,y0 = {0} deg".format(np.rad2deg(np.unwrap([theta0])[0])))
#     theta1 = np.arctan2(p3y - p2y, p3x - p2x)
#     # print("expected tangential angle in x3,y3 = {0} deg".format(np.rad2deg(np.unwrap([theta1])[0])))
#     biarc = biarc_helper(p0x, p0y, theta0, p3x, p3y, theta1)
#
#     arc1p1 = np.array([[p0x, ], [p0y, ]])
#     arcstar = np.array([[biarc.xstar, ], [biarc.ystar, ]])
#     radius1 = np.abs(1 / biarc.chi0)
#     eq1 = circle_parametric_equation_given_two_points(arc1p1, arcstar, radius1)
#     bezier_conc = bezier_concavity(cubicbezier, 0, 'x')
#     besteq = None
#     for e in eq1:
#         circlex0 = e.cx + radius1 * np.cos(e.t0)
#         circley0 = e.cy + radius1 * np.sin(e.t0)
#         if circle_concavity(e.t0, 'x') == bezier_conc:
#             besteq = e
#             break
#
#     # print("({0} + {1}*cos(t), {2} + {1}*sin(t))".format(besteq.cx, radius1, besteq.cy))
#     # print("min t = {0}".format(min(besteq.t0, besteq.t1)))
#     # print("max t = {0}".format(max(besteq.t0, besteq.t1)))
#
#     arc2p2 = np.array([[p3x, ], [p3y, ]])
#     radius2 = np.abs(1 / biarc.chi1)
#     eq2 = circle_parametric_equation_given_two_points(arcstar, arc2p2, radius2)
#     bezier_conc2 = bezier_concavity(cubicbezier, 1, 'x')
#     besteq2 = None
#     for e in eq2:
#         circlex1 = e.cx + radius2 * np.cos(e.t1)
#         circley1 = e.cy + radius2 * np.sin(e.t1)
#         if circle_concavity(e.t1, 'x') == bezier_conc2:
#             besteq2 = e
#             break
#     # print("({0} + {1}*cos(t), {2} + {1}*sin(t))".format(besteq2.cx, radius2, besteq2.cy))
#     # print("min t = {0}".format(min(besteq2.t0, besteq2.t1)))
#     # print("max t = {0}".format(max(besteq2.t0, besteq2.t1)))
#     return Biarc(eq1=besteq, eq2=besteq2)
#
#
# def estimate_errors(cubicbezier, biarc, no_of_samples=20):
#     errors = []
#     for bt in frange(0, 1, 1 / no_of_samples):
#         bezier = (1 - bt) ** 3 * cubicbezier.p0 + 3 * bt * (1 - bt) ** 2 * cubicbezier.p1 + \
#                  3 * bt ** 2 * (1 - bt) * cubicbezier.p2 + bt ** 3 * cubicbezier.p3
#         bezier_x = bezier[0][0]
#         bezier_y = bezier[1][0]
#         for eqidx, eq in enumerate([biarc.eq1, biarc.eq2]):
#             horerror = None
#             vererror = None
#             # calculate horizontal error
#             circle_x = bezier_x
#             cos_t = (circle_x - eq.cx) / eq.radius
#             min_t = min(eq.t1, eq.t0)
#             max_t = max(eq.t1, eq.t0)
#             if -1 <= cos_t <= 1:
#                 t = np.arccos(cos_t)
#                 while t > max_t:
#                     t = t - np.pi
#                 while t < min_t:
#                     t = t + np.pi
#                 # print("t = {0}, t0 = {1}, t1 = {2}".format(t, min_t, max_t))
#                 if min_t <= t <= max_t:
#                     sin_t = np.sin(t)
#                     circle_y = eq.cy + eq.radius * sin_t
#                     error = np.linalg.norm(np.array([circle_x, circle_y]) - np.array([bezier_x, bezier_y]))
#                     horerror = Error(bt=bt, t=t, bx=bezier_x, by=bezier_y, cx=circle_x, cy=circle_y, error=error, eq=eq,
#                                      dir="ver")
#
#             # calculate vertical error
#             circle_y = bezier_y
#             sin_t = (circle_y - eq.cy) / eq.radius
#             if -1 <= sin_t <= 1:
#                 t = np.arcsin(sin_t)
#                 while t > max_t:
#                     t = t - np.pi
#                 while t < min_t:
#                     t = t + np.pi
#                 # print("t = {0}, t0 = {1}, t1 = {2}".format(t, min_t, max_t))
#                 if min_t <= t <= max_t:
#                     cos_t = np.cos(t)
#                     circle_x = eq.cx + eq.radius * cos_t
#                     error = np.linalg.norm(np.array([circle_x, circle_y]) - np.array([bezier_x, bezier_y]))
#                     vererror = Error(bt=bt, t=t, bx=bezier_x, by=bezier_y, cx=circle_x, cy=circle_y, error=error, eq=eq,
#                                      dir="hor")
#
#         if horerror and vererror:
#             if horerror.error < vererror.error:
#                 errors.append(horerror)
#             elif vererror.error >= horerror.error:
#                 errors.append(vererror)
#         elif horerror:
#             errors.append(horerror)
#         elif vererror:
#             errors.append(vererror)
#
#     errors.sort(key=lambda x: x.error, reverse=True)
#     return errors
#
#
# def bezier_approximator(list_of_bezier):
#     for b in list_of_bezier:
#         cb = CubicBezier(
#             p0=np.array([[b.nodes[0][0], ], [b.nodes[1][0]]]),
#             p1=np.array([[b.nodes[0][1], ], [b.nodes[1][1]]]),
#             p2=np.array([[b.nodes[0][2], ], [b.nodes[1][2]]]),
#             p3=np.array([[b.nodes[0][3], ], [b.nodes[1][3]]]))
#         biarc = biarc_from_bezier(cb)
#         all_errors = estimate_errors(cb, biarc)
#         if all_errors:
#             biggest_error = all_errors[0]
#             if biggest_error.error > 0.1:
#                 [subbez1, subbez2] = b.specialize(0, biggest_error.bt).nodes, b.specialize(biggest_error.bt, 1).nodes
#                 return bezier_approximator([Curve(nodes=subbez1, degree=3), Curve(nodes=subbez2, degree=3)])
#             else:
#                 return list_of_bezier
#         else:
#             return list_of_bezier
#
#
# def flatten(items):
#     """Yield items from any nested iterable; see REF."""
#     from collections.abc import Iterable
#     for x in items:
#         if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
#             yield from flatten(x)
#         else:
#             yield x
#
#
# if __name__ == "__main__":
#     b = CubicBezier(p0=np.array([[1.7, ], [2.2, ]]),
#                     p1=np.array([[4.3, ], [-1.3, ]]),
#                     p2=np.array([[-2.5, ], [3.3, ]]),
#                     p3=np.array([[-1.8, ], [1.1, ]]))
#     curves = (bezier_approximator([Curve(nodes=b.nodes(), degree=len(b.nodes()) - 1)]))
#     for b in flatten(curves):
#         cb = CubicBezier(
#             p0=np.array([[b.nodes[0][0], ], [b.nodes[1][0], ]]),
#             p1=np.array([[b.nodes[0][1], ], [b.nodes[1][1], ]]),
#             p2=np.array([[b.nodes[0][2], ], [b.nodes[1][2], ]]),
#             p3=np.array([[b.nodes[0][3], ], [b.nodes[1][3], ]]))
#         biarc = biarc_from_bezier(cb)
#         print(biarc.eq1)
#         print(biarc.eq2)
