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


def path_validator(path: str) -> bool:
    """Validator to check if a given path exists.

    Args:
        path (str): Path to validate

    Returns:
        bool: True if path exists, False otherwise
    """
    return Path(path).exists()


validators = [
    Validator(
        "general.max_workers",
        required=True,
        cast=int,
        default=4,
        condition=lambda x: x > 0,
    ),
    Validator("temporal.host", required=True, cast=str, condition=validators.hostname),
    Validator("temporal.port", required=True, cast=int, default=7233),
    Validator("temporal.tls", required=True, cast=bool, default=False),
    Validator("temporal.client_cert", cast=str, condition=path_validator),
    Validator("temporal.client_private_key", cast=str, condition=path_validator),
    Validator("temporal.domain", cast=str),
    Validator("temporal.server_root_ca_cert", cast=str, condition=path_validator),
]

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml", ".secrets.toml"],
    validators=validators,
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

    log_dest = get_log_path().joinpath("e4efs_data_processing_workflow_worker.log")
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
        "Executing fishsense-data-processing-workflow-worker:%s",
        version("fishsense-data-processing-workflow-worker"),
    )


# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load these files in the order.
