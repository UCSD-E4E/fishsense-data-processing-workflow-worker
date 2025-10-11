from copy import copy
from typing import Tuple

import numpy as np
import torch

from fishsense.calibration.lens_calibration import LensCalibration
from fishsense.image.pdf import Pdf
from fishsense.library.homography.image_matcher import ImageMatcher
from fishsense.library.homography.utils import numpy_image_to_torch
from fishsense.plane_detector.plane_detector import PlaneDetector


class SlateDetector(PlaneDetector):
    def __init__(
        self,
        image: np.ndarray[np.uint8],
        pdf: Pdf,
        lens_calibration: LensCalibration,
        device: str,
        try_multiple_slate_rotations: bool = False,
    ) -> None:
        super().__init__(image, lens_calibration)

        self.__pdf = pdf
        self.__ran_template_matches = False
        self.__template_matches = None
        self.__image_matches = None
        self.__device = device
        self.__try_multiple_slate_rotations = try_multiple_slate_rotations

    @property
    def pdf(self) -> Pdf:
        return self.__pdf

    def _get_template_matches(self) -> Tuple[torch.Tensor, torch.Tensor]:
        if not self.__ran_template_matches:
            if self.__try_multiple_slate_rotations:
                rotated_pdf = copy(self.__pdf)
                rotated_pdf.rotate(180)
                pdfs = [self.__pdf, rotated_pdf]
            else:
                pdfs = [self.__pdf]

            max_num_keypoints = 0
            for pdf in pdfs:
                tensor_template = numpy_image_to_torch(pdf.image)

                for scale in range(1, 20):
                    scale = float(scale) / 10.0

                    image_matcher = ImageMatcher(
                        tensor_template,
                        self.__device,
                        com_license=False,
                        processing_conf={
                            "preprocess": {
                                "gamma": 2.0,
                                "sharpness": None,
                                "scale": scale,
                            },
                            "matcher": {"filter_threshold": 0.5},
                        },
                    )

                    template_matches, image_matches = image_matcher(
                        numpy_image_to_torch(self.image)
                    )

                    num_keypoints, _ = template_matches.shape
                    if num_keypoints > max_num_keypoints:
                        max_num_keypoints = num_keypoints
                        self.__pdf = pdf

                        self.__template_matches = template_matches
                        self.__image_matches = image_matches

            self.__ran_template_matches = True

        return self.__template_matches, self.__image_matches

    def _get_points_image_space(self):
        _, image_matches = self._get_template_matches()

        return image_matches.cpu().numpy()

    def _get_points_body_space(self):
        template_matches, _ = self._get_template_matches()

        num_points, _ = template_matches.shape
        objp = np.zeros((num_points, 3), np.float32)
        objp[:, :2] = self.__pdf.get_physical_measurements(
            template_matches.cpu().numpy()
        )

        return objp

    def is_valid(self):
        template_matches, _ = self._get_template_matches()

        if template_matches is None:
            return False

        num_matches, _ = template_matches.shape

        return num_matches > 10
