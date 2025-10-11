"""An image processor that takes in a RAW file and produces an image."""

import math
from pathlib import Path

import cv2
import numpy as np
import rawpy

# These modules do exist. Pylint can't find them for some reason.
# pylint: disable=no-name-in-module
from skimage.exposure import adjust_gamma, equalize_adapthist
from skimage.util import img_as_float, img_as_ubyte

from fishsense.image.image_processors.image_processor import ImageProcessor


class RawProcessor(ImageProcessor):
    """An image processor that takes in a RAW file and produces an image."""

    def __init__(self) -> None:
        super().__init__()

    def process(self, file: Path) -> np.ndarray:
        with file.open("rb") as f:
            with rawpy.imread(f) as raw:
                img = img_as_float(
                    raw.postprocess(
                        gamma=(1, 1),
                        no_auto_bright=True,
                        use_camera_wb=True,
                        output_bps=16,
                        user_flip=0,
                    )
                )

                hsv = cv2.cvtColor(img_as_ubyte(img), cv2.COLOR_BGR2HSV)
                _, _, val = cv2.split(hsv)

                mid = 20
                mean = np.mean(val)
                meanLog = math.log(mean)
                midLog = math.log(mid * 255)
                gamma = midLog / meanLog
                gamma = 1 / gamma

                img = adjust_gamma(img, gamma=gamma)

                img = equalize_adapthist(img)

                return img[:, :, ::-1]
