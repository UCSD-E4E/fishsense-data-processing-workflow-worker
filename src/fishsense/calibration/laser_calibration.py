from pathlib import Path
from typing import Iterator, Self

import numpy as np

from fishsense.library.array_read_write import (
    read_laser_calibration,
    write_laser_calibration,
)
from fishsense.library.laser_parallax import (
    atanasov_calibration_method,
    gauss_newton_estimate_state,
)


class LaserCalibration:
    def __init__(
        self,
        laser_axis: np.ndarray | None = None,
        laser_position: np.ndarray | None = None,
    ) -> None:
        self._laser_axis = laser_axis
        self._laser_position = laser_position

        either_not_none = laser_axis is not None or laser_position is not None
        both_not_none = laser_axis is not None and laser_position is not None

        if either_not_none and not both_not_none:
            raise ValueError(
                "Either laser_axis or laser_position are none.  Please either set both to be none or set both values."
            )

    @property
    def laser_axis(self) -> np.ndarray:
        return self._laser_axis

    @property
    def laser_position(self) -> np.ndarray:
        return self._laser_position

    def load(self, calibration_path: Path):
        self._laser_position, self._laser_axis = read_laser_calibration(
            calibration_path.absolute().as_posix()
        )

    def save(self, calibration_path: Path):
        if self.laser_position is None or self.laser_axis is None:
            raise ValueError(
                "laser_position or laser_axis are None.  Please call load or calibrate and try again."
            )

        write_laser_calibration(
            calibration_path.absolute().as_posix(),
            self.laser_axis,
            self.laser_position,
        )

    def plane_calibrate(
        self,
        laser_points_3d: Iterator[np.ndarray],
    ) -> None:
        laser_params = atanasov_calibration_method(laser_points_3d)
        self._laser_axis = laser_params[:3]

        self._laser_position = np.zeros(3, dtype=float)
        self._laser_position[:2] = laser_params[-2:]
