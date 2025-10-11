from pathlib import Path
from typing import Self

import cv2
import numpy as np
import pymupdf

from fishsense.library.constants import INCH_TO_M


class Pdf:
    DPI = 300

    def __init__(self, file_name: Path) -> None:
        with pymupdf.open(file_name.absolute().as_posix()) as doc:
            page: pymupdf.Page = doc.load_page(0)
            pixmap: pymupdf.Pixmap = page.get_pixmap(dpi=Pdf.DPI)
            bytes = np.frombuffer(pixmap.samples, dtype=np.uint8)

            image = bytes.reshape(pixmap.height, pixmap.width, pixmap.n)
            image = cv2.UMat(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

            _, image = cv2.threshold(image, 125, 255, cv2.THRESH_BINARY)

            self.__image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR).get()

    @property
    def image(self) -> np.ndarray:
        return self.__image

    @property
    def width(self) -> int:
        _, width, _ = self.__image.shape

        return width

    @property
    def height(self) -> int:
        height, _, _ = self.__image.shape

        return height

    @property
    def channels(self) -> int:
        _, _, channels = self.__image.shape

        return channels

    def __copy__(self) -> Self:
        pdf = Pdf.__new__(Pdf)
        pdf.__image = self.__image.copy()

        return pdf

    def get_physical_measurements(self, points: np.ndarray) -> np.ndarray:
        return (points / float(Pdf.DPI)) * INCH_TO_M

    def rotate(self, angle: float) -> None:
        rotation_matrix = cv2.getRotationMatrix2D(
            (self.width / 2, self.height / 2), angle, 1
        )
        self.__image = cv2.warpAffine(
            self.__image, rotation_matrix, (self.width, self.height)
        )
