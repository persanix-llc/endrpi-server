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
from typing import TypeVar, Generic, Optional

from pydantic.generics import GenericModel

# Pydantic generic
T = TypeVar('T')


class UnitPrefix(str, Enum):
    """
    Enumerations for standard metric prefixes.

    Reference: `Metric prefix`_

    .. _Metric prefix: https://en.wikipedia.org/wiki/Metric_prefix
    """
    KILO = 'KILO'
    MEGA = 'MEGA'
    GIGA = 'GIGA'


class FrequencyUnit(str, Enum):
    """Enumerations for frequency units."""
    HERTZ = 'HERTZ'


class InformationUnit(str, Enum):
    """Enumerations for information units."""
    BYTE = 'BYTE'


class TemperatureUnit(str, Enum):
    """Enumerations for temperature units."""
    CELSIUS = 'CELSIUS'
    FAHRENHEIT = 'FAHRENHEIT'


class Measurement(GenericModel, Generic[T]):
    """Interface for standardized measurements using quantity and unit."""
    quantity: float
    prefix: Optional[UnitPrefix]
    unitOfMeasurement: T
