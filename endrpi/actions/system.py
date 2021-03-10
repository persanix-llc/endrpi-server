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

import datetime
import platform as system_platform
import re
from typing import Dict, Callable, Union

from pydantic import ValidationError

from endrpi.model.action_result import ActionResult, error_action_result, success_action_result
from endrpi.model.frequency import Frequency
from endrpi.model.measurement import Measurement, TemperatureUnit, UnitPrefix, InformationUnit, FrequencyUnit
from endrpi.model.memory import Memory
from endrpi.model.message import PlatformMessage, TemperatureMessage, \
    ThrottleMessage, UpTimeMessage, FrequencyMessage, MemoryMessage, SystemMessage
from endrpi.model.platform import Platform, OperatingSystem
from endrpi.model.system import System
from endrpi.model.temperature import Temperature
from endrpi.model.throttle import Throttle
from endrpi.model.up_time import UpTime
from endrpi.utils.bitwise import is_bit_set
from endrpi.utils.process import process_output


def read_system() -> ActionResult[System]:
    """Returns the result of attempting to read all system statuses."""

    field_actions: Dict[str, Callable[[], ActionResult]] = {
        'platform': read_platform,
        'temperature': read_temperature,
        'throttle': read_throttle,
        'uptime': read_uptime,
        'frequency': read_frequency,
        'memory': read_memory
    }

    # Iterate through each field action, read its corresponding data, and add it to the response args
    system_response_args = {}
    for field_name, field_action in field_actions.items():
        action_result = field_action()
        if action_result.success:
            system_response_args[field_name] = action_result.data
        else:
            return error_action_result(action_result.error.message)

    try:
        system = System(**system_response_args)
        return success_action_result(system)
    except ValidationError:
        return error_action_result(SystemMessage.ERROR_VALIDATION)


def read_platform() -> ActionResult[Platform]:
    """Returns the result of attempting to read :class:`endrpi.model.platform.Platform` data."""

    try:
        operating_system = OperatingSystem(
            name=system_platform.system(),
            release=system_platform.release(),
            version=system_platform.version()
        )
        platform = Platform(
            machineType=system_platform.machine(),
            networkName=system_platform.node(),
            operatingSystem=operating_system
        )

        return success_action_result(platform)
    except ValidationError:
        return error_action_result(PlatformMessage.ERROR_VALIDATION)


def read_temperature() -> ActionResult[Temperature]:
    """Returns the result of attempting to read :class:`endrpi.model.temperature.Temperature` data."""

    # The temperature output is expected to resemble '123456'
    # See: https://www.kernel.org/doc/Documentation/thermal/sysfs-api.txt
    temperature_output: Union[str, None] = process_output(['cat', '/sys/class/thermal/thermal_zone0/temp'])

    if not temperature_output:
        return error_action_result(TemperatureMessage.ERROR_SOC_QUERY)

    try:
        # Attempt to convert the temperature string to an integer (i.e. '123456' -> 123456)
        temperature_number = int(temperature_output, 10)
    except ValueError:
        return error_action_result(TemperatureMessage.ERROR_SOC_PARSE)

    # Convert the raw temperature integer output to celsius and wrap it with a measurement object
    temperature_celsius = temperature_number / 1000
    system_on_chip_temperature = Measurement(quantity=temperature_celsius, unitOfMeasurement=TemperatureUnit.CELSIUS)

    try:
        temperature = Temperature(systemOnChip=system_on_chip_temperature)
        return success_action_result(temperature)
    except ValidationError:
        return error_action_result(TemperatureMessage.ERROR_VALIDATION)


