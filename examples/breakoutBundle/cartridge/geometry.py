from __future__ import division

from . import vars
katasdk = vars.katasdk
pygame = katasdk.kengi.pygame

#    Geometry functions to find intersecting lines. 
#    These calculations use this formula for a straight line:-
#        y = mx + b where m is the gradient and b is the y value when x=0
#
#    See here for background http://www.mathopenref.com/coordintersection.html
#     
#    Throughout the code the variable p is a point tuple representing (x,y) 
#

# Calc the gradient 'm' of a line between p1 and p2
def calculate_gradient(p1, p2):
    # Ensure that the line is not vertical
    if p1[0] != p2[0]:
        m = (p1[1] - p2[1]) / (p1[0] - p2[0])
        return m
    else:
        return None


# Calc the point 'b' where line crosses the Y axis
def calculate_y_axis_intersect(p, m):
    return p[1] - (m * p[0])


# Calc the point where two infinitely long lines (p1 to p2 and p3 to p4) intersect.
# Handle parallel lines and vertical lines (the later has infinate 'm').
# Returns a point tuple of points like this ((x,y),...)  or None 
# In non parallel cases the tuple will contain just one point.
# For parallel lines that lay on top of one another the tuple will contain all four points of the two lines
def get_intersect_point(p1, p2, p3, p4):
    m1 = calculate_gradient(p1, p2)
    m2 = calculate_gradient(p3, p4)

    # See if the the lines are parallel
    if m1 != m2:
        # Not parallel

        # See if either line is vertical
        if m1 is not None and m2 is not None:
            # Neither line vertical            
            b1 = calculate_y_axis_intersect(p1, m1)
            b2 = calculate_y_axis_intersect(p3, m2)
            x = (b2 - b1) / (m1 - m2)
            y = (m1 * x) + b1
        else:
            # Line 1 is vertical so use line 2's values
            if m1 is None:
                b2 = calculate_y_axis_intersect(p3, m2)
                x = p1[0]
                y = (m2 * x) + b2
            # Line 2 is vertical so use line 1's values                
            elif m2 is None:
                b1 = calculate_y_axis_intersect(p1, m1)
                x = p3[0]
                y = (m1 * x) + b1
            else:
                assert False

        return (x, y),
    else:
        # Parallel lines with same 'b' value must be the same line so they intersect 
        # everywhere in this case we return the start and end points of both lines
        # the calculate_intersect_point function will sort out which of these points
        # lays on both line segments
        b1, b2 = None, None  # vertical lines have no b value
        if m1 is not None:
            b1 = calculate_y_axis_intersect(p1, m1)

        if m2 is not None:
            b2 = calculate_y_axis_intersect(p3, m2)

        # If these parallel lines lay on one another    
        if b1 == b2:
            return p1, p2, p3, p4
        else:
            return None


# For line segments (ie not infinitely long lines) the intersect point may not lay on both lines.
# If the point where two lines intersect is inside both line's bounding rectangles then the lines intersect.
# Returns intersect point if the line intersect or None if not
def calculate_intersect_point(p1, p2, p3, p4):
    p = get_intersect_point(p1, p2, p3, p4)

    if p is not None:
        width = p2[0] - p1[0]
        height = p2[1] - p1[1]
        r1 = pygame.Rect(p1, (width, height))
        r1.normalize()

        width = p4[0] - p3[0]
        height = p4[1] - p3[1]
        r2 = pygame.Rect(p3, (width, height))
        r2.normalize()

        # Ensure both rects have a width and height of at least 'tolerance' else the
        # collidepoint check of the Rect class will fail as it doesn't include the bottom
        # and right hand side 'pixels' of the rectangle
        tolerance = 1
        if r1.width < tolerance:
            r1.width = tolerance

        if r1.height < tolerance:
            r1.height = tolerance

        if r2.width < tolerance:
            r2.width = tolerance

        if r2.height < tolerance:
            r2.height = tolerance

        for point in p:
            try:
                res1 = r1.collidepoint(point)
                res2 = r2.collidepoint(point)
                if res1 and res2:
                    point = [int(pp) for pp in point]
                    return point
            except:
                # sometimes the value in a point are too large for PyGame's Rect class
                str = "point was invalid  ", point
                print(str)

        # This is the case where the infinitely long lines crossed but the line segments didn't
        return None

    else:
        return None


# Test script below...
if __name__ == "__main__":
    # Test cases:
    #   line 1 and 2 intersect, 1 and 3 don't but would if extended
    #   lines 2 and 3 are parallel
    #   line 5 is horizontal, line 4 is vertical and the line segments intersect

    # line 1
    p1 = (1, 5)
    p2 = (4, 7)

    # line 2
    p3 = (4, 5)
    p4 = (3, 7)

    # line 3
    p5 = (4, 1)
    p6 = (3, 3)

    # line 4
    p7 = (3, 1)
    p8 = (3, 10)

    # line 5
    p9 = (0, 6)
    p10 = (5, 6)

    assert None != calculate_intersect_point(p1, p2, p3, p4), "line 1 line 2 should intersect"
    assert None != calculate_intersect_point(p3, p4, p1, p2), "line 2 line 1 should intersect"
    assert None == calculate_intersect_point(p1, p2, p5, p6), "line 1 line 3 shouldn't intersect"
    assert None == calculate_intersect_point(p3, p4, p5, p6), "line 2 line 3 shouldn't intersect"
    assert None != calculate_intersect_point(p1, p2, p7, p8), "line 1 line 4 should intersect"
    assert None != calculate_intersect_point(p7, p8, p1, p2), "line 4 line 1 should intersect"
    assert None != calculate_intersect_point(p1, p2, p9, p10), "line 1 line 5 should intersect"
    assert None != calculate_intersect_point(p9, p10, p1, p2), "line 5 line 1 should intersect"
    assert None != calculate_intersect_point(p7, p8, p9, p10), "line 4 line 5 should intersect"
    assert None != calculate_intersect_point(p9, p10, p7, p8), "line 5 line 4 should intersect"

    print("\nSUCCESS! All asserts passed for doLinesIntersect")
