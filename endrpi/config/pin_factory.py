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

from gpiozero import Device
from gpiozero.pins.local import LocalPiFactory
from gpiozero.pins.mock import MockFactory
from gpiozero.pins.native import NativeFactory

from endrpi.config.logging import get_logger


def configure_pin_factory() -> None:
    """
    Configures GPIOZero to use the :class:`NativeFactory` if possible, otherwise falls back to :class:`MockFactory`.
    """

    logger = get_logger()

    # noinspection PyBroadException
    try:
        pin_factory: LocalPiFactory = NativeFactory()
    except Exception:
        pin_factory: LocalPiFactory = MockFactory()
        logger.warning('Failed Raspberry Pi GPIO initialization, all pin interactions will be mocked.')

    Device.pin_factory = pin_factory
