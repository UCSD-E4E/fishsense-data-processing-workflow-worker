import numpy as np

from fishsense.calibration.laser_calibration import LaserCalibration
from fishsense.calibration.lens_calibration import LensCalibration
from fishsense.depth_map.depth_map import DepthMap
from fishsense.library.laser_parallax import compute_world_point


class LaserDepthMap(DepthMap):
    def __init__(
        self,
        laser_image_position: np.ndarray,
        lens_calibration: LensCalibration,
        laser_calibration: LaserCalibration,
    ) -> None:
        super().__init__()

        self._laser_image_position = laser_image_position
        self._lens_calibration = lens_calibration
        self._laser_calibration = laser_calibration

    @property
    def depth_map(self) -> np.ndarray:
        return np.array(
            [
                [
                    compute_world_point(
                        self._laser_calibration.laser_position,
                        self._laser_calibration.laser_axis,
                        self._lens_calibration.inverted_camera_matrix,
                        self._laser_image_position,
                    )[2]
                ]
            ]
        )
