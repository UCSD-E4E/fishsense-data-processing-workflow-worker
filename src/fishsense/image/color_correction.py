import numpy as np
from skimage.restoration import denoise_tv_chambolle, estimate_sigma

from fishsense.depth_map.depth_map import DepthMap
from fishsense.library.seathru import run_pipeline


class Args:
    def __init__(self, f, l, p, min_depth, max_depth, spread_data_fraction):
        self.f = f
        self.l = l
        self.p = p
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.spread_data_fraction = spread_data_fraction

    def __iter__(self):
        return self.__dict__.__iter__()


class ColorCorrection:
    def __init__(
        self,
        f=2.0,
        l=0.5,
        p=0.01,
        min_depth=0.0,
        max_depth: float = None,
        spread_data_fraction=0.05,
    ):
        self.__f = f
        self.__l = l
        self.__p = p
        self.__min_depth = min_depth
        self.__max_depth = max_depth
        self.__spread_data_fraction = spread_data_fraction

    def __img2double(self, img: np.ndarray, max_value: float) -> np.ndarray:
        img_double = img.astype(np.float64)

        return img_double / max_value

    def __double2img(
        self, double: np.ndarray, max_value: float, dtype: np.dtype
    ) -> np.ndarray:
        return (double * max_value).astype(dtype)

    def correct_color(self, img: np.ndarray, depth_map: DepthMap) -> np.ndarray:
        max_value = float(img.max())

        args = Args(
            self.__f,
            self.__l,
            self.__p,
            self.__min_depth,
            self.__max_depth or depth_map.depth_map.max(),
            self.__spread_data_fraction,
        )
        recovered = run_pipeline(
            self.__img2double(img, max_value), depth_map.depth_map, args
        )
        sigma_est = (
            estimate_sigma(recovered, channel_axis=2, average_sigmas=True) / 10.0
        )
        recovered = denoise_tv_chambolle(recovered, sigma_est, channel_axis=2)

        return self.__double2img(recovered, max_value, img.dtype)
