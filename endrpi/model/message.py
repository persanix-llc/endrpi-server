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

from pydantic import BaseModel


class WebSocketMessage(str, Enum):
    ERROR_INVALID_DATA = 'Received invalid message'
    ERROR_MISSING_ACTION_FIELD = 'Received message with missing \'action\' field'
    ERROR_INVALID_ACTION_FIELD = 'Received message with invalid \'action\' field'
    ERROR_UNKNOWN_ACTION_VALUE = 'Received message with unknown \'action\' value'
    ERROR_MISSING_PARAMS_FIELD = 'Received message with missing \'params\' field'
    ERROR_INVALID_PARAMS_FIELD = 'Received message with invalid \'params\' field'
    ERROR_MISSING_PIN_ID = 'At least one pin id and pin configuration must be supplied'
    SUCCESS_PIN_CONFIGS_UPDATED = 'Pin configurations updated'


class SystemMessage(str, Enum):
    ERROR_VALIDATION = 'Failed to validate system'


class PlatformMessage(str, Enum):
    ERROR_VALIDATION = 'Failed to validate system platform'


class TemperatureMessage(str, Enum):
    ERROR_SOC_QUERY = 'Failed to query system on chip temperature'
    ERROR_SOC_PARSE = 'Failed to parse system on chip temperature query'
    ERROR_VALIDATION = 'Failed to validate system temperature'


class ThrottleMessage(str, Enum):
    ERROR_QUERY = 'Failed to query system throttle status'
    ERROR_PARSE = 'Failed to parse system throttle status query'
    ERROR_VALIDATION = 'Failed to validate system throttle'


class UpTimeMessage(str, Enum):
    ERROR_QUERY = 'Failed to query system uptime'
    ERROR_PARSE = 'Failed to parse system uptime query'
    ERROR_VALIDATION = 'Failed to validate system uptime'


class FrequencyMessage(str, Enum):
    ERROR_ARM_QUERY = 'Failed to query system ARM frequency'
    ERROR_CORE_QUERY = 'Failed to query system core frequency'
    ERROR_PARSE = 'Failed to parse system frequency query'
    ERROR_VALIDATION = 'Failed to validate system frequency'


class MemoryMessage(str, Enum):
    ERROR_QUERY = 'Failed to query system memory'
    ERROR_PARSE = 'Failed to parse system memory query'
    ERROR_VALIDATION = 'Failed to validate system memory'


class PinMessage(str, Enum):
    ERROR_VALIDATION = 'Failed to validate pin configuration'
    ERROR_UNSUPPORTED__PIN_ID__ = 'Failed to read unsupported pin `{pin_id}`'
    ERROR_NO_INPUT_PULL = 'No pull specified for input pin configuration'
    ERROR_NO_OUTPUT_STATE = 'No state specified for output pin configuration'
    ERROR_NOT_FOUND__PIN_ID__ = 'Pin with BCM pin number `{pin_id}` not found'
    SUCCESS_UPDATED__PIN_ID__ = 'Pin configuration for pin `{pin_id}` was updated successfully'


class MessageData(BaseModel):
    """
    Interface used to represent a simple message as a data object.

    .. note::
        Usually used for JSON error responses.
    """
    message: str
