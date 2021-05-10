"""
This module allows converting between ObjectContour and Roi while
 preventing the circular dependency between object_contour and roi.
 TODO: see if a more elegant solution exists
"""
from pyper.contours.roi import roi_classes


def contour_to_roi(cnt, shape=None):
    """
    :param ObjectContour cnt:
    :param str shape: one of ('circle', 'ellipse', 'rectangle')
    :return:
    """
    if shape is None:
        shape = cnt.contour_type
    shape = shape.lower()
    cnt._fit()
    if shape in ('circle', 'ellipse', 'rectangle'):
        return roi_classes[shape](*cnt.fit)
    else:
        raise ValueError('Unsupported Roi type: "{}"'.format(shape))
