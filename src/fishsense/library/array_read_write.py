"""
Module for reading and writing numpy arrays
"""

import io
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


def write_numpy_array(array: np.ndarray, name: str, file: tarfile.TarFile):
    with io.BytesIO() as b:
        np.save(b, array)
        tarinfo = tarfile.TarInfo(name)
        tarinfo.size = len(b.getvalue())
        tarinfo.mtime = int(datetime.now().timestamp())
        b.seek(0)
        file.addfile(tarinfo, b)


def write_camera_calibration(
    file_path: str, calibration_matrix: np.ndarray, distortion_coefficients: np.ndarray
):
    metadata = {"calibrated_date": str(datetime.now(timezone.utc))}
    with tarfile.open(file_path, "x:gz") as f:
        with io.StringIO() as s:
            json.dump(metadata, s, indent=True)
            bytes = s.getvalue().encode("utf8")
            with io.BytesIO(bytes) as b:
                tarinfo = tarfile.TarInfo("metadata.json")
                tarinfo.size = len(bytes)
                tarinfo.mtime = int(datetime.now().timestamp())
                f.addfile(tarinfo, b)

        write_numpy_array(calibration_matrix, "_calibration_matrix.npy", f)
        write_numpy_array(distortion_coefficients, "_distortion_coefficients.npy", f)


def write_laser_calibration(
    file_path: str, laser_axis: np.ndarray, laser_pos: np.ndarray
):
    metadata = {"calibrated_date": str(datetime.now(timezone.utc))}
    with tarfile.open(file_path, "x:gz") as f:
        with io.StringIO() as s:
            json.dump(metadata, s, indent=True)
            bytes = s.getvalue().encode("utf8")
            with io.BytesIO(bytes) as b:
                tarinfo = tarfile.TarInfo("metadata.json")
                tarinfo.size = len(bytes)
                tarinfo.mtime = int(datetime.now().timestamp())
                f.addfile(tarinfo, b)

        write_numpy_array(laser_axis, "laser_axis.npy", f)
        write_numpy_array(laser_pos, "laser_pos.npy", f)


def _read_numpy_array(buffer: io.BufferedReader):
    with io.BytesIO(buffer.read()) as b:
        return np.load(b)


def read_numpy_array(file: tarfile.TarFile, name: str) -> np.ndarray:
    return _read_numpy_array(file.extractfile(name))


def read_camera_calibration(file_path: Path):
    with file_path.open("rb") as f:
        with tarfile.open(fileobj=f) as t:
            calibration_matrix = read_numpy_array(t, "_calibration_matrix.npy")
            distortion_coeffs = read_numpy_array(t, "_distortion_coefficients.npy")
    return calibration_matrix, distortion_coeffs


def read_laser_calibration(file_path: str):
    with tarfile.open(file_path, "r:gz") as f:
        laser_position = read_numpy_array(f, "laser_pos.npy")
        laser_orientation = read_numpy_array(f, "laser_axis.npy")
    return laser_position, laser_orientation
