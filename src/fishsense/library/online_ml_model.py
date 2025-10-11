import fcntl
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

from requests import get

from fishsense.library.paths import CACHE_DIRECTORY


class OnlineMLModel(ABC):
    def __init__(self) -> None:
        super().__init__()

        self.__lock_fd: Dict[str, int] = {}

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    def _model_cache_path(self) -> Path:
        return CACHE_DIRECTORY / "models"

    @property
    def __download_lock_name(self) -> str:
        return f".{self.name}.download.lock"

    @property
    @abstractmethod
    def _model_path(self) -> Path:
        raise NotImplementedError

    @property
    @abstractmethod
    def _model_url(self) -> str:
        raise NotImplementedError

    def __download_file(self, url: str, path: Path) -> Path:
        if not path.exists():
            self.__acquire_download_lock()

            path.parent.mkdir(parents=True, exist_ok=True)

            response = get(url)
            with path.open("wb") as file:
                file.write(response.content)

            self.__release_download_lock()

        return path.absolute()

    def __get_lock_path(self, name: str) -> Path:
        return CACHE_DIRECTORY / name

    def __acquire_download_lock(self):
        return self.__acquire_lock(self.__download_lock_name)

    def __acquire_lock(self, name: str):
        self.__lock_fd[name] = os.open(
            self.__get_lock_path(name), os.O_CREAT | os.O_WRONLY
        )
        fcntl.flock(self.__lock_fd[name], fcntl.LOCK_EX)

    def __release_download_lock(self):
        return self.__release_lock(self.__download_lock_name)

    def __release_lock(self, name: str):
        fcntl.flock(self.__lock_fd[name], fcntl.LOCK_UN)
        os.close(self.__lock_fd[name])

        del self.__lock_fd[name]

    def download_model(self) -> Path:
        return self.__download_file(
            self._model_url,
            self._model_path,
        )