def read_throttle() -> ActionResult[Throttle]:
    """Returns the result of attempting to read :class:`endrpi.model.throttle.Throttle` data."""

    # The throttle output is expected to resemble 'throttled=0x50000'
    throttle_output: Union[str, None] = process_output(['vcgencmd', 'get_throttled'])

    if not throttle_output:
        return error_action_result(ThrottleMessage.ERROR_QUERY)

    # Ensure the throttle process command returned valid data ('throttled=0x50000')
    throttle_search = re.search('^throttled=(0x[0-9a-fA-F]{1,5})$', throttle_output)
    if not throttle_search:
        return error_action_result(ThrottleMessage.ERROR_PARSE)

    # Get the hex code from the command output (i.e. 'throttled=0x50000' -> '0x50000')
    throttle_code_text = throttle_search.group(1)

    try:
        # Attempt to convert the throttle code hex string to an integer (i.e. '0x50000' -> 327680)
        throttle_code = int(throttle_code_text, 16)
    except ValueError:
        return error_action_result(ThrottleMessage.ERROR_PARSE)

    try:
        throttle = Throttle(
            throttling=is_bit_set(throttle_code, 2),
            throttlingHasOccurred=is_bit_set(throttle_code, 18),
            underVoltageDetected=is_bit_set(throttle_code, 0),
            underVoltageHasOccurred=is_bit_set(throttle_code, 16),
            armFrequencyCapped=is_bit_set(throttle_code, 1),
            armFrequencyCappingHasOccurred=is_bit_set(throttle_code, 17),
            softTemperatureLimitActive=is_bit_set(throttle_code, 3),
            softTemperatureLimitHasOccurred=is_bit_set(throttle_code, 19)
        )
        return success_action_result(throttle)
    except ValidationError:
        return error_action_result(ThrottleMessage.ERROR_VALIDATION)


def read_uptime() -> ActionResult[UpTime]:
    """Returns the result of attempting to read :class:`endrpi.model.uptime.UpTime` data."""

    # The uptime output is expected to resemble '1648.26 5522.57'
    # Reference: https://man7.org/linux/man-pages/man5/proc.5.html
    uptime_output: Union[str, None] = process_output(['cat', '/proc/uptime'])

    if not uptime_output:
        return error_action_result(UpTimeMessage.ERROR_QUERY)

    # Ensure the uptime process command returned valid data (uptime, idle time - '1648.26 5522.57')
    uptime_search = re.search(r'(\d+(\.\d*)?)\s(\d+(\.\d*)?)', uptime_output)
    if not uptime_search:
        return error_action_result(UpTimeMessage.ERROR_PARSE)

    # Get the uptime measurement from the command output (i.e. '1648.26 5522.57' -> '1648.26')
    uptime_text = uptime_search.group(1)

    try:
        # Attempt to convert the uptime string to a float (i.e. '1648.26' -> 1648.26)
        uptime_seconds = float(uptime_text)
    except ValueError:
        return error_action_result(UpTimeMessage.ERROR_PARSE)

    # Format the seconds to a human readable date (i.e. 1648 -> 0:27:28)
    # Note: Seconds are rounded to remove unwanted milliseconds (i.e. 1648.26 -> 0:27:28.260000)
    rounded_uptime_seconds = round(uptime_seconds)
    uptime_time_delta = datetime.timedelta(seconds=rounded_uptime_seconds)
    uptime_formatted = str(uptime_time_delta)

    try:
        uptime = UpTime(seconds=uptime_seconds, formatted=uptime_formatted)
        return success_action_result(uptime)
    except ValidationError:
        return error_action_result(UpTimeMessage.ERROR_VALIDATION)


