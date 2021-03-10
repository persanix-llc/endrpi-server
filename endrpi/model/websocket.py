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
from typing import TypeVar, Generic, List, Optional

from pydantic import BaseModel
from pydantic.generics import GenericModel

from endrpi.model.pin import RaspberryPiPinIds, PinConfigurationMap

# Pydantic generics
T = TypeVar('T')
S = TypeVar('S')


class WebSocketInput(GenericModel, Generic[T, S]):
    """Interface for generic websocket input."""
    action: T
    params: Optional[S]


class WebSocketAction(str, Enum):
    """Enumerations for all web socket actions."""
    READ_TEMPERATURE = 'READ_TEMPERATURE'
    READ_THROTTLE = 'READ_THROTTLE'
    READ_UPTIME = 'READ_UPTIME'
    READ_FREQUENCY = 'READ_FREQUENCY'
    READ_MEMORY = 'READ_MEMORY'
    READ_PIN_CONFIGURATIONS = 'READ_PIN_CONFIGURATIONS'
    UPDATE_PIN_CONFIGURATIONS = 'UPDATE_PIN_CONFIGURATIONS'


class ReadPinConfigurationsParams(BaseModel):
    pins: List[RaspberryPiPinIds]


class UpdatePinConfigurationsParams(BaseModel):
    pins: PinConfigurationMap
