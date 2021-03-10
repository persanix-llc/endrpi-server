#  Copyright (c) 2020 - 2021 Persanix LLC. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import sys
from typing import Dict

from loguru import logger
from uvicorn.config import LOGGING_CONFIG


class LoguruInterceptHandler(logging.Handler):
    """
    Intercept handler from the Loguru documentation which is used to intercept messages
    from the Uvicorn logger and use them with Loguru.
    
    .. note::
        See `Loguru documentation`_

    .. _Loguru documentation: https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """  # noqa

    def emit(self, record):
        # Get corresponding loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_logger() -> None:
    """Configures the Endrpi, Uvicorn, and AsyncIO loggers with a custom Loguru formatter."""

    logger_format = '<g>{time:YYYY-MM-DD HH:mm:ss}</g> [ <level>{level: <8}</level>] - <level>{message}</level>'

    # Remove the default loguru logger and add a custom formatted loguru logger
    logger.remove()
    logger.add(sys.stdout, colorize=True, format=logger_format)

    # Configure uvicorn to use the loguru formatter
    logging.getLogger('uvicorn').handlers = [LoguruInterceptHandler()]
    logging.getLogger('uvicorn').setLevel('INFO')

    # Configure asyncio to use the loguru formatter
    logging.getLogger('asyncio').handlers = [LoguruInterceptHandler()]
    logging.getLogger('asyncio').setLevel('INFO')

    # Configure endrpi to use the loguru formatter
    get_logger().handlers = [LoguruInterceptHandler()]
    get_logger().setLevel('INFO')


def get_logging_configuration() -> Dict[str, any]:
    """
    Returns a custom logging config for Uvicorn that allows it to use the :class:`LoguruInterceptHandler`.

    .. note::
        Without using this config, Uvicorn will not uphold the logging override.
    """

    return {
        **LOGGING_CONFIG,

        # This should be the default but added here just in case an update to uvicorn changes it
        "disable_existing_loggers": False,

        # This might not be necessary in the future, it looks like the uvicorn loggers are not overridable by default
        "loggers": {}
    }


def get_logger() -> logging.Logger:
    """Returns the endrpi logger."""
    return logging.getLogger('endrpi')
