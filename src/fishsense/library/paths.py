import importlib
import importlib.metadata
from pathlib import Path

from platformdirs import user_cache_dir


def _get_cache_directory() -> Path:
    directory = Path(
        user_cache_dir(
            appname="fishsense",
            appauthor="Engineers for Exploration",
            version='0.0.0',
        )
    )

    if not directory.exists():
        directory.mkdir(exist_ok=True, parents=True)

    return directory


CACHE_DIRECTORY = _get_cache_directory()
