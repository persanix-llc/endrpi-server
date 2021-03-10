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

from enum import Enum
from typing import Union, Dict, Optional

from pydantic import BaseModel


class RaspberryPiPinIds(str, Enum):
    """Enumerations for pin ids on the Raspberry Pi."""
    GPIO2 = 'GPIO2'
    GPIO3 = 'GPIO3'
    GPIO4 = 'GPIO4'
    GPIO14 = 'GPIO14'
    GPIO15 = 'GPIO15'
    GPIO17 = 'GPIO17'
    GPIO18 = 'GPIO18'
    GPIO27 = 'GPIO27'
    GPIO22 = 'GPIO22'
    GPIO23 = 'GPIO23'
    GPIO24 = 'GPIO24'
    GPIO10 = 'GPIO10'
    GPIO9 = 'GPIO9'
    GPIO25 = 'GPIO25'
    GPIO11 = 'GPIO11'
    GPIO7 = 'GPIO7'
    GPIO5 = 'GPIO5'
    GPIO6 = 'GPIO6'
    GPIO12 = 'GPIO12'
    GPIO13 = 'GPIO13'
    GPIO19 = 'GPIO19'
    GPIO16 = 'GPIO16'
    GPIO26 = 'GPIO26'
    GPIO20 = 'GPIO20'
    GPIO21 = 'GPIO21'

    @classmethod
    def from_bcm_id(cls, pin_id: str) -> Union['RaspberryPiPinIds', None]:
        # Attempt to instantiate a raspberry pi pin id from a string and return the pin id
        try:
            return cls[pin_id]
        except KeyError:
            return None


class PinPull(str, Enum):
    """Enumerations for the pull states of a GPIO pin."""
    FLOATING = 'FLOATING'
    UP = 'UP'
    DOWN = 'DOWN'


class PinIo(str, Enum):
    """Enumerations for the io states of a GPIO pin."""
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'


class PinConfiguration(BaseModel):
    """Interface for GPIO pin io function, state, and pull."""
    io: PinIo
    state: Optional[float]
    pull: Optional[PinPull]


PinConfigurationMap = Dict[RaspberryPiPinIds, PinConfiguration]
