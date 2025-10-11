from pathlib import Path
from typing import Iterator

import cv2
import numpy as np

from fishsense.library.array_read_write import (
    read_camera_calibration,
    write_camera_calibration,
)


class LensCalibration:
    def __init__(
        self,
        camera_matrix: np.ndarray | None = None,
        distortion_coefficients: np.ndarray | None = None,
    ) -> None:
        self._camera_matrix = camera_matrix
        self._distortion_coefficients = distortion_coefficients

        either_not_none = (
            camera_matrix is not None or distortion_coefficients is not None
        )
        both_not_none = (
            camera_matrix is not None and distortion_coefficients is not None
        )

        if either_not_none and not both_not_none:
            raise ValueError(
                "Either camera_matrix or distortion_coefficients are none.  Please either set both to be none or set both values."
            )

    @property
    def camera_matrix(self) -> np.ndarray | None:
        return self._camera_matrix

    @property
    def inverted_camera_matrix(self) -> np.ndarray | None:
        if self.camera_matrix is None:
            return None

        return np.linalg.inv(self.camera_matrix)

    @property
    def distortion_coefficients(self) -> np.ndarray | None:
        return self._distortion_coefficients

    def load(self, calibration_path: Path):
        self._camera_matrix, self._distortion_coefficients = read_camera_calibration(
            calibration_path.absolute()
        )

    def save(self, calibration_path: Path):
        if self.camera_matrix is None or self.distortion_coefficients is None:
            raise ValueError(
                "camera_matrix or distortion_coefficients are None.  Please call load or calibrate and try again."
            )

        write_camera_calibration(
            calibration_path.absolute().as_posix(),
            self._camera_matrix,
            self._distortion_coefficients,
        )

    def plane_calibrate(
        self,
        body_space_points: Iterator[np.ndarray],
        image_space_points: Iterator[np.ndarray],
        image_width: int,
        image_height: int,
        max_error=None,
    ) -> float:
        error, self._camera_matrix, self._distortion_coefficients, _, _ = (
            cv2.calibrateCamera(
                body_space_points,
                image_space_points,
                (image_width, image_height),
                None,
                None,
            )
        )

        if max_error is not None and error > max_error:
            raise ValueError(
                f"While calibrating, an error of {error} was above the maximum allowed error of {max_error}."
            )

        return error
