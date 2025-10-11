from abc import ABC, abstractmethod

import numpy as np

from fishsense.calibration.lens_calibration import LensCalibration
from fishsense.library.laser_parallax import compute_world_point_from_depth


class DepthMap(ABC):
    def __init__(self) -> None:
        super().__init__()

    @property
    @abstractmethod
    def depth_map(self) -> np.ndarray:
        raise NotImplementedError

    def _get_depth_coordinate(
        self,
        image_coordinate: np.ndarray,
        image_width: int | float,
        image_height: int | float,
    ) -> np.ndarray:
        depth_shape = np.array(self.depth_map.shape, dtype=float)
        image_shape = np.array([image_height, image_width], dtype=float)

        return image_coordinate / (image_shape * depth_shape)

    def get_camera_space_point(
        self,
        image_coordinate: np.ndarray,
        image_width: int | float,
        image_height: int | float,
        lens_calibration: LensCalibration,
    ) -> np.ndarray:
        depth_coordinate = np.floor(
            self._get_depth_coordinate(image_coordinate, image_width, image_height)
        ).astype(int)

        depth = self.depth_map[depth_coordinate[0], depth_coordinate[1]]

        return compute_world_point_from_depth(
            image_coordinate, depth, lens_calibration.inverted_camera_matrix
        )
