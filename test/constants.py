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

from endrpi.model.frequency import Frequency
from endrpi.model.measurement import Measurement, TemperatureUnit, FrequencyUnit, InformationUnit, UnitPrefix
from endrpi.model.memory import Memory
from endrpi.model.platform import Platform, OperatingSystem
from endrpi.model.system import System
from endrpi.model.temperature import Temperature
from endrpi.model.throttle import Throttle
from endrpi.model.up_time import UpTime


def get_valid_system():
    return System(
        platform=get_valid_platform(),
        temperature=get_valid_temperature(),
        throttle=get_valid_throttle(),
        uptime=get_valid_uptime(),
        frequency=get_valid_frequency(),
        memory=get_valid_memory()
    )


def get_valid_operating_system():
    return OperatingSystem(name='OS Name', release='123', version='1.2.3')


def get_valid_platform():
    return Platform(machineType='Machine',
                    networkName='machine-1',
                    operatingSystem=get_valid_operating_system())


def get_valid_temperature():
    return Temperature(systemOnChip=Measurement(quantity=20, unitOfMeasurement=TemperatureUnit.CELSIUS))


def get_valid_throttle():
    return Throttle(throttling=True, throttlingHasOccurred=True,
                    underVoltageDetected=True, underVoltageHasOccurred=False,
                    armFrequencyCapped=False, armFrequencyCappingHasOccurred=True,
                    softTemperatureLimitActive=True, softTemperatureLimitHasOccurred=True)


def get_valid_uptime():
    return UpTime(seconds=123456, formatted='1 day, 10:17:36')


def get_valid_frequency():
    return Frequency(arm=Measurement(quantity=600000, unitOfMeasurement=FrequencyUnit.HERTZ),
                     core=Measurement(quantity=500000, unitOfMeasurement=FrequencyUnit.HERTZ))


def get_valid_memory():
    return Memory(total=Measurement(prefix=UnitPrefix.KILO, quantity=4000, unitOfMeasurement=InformationUnit.BYTE),
                  free=Measurement(prefix=UnitPrefix.KILO, quantity=100, unitOfMeasurement=InformationUnit.BYTE),
                  available=Measurement(prefix=UnitPrefix.KILO, quantity=200, unitOfMeasurement=InformationUnit.BYTE))
