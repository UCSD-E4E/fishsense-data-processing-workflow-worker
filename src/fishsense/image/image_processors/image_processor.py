"""Base class for image processing"""

from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np


class ImageProcessor(ABC):
    """Base class for image processing"""

    @abstractmethod
    def process(self, file: Path) -> np.ndarray:
        """Takes in an image file and processes it for use.

        Args:
            file (Path): The file path to the image file.

        Returns:
            np.ndarray: The processed image.
        """
        raise NotImplementedError
