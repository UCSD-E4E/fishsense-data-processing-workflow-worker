"""Dynaconf settings module."""

import logging
import logging.handlers
import os
import time
from importlib.metadata import version
from pathlib import Path

import platformdirs
import validators
from dynaconf import Dynaconf, Validator

IS_DOCKER = os.environ.get("E4EFS_DOCKER", False)
platform_dirs = platformdirs.PlatformDirs("e4efs_api_workflow_worker")


def get_log_path() -> Path:
    """Get log path

    Returns:
        Path: Path to log directory
    """
    if IS_DOCKER:
        return Path("/e4efs/logs")
    log_path = platform_dirs.user_log_path
    log_path.mkdir(parents=True, exist_ok=True)
    return log_path


def get_config_path() -> Path:
    """Get config path

    Returns:
        Path: Path to config directory
    """
    if IS_DOCKER:
        return Path("/e4efs/config")
    config_path = Path(".")
    return config_path


validators = [
    Validator("temporal.host", required=True, cast=str, condition=validators.hostname),
    Validator("temporal.port", required=True, cast=str, default=7233),
    Validator("label_studio.host", required=True, condition=validators.hostname),
    Validator("label_studio.api_key", required=True, cast=str),
    Validator("label_studio.laser_project_ids", required=True, cast=list),
    Validator("label_studio.head_tail_project_ids", required=True, cast=list),
    Validator("postgres.host", required=True, cast=str, condition=validators.hostname),
    Validator("postgres.port", required=True, cast=int, default=5432),
    Validator("postgres.username", required=True, cast=str),
    Validator("postgres.password", required=True, cast=str),
]

settings = Dynaconf(
    envvar_prefix="E4EFS",
    environments=False,
    settings_files=[
        (get_config_path() / "settings.toml").as_posix(),
        (get_config_path() / ".secrets.toml").as_posix(),
    ],
    merge_enabled=True,
    validators=validators,
)

PG_CONNECTION_STRING = (
    f"postgresql+asyncpg://{settings.postgres.username}:{settings.postgres.password}"
    + f"@{settings.postgres.host}:{settings.postgres.port}/{settings.postgres.database}"
)


def configure_log_handler(handler: logging.Handler):
    """Configures the log handler with standard formatting

    Args:
        handler (logging.Handler): Handler to configure
    """
    handler.setLevel(logging.DEBUG)
    msg_fmt = "%(asctime)s.%(msecs)03dZ - %(name)s - %(levelname)s - %(message)s"
    root_formatter = logging.Formatter(msg_fmt, datefmt="%Y-%m-%dT%H:%M:%S")
    handler.setFormatter(root_formatter)


def configure_logging():
    """Configures logging"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    log_dest = get_log_path().joinpath("e4efs_api_workflow_worker.log")
    print(f'Logging to "{log_dest.as_posix()}"')

    log_file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_dest, when="midnight", backupCount=5
    )
    configure_log_handler(log_file_handler)
    root_logger.addHandler(log_file_handler)

    console_handler = logging.StreamHandler()
    configure_log_handler(console_handler)
    root_logger.addHandler(console_handler)
    logging.Formatter.converter = time.gmtime

    logging.info("Log path: %s", get_log_path())
    logging.info("Config path: %s", get_config_path())
    logging.info(
        "Executing fishsense_api_workflow_worker:%s",
        version("fishsense_api_workflow_worker"),
    )


# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
