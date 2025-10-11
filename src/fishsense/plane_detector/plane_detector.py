from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Tuple

import cv2
import numpy as np

from fishsense.calibration.lens_calibration import LensCalibration
from fishsense.library.laser_parallax import image_coordinate_to_projected_point


class PlaneDetector(ABC):
    def __init__(self, image: np.ndarray, lens_calibration: LensCalibration) -> None:
        self._image = image
        self._height, self._width, _ = image.shape
        self._points_image_space: np.ndarray | None = None
        self._points_body_space: np.ndarray | None = None
        self._lens_calibration = lens_calibration

    @property
    def image(self) -> np.ndarray:
        return self._image

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def lens_calibration(self) -> LensCalibration:
        return self._lens_calibration

    @abstractmethod
    def _get_points_image_space(self) -> np.ndarray | None:
        raise NotImplementedError

    @abstractmethod
    def _get_points_body_space(self) -> np.ndarray | None:
        raise NotImplementedError

    @property
    def points_image_space(self) -> np.ndarray | None:
        if self._points_image_space is None:
            self._points_image_space = self._get_points_image_space()

        return self._points_image_space

    @property
    def points_body_space(self) -> np.ndarray | None:
        if self._points_body_space is None:
            self._points_body_space = self._get_points_body_space()

        return self._points_body_space

    def _get_body_to_camera_space_transform(
        self,
    ) -> Tuple[np.ndarray | None, np.ndarray | None]:
        empty_dist_coeffs = np.zeros((5,))
        ret, rotation_vectors, translation = cv2.solvePnP(
            self.points_body_space,
            self.points_image_space,
            self.lens_calibration.camera_matrix,
            empty_dist_coeffs,
        )

        if not ret:
            return None, None

        rotation, _ = cv2.Rodrigues(rotation_vectors)
        return rotation, translation

    def _get_points_camera_space(self) -> np.ndarray | None:
        rotation, translation = self._get_body_to_camera_space_transform()
        body_points = self.points_body_space

        if rotation is None or translation is None or body_points is None:
            return None

        board_plane_points = (rotation @ body_points.T + translation).T
        return board_plane_points

    def _get_normal_vector_camera_space(self) -> np.ndarray | None:
        camera_points = self._get_points_camera_space()

        if camera_points is None:
            return camera_points

        return np.cross(
            camera_points[1, :] - camera_points[0, :],
            camera_points[2, :] - camera_points[0, :],
        )

    def project_point_onto_plane_camera_space(
        self, point_image_space: np.ndarray
    ) -> np.ndarray | None:
        ray = (
            image_coordinate_to_projected_point(
                point_image_space, self.lens_calibration.inverted_camera_matrix
            )
            * -1
        )

        camera_points = self._get_points_camera_space()
        normal_vector = self._get_normal_vector_camera_space()

        if camera_points is None or normal_vector is None:
            return None

        # find scale factor such that the laser ray intersects with the plane
        scale_factor = (normal_vector.T @ camera_points[0, :]) / (normal_vector.T @ ray)
        return ray * scale_factor

    def is_valid(self) -> bool:
        return (
            self.points_image_space is not None and self.points_body_space is not None
        )
