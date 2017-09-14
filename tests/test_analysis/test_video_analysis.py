import numpy as np

from pyper.analysis.video_analysis import points_to_angle


def test_points_to_angle():
    assert points_to_angle(np.array([-1, -1]), np.array([0, 0]), np.array([1, 1])) == 0
    assert points_to_angle(np.array([-1, -1]), np.array([0, 0]), np.array([0, 1])) == -45
    assert points_to_angle(np.array([-1, -1]), np.array([0, 0]), np.array([1, 0])) == 45
    assert points_to_angle(np.array([0, 1]), np.array([0, 0]), np.array([1, -1])) == -45
    assert points_to_angle(np.array([0, 1]), np.array([0, 0]), np.array([-1, -1])) == 45

