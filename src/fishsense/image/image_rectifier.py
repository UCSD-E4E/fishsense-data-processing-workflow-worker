from pathlib import Path

import cv2
import numpy as np

from fishsense.calibration.lens_calibration import LensCalibration


class ImageRectifier:
    def __init__(self, lens_calibration: LensCalibration):
        self._lens_calibration = lens_calibration

    def rectify(self, img: np.ndarray) -> np.ndarray:
        return cv2.undistort(
            cv2.UMat(img),
            self._lens_calibration.camera_matrix,
            self._lens_calibration.distortion_coefficients,
        ).get()


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    img = cv2.imread("./data/png/P7170081.png")

    image_rectifier = ImageRectifier(Path("./data/lens-calibration.pkg"))
    undist_img = image_rectifier.rectify(img)

    plt.imshow(undist_img)
    plt.show()