def read_frequency() -> ActionResult[Frequency]:
    """Returns the result of attempting to read :class:`endrpi.model.frequency.Frequency` data."""

    # The frequency outputs are expected to resemble 'frequency(45)=600000000'
    arm_frequency_output: Union[str, None] = process_output(['vcgencmd', 'measure_clock', 'arm'])
    core_frequency_output: Union[str, None] = process_output(['vcgencmd', 'measure_clock', 'core'])

    if not arm_frequency_output:
        return error_action_result(FrequencyMessage.ERROR_ARM_QUERY)
    if not core_frequency_output:
        return error_action_result(FrequencyMessage.ERROR_CORE_QUERY)

    # Ensure the frequency process commands returned valid data (i.e. 'frequency(45)=600000000')
    # Note: The frequency response number seems to be an array index (changed from 45 -> 48 in update)
    arm_frequency_search = re.search('^frequency[(][0-9]{1,2}[)]=([0-9]+)$', arm_frequency_output)
    core_frequency_search = re.search('^frequency[(][0-9]{1,2}[)]=([0-9]+)$', core_frequency_output)
    if not arm_frequency_search or not core_frequency_search:
        return error_action_result(FrequencyMessage.ERROR_PARSE)

    # Get the hertz measurements from the command outputs (i.e. 'frequency(45)=600000000' -> '600000000')
    arm_frequency_hertz_text = arm_frequency_search.group(1)
    core_frequency_hertz_text = core_frequency_search.group(1)

    try:
        # Attempt to convert the hertz strings to floats (i.e. '600000000' -> 600000000)
        arm_frequency_hertz = float(arm_frequency_hertz_text)
        core_frequency_hertz = float(core_frequency_hertz_text)
    except ValueError:
        return error_action_result(FrequencyMessage.ERROR_PARSE)

    try:
        frequency = Frequency(
            arm=Measurement(quantity=arm_frequency_hertz, unitOfMeasurement=FrequencyUnit.HERTZ),
            core=Measurement(quantity=core_frequency_hertz, unitOfMeasurement=FrequencyUnit.HERTZ),
        )
        return success_action_result(frequency)
    except ValidationError:
        return error_action_result(FrequencyMessage.ERROR_VALIDATION)


def read_memory() -> ActionResult[Memory]:
    """Returns the result of attempting to read :class:`endrpi.model.memory.Memory` data."""

    # The meminfo output is expected to resemble:
    # MemTotal:         948280 kB
    # MemFree:          603056 kB
    # MemAvailable:     771196 kB
    # ...
    # See: https://github.com/torvalds/linux/blob/master/Documentation/filesystems/proc.rst#meminfo
    meminfo_output: Union[str, None] = process_output(['cat', '/proc/meminfo'])

    if not meminfo_output:
        return error_action_result(MemoryMessage.ERROR_QUERY)

    # Ensure the meminfo process command returned valid data (i.e. 'MemTotal:         948280 kB')
    mem_total_search = re.search(r'MemTotal:\s+([0-9]+)\s+kB', meminfo_output)
    mem_free_search = re.search(r'MemFree:\s+([0-9]+)\s+kB', meminfo_output)
    mem_available_search = re.search(r'MemAvailable:\s+([0-9]+)\s+kB', meminfo_output)
    if not mem_total_search or not mem_free_search or not mem_available_search:
        return error_action_result(MemoryMessage.ERROR_PARSE)

    # Get the byte measurements from the command outputs (i.e. 'MemTotal: 948280 kB' -> '948280')
    mem_total_text = mem_total_search.group(1)
    mem_free_text = mem_free_search.group(1)
    mem_available_text = mem_available_search.group(1)

    try:
        # Attempt to convert the memory strings to integers (i.e. '948280' -> 948280)
        mem_total_kb = int(mem_total_text)
        mem_free_kb = int(mem_free_text)
        mem_available_kb = int(mem_available_text)
    except ValueError:
        return error_action_result(MemoryMessage.ERROR_PARSE)

    try:
        mem_total = Measurement(quantity=mem_total_kb,
                                prefix=UnitPrefix.KILO,
                                unitOfMeasurement=InformationUnit.BYTE)
        mem_free = Measurement(quantity=mem_free_kb,
                               prefix=UnitPrefix.KILO,
                               unitOfMeasurement=InformationUnit.BYTE)
        mem_available = Measurement(quantity=mem_available_kb,
                                    prefix=UnitPrefix.KILO,
                                    unitOfMeasurement=InformationUnit.BYTE)
        memory = Memory(total=mem_total, free=mem_free, available=mem_available)
        return success_action_result(memory)
    except ValidationError:
        return error_action_result(MemoryMessage.ERROR_VALIDATION)
