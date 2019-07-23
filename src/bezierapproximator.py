import numpy as np
from line import Line
from biarc import Biarc


class BezierApproximator(object):
    def __init__(self):
        pass

    @staticmethod
    def is_real_inflexion_point(pt):
        return pt.imag == 0 and 0 < pt.real < 1

    def approx_cubic_bezier(self, bezier, sampling_step, tolerance):
        # Place to store the result
        biarcs = []
        # The bezier curves to approximate
        curves = [bezier]
        # First, calculate the inflexion points and split the bezier at them (if any)
        to_split = curves.pop()
        inflex = to_split.inflexion_points()
        i1 = self.is_real_inflexion_point(inflex[0])
        i2 = self.is_real_inflexion_point(inflex[1])
        if i1 and (not i2):
            splitted = to_split.split(inflex[0].real)
            curves.append(splitted[1])
            curves.append(splitted[0])
        elif (not i1) and i2:
            splited = to_split.split(inflex[1].real)
            curves.append(splited[1])
            curves.append(splited[0])
        elif i1 and i2:
            t1 = inflex[0].real
            t2 = inflex[1].real
            # I'm not sure if I need, but it does not hurt to order them
            if t1 > t2:
                t1, t2 = t2, t1
            # Make the first split and save the first new curve.The second one has to be splitted again
            # at the recalculated t2(it is on a new curve)
            splited1 = to_split.split(t1)
            t2 = (1 - t1) * t2
            to_split = splited1[1]
            splited2 = to_split.split(t2)
            curves.append(splited2[1])
            curves.append(splited2[0])
            curves.append(splited1[0])
        else:
            curves.append(to_split)

        # Second, approximate the curves until we run out of them

        while curves:
            bezier = curves.pop()

            # Calculate the transition point for the BiArc
            # V: Intersection point of tangent lines
            t1 = Line().from_points(bezier.p1, bezier.c1)
            t2 = Line().from_points(bezier.p2, bezier.c2)
            v = t1.intersection(t2)
            # G: incenter point of the triangle(P1, V, P2)
            # http: // www.mathopenref.com / coordincenter.html
            d_p2_v = np.linalg.norm(bezier.p2 - v)
            d_p1_v = np.linalg.norm(bezier.p1 - v)
            d_p1_p2 = np.linalg.norm(bezier.p1 - bezier.p2)
            g = (d_p2_v * bezier.p1 + d_p1_v * bezier.p2 + d_p1_p2 * v) / (d_p2_v + d_p1_v + d_p1_p2)

            # Calculate the BiArc
            biarc = Biarc(bezier.p1, (bezier.p1 - bezier.c1), bezier.p2, (bezier.p2 - bezier.c2), g)
            # Calculate the maximum error
            max_distance = 0
            max_distance_at = 0
            nr_points_to_check = int(biarc.length() / sampling_step)
            parameter_step = 1 / nr_points_to_check

            for i in range(nr_points_to_check):
                t = parameter_step * i
                u1 = biarc.point_at(t)
                u2 = bezier.point_at(t)
                distance = np.linalg.norm(u1 - u2)
                if distance > max_distance:
                    max_distance = distance
                    max_distance_at = t

            # Check if the two curves are close enough
            if max_distance > tolerance:
                # If not, split the bezier curve the point where the distance is the maximum
                # and try again with the two halves
                bs = bezier.split(max_distance_at)
                curves.append(bs[1])
                curves.append(bs[0])
            else:
                # Otherwise we are done with the current bezier
                biarcs.append(biarc)
        return biarcs

if __name__=="__main__":
    from beziercurve import BezierCurve
    b = BezierCurve(p1=np.array([[1.7, ], [2.2, ]]),
                    c1=np.array([[4.3, ], [-1.3, ]]),
                    c2=np.array([[-2.5, ], [3.3, ]]),
                    p2=np.array([[-1.8, ], [1.1, ]]))
    a = BezierApproximator()
    result = a.approx_cubic_bezier(b, 0.1, 0.1)
    print(result)
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
