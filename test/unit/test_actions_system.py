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

import unittest
from unittest import TestCase
from unittest.mock import patch

from pydantic import ValidationError, BaseModel
from endrpi.model.message import PlatformMessage, TemperatureMessage, ThrottleMessage, UpTimeMessage, SystemMessage, \
    FrequencyMessage, MemoryMessage

from endrpi.actions.system import read_temperature, read_platform, read_uptime, read_throttle, read_frequency, \
    read_memory, read_system
from endrpi.model.action_result import error_action_result, success_action_result
from endrpi.model.frequency import Frequency
from endrpi.model.measurement import UnitPrefix, InformationUnit, TemperatureUnit, FrequencyUnit
from endrpi.model.memory import Memory
from endrpi.model.platform import Platform
from endrpi.model.system import System
from endrpi.model.temperature import Temperature
from endrpi.model.throttle import Throttle
from endrpi.model.up_time import UpTime
from test.constants import get_valid_temperature, get_valid_throttle, get_valid_uptime, get_valid_frequency, \
    get_valid_memory, get_valid_platform


class TestSystemActions(TestCase):

    @patch('endrpi.actions.system.read_memory')
    @patch('endrpi.actions.system.read_frequency')
    @patch('endrpi.actions.system.read_uptime')
    @patch('endrpi.actions.system.read_throttle')
    @patch('endrpi.actions.system.read_temperature')
    @patch('endrpi.actions.system.read_platform')
    def test_read_system(self,
                         read_platform_mock,
                         read_temperature_mock,
                         read_throttle_mock,
                         read_uptime_mock,
                         read_frequency_mock,
                         read_memory_mock):
        # Ensure the underlying system call errors are propagated
        read_platform_mock.return_value = error_action_result('Failed')
        read_temperature_mock.return_value = success_action_result(get_valid_temperature())
        read_throttle_mock.return_value = success_action_result(get_valid_throttle())
        read_uptime_mock.return_value = success_action_result(get_valid_uptime())
        read_frequency_mock.return_value = success_action_result(get_valid_frequency())
        read_memory_mock.return_value = success_action_result(get_valid_memory())
        action_result = read_system()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': 'Failed'}, action_result.error)

        # Ensure validation errors are propagated
        with patch.object(System, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            read_platform_mock.return_value = success_action_result(get_valid_platform())
            read_temperature_mock.return_value = success_action_result(get_valid_temperature())
            read_throttle_mock.return_value = success_action_result(get_valid_throttle())
            read_uptime_mock.return_value = success_action_result(get_valid_uptime())
            read_frequency_mock.return_value = success_action_result(get_valid_frequency())
            read_memory_mock.return_value = success_action_result(get_valid_memory())
            action_result = read_system()
            self.assertFalse(action_result.success)
            self.assertIsNone(action_result.data)
            self.assertEqual({'message': SystemMessage.ERROR_VALIDATION}, action_result.error)

        # Ensure the underlying system call return values are aggregated correctly
        read_platform_mock.return_value = success_action_result(get_valid_platform())
        read_temperature_mock.return_value = success_action_result(get_valid_temperature())
        read_throttle_mock.return_value = success_action_result(get_valid_throttle())
        read_uptime_mock.return_value = success_action_result(get_valid_uptime())
        read_frequency_mock.return_value = success_action_result(get_valid_frequency())
        read_memory_mock.return_value = success_action_result(get_valid_memory())
        action_result = read_system()
        self.assertTrue(action_result.success)
        self.assertEqual(action_result.data.platform, read_platform_mock.return_value.data)
        self.assertEqual(action_result.data.temperature, read_temperature_mock.return_value.data)
        self.assertEqual(action_result.data.throttle, read_throttle_mock.return_value.data)
        self.assertEqual(action_result.data.uptime, read_uptime_mock.return_value.data)
        self.assertEqual(action_result.data.frequency, read_frequency_mock.return_value.data)
        self.assertEqual(action_result.data.memory, read_memory_mock.return_value.data)
        self.assertIsNone(action_result.error)

    @patch('endrpi.actions.system.system_platform')
    def test_read_platform(self, platform_mock):
        # Ensure validation errors are propagated
        with patch.object(Platform, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            action_result = read_platform()
            self.assertFalse(action_result.success)
            self.assertIsNone(action_result.data)
            self.assertEqual({'message': PlatformMessage.ERROR_VALIDATION}, action_result.error)

        # Ensure the platform values are aggregated correctly
        platform = get_valid_platform()
        platform_mock.system.return_value = platform.operatingSystem.name
        platform_mock.release.return_value = platform.operatingSystem.release
        platform_mock.version.return_value = platform.operatingSystem.version
        platform_mock.machine.return_value = platform.machineType
        platform_mock.node.return_value = platform.networkName
        action_result = read_platform()
        self.assertTrue(action_result.success)
        self.assertEqual(platform, action_result.data)
        self.assertIsNone(action_result.error)

    @patch('endrpi.actions.system.process_output')
    def test_read_temperature(self, process_output_mock):
        # Ensure null process output propagates an error
        process_output_mock.return_value = None
        action_result = read_temperature()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': TemperatureMessage.ERROR_SOC_QUERY}, action_result.error)

        # Ensure empty process output propagates an error
        process_output_mock.return_value = ''
        action_result = read_temperature()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': TemperatureMessage.ERROR_SOC_QUERY}, action_result.error)

        # Ensure invalid process output propagates an error
        process_output_mock.return_value = 'qwerty'
        action_result = read_temperature()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': TemperatureMessage.ERROR_SOC_PARSE}, action_result.error)

        # Ensure validation errors are propagated
        with patch.object(Temperature, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            process_output_mock.return_value = '1'
            action_result = read_temperature()
            self.assertFalse(action_result.success)
            self.assertIsNone(action_result.data)
            self.assertEqual({'message': TemperatureMessage.ERROR_VALIDATION}, action_result.error)

        # Ensure a simple temperature is read correctly
        process_output_mock.return_value = '1'
        action_result = read_temperature()
        self.assertTrue(action_result.success)
        self.assertEqual(0.001, action_result.data.systemOnChip.quantity)
        self.assertIsNone(action_result.data.systemOnChip.prefix)
        self.assertEqual(TemperatureUnit.CELSIUS, action_result.data.systemOnChip.unitOfMeasurement)
        self.assertIsNone(action_result.error)

        # Ensure a temperature with a leading zero is read correctly
        process_output_mock.return_value = '0102'
        action_result = read_temperature()
        self.assertTrue(action_result.success)
        self.assertEqual(0.102, action_result.data.systemOnChip.quantity)
        self.assertIsNone(action_result.data.systemOnChip.prefix)
        self.assertEqual(TemperatureUnit.CELSIUS, action_result.data.systemOnChip.unitOfMeasurement)
        self.assertIsNone(action_result.error)

        # Ensure a large temperature is read correctly
        process_output_mock.return_value = '987654'
        action_result = read_temperature()
        self.assertTrue(action_result.success)
        self.assertEqual(987.654, action_result.data.systemOnChip.quantity)
        self.assertIsNone(action_result.data.systemOnChip.prefix)
        self.assertEqual(TemperatureUnit.CELSIUS, action_result.data.systemOnChip.unitOfMeasurement)
        self.assertIsNone(action_result.error)

    @patch('endrpi.actions.system.process_output')
    @patch('endrpi.actions.system.int', wraps=int)
    def test_read_throttle(self, int_mock, process_output_mock):
        # Ensure null process output propagates an error
        process_output_mock.return_value = None
        action_result = read_throttle()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': ThrottleMessage.ERROR_QUERY}, action_result.error)

        # Ensure empty process output propagates an error
        process_output_mock.return_value = ''
        action_result = read_throttle()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': ThrottleMessage.ERROR_QUERY}, action_result.error)

        # Ensure invalid process output propagates an error
        process_output_mock.return_value = 'qwerty'
        action_result = read_throttle()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': ThrottleMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.return_value = '1234'
        action_result = read_throttle()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': ThrottleMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.return_value = 'throttled=1234'
        action_result = read_throttle()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': ThrottleMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.return_value = 'throttled=0x1234G'
        action_result = read_throttle()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': ThrottleMessage.ERROR_PARSE}, action_result.error)

        # Ensure int conversion errors propagate
        # Note: A regex check in the code "essentially" prevents conversion errors so have mock int()
        process_output_mock.return_value = 'throttled=0x12345'
        int_mock.side_effect = ValueError('Conversion error')
        action_result = read_throttle()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': ThrottleMessage.ERROR_PARSE}, action_result.error)
        int_mock.side_effect = None

        # Ensure validation errors are propagated
        with patch.object(Throttle, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            process_output_mock.return_value = 'throttled=0xF000F'
            action_result = read_throttle()
            self.assertFalse(action_result.success)
            self.assertIsNone(action_result.data)
            self.assertEqual({'message': ThrottleMessage.ERROR_VALIDATION}, action_result.error)

        # Ensure the bit flag comparisons are aggregated correctly
        process_output_mock.return_value = 'throttled=0xF000F'
        action_result = read_throttle()
        self.assertTrue(action_result.success)
        self.assertTrue(action_result.data.throttling)
        self.assertTrue(action_result.data.throttlingHasOccurred)
        self.assertTrue(action_result.data.underVoltageDetected)
        self.assertTrue(action_result.data.underVoltageHasOccurred)
        self.assertTrue(action_result.data.armFrequencyCapped)
        self.assertTrue(action_result.data.armFrequencyCappingHasOccurred)
        self.assertTrue(action_result.data.softTemperatureLimitActive)
        self.assertTrue(action_result.data.softTemperatureLimitHasOccurred)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = 'throttled=0x7000F'
        action_result = read_throttle()
        self.assertTrue(action_result.success)
        self.assertTrue(action_result.data.throttling)
        self.assertTrue(action_result.data.throttlingHasOccurred)
        self.assertTrue(action_result.data.underVoltageDetected)
        self.assertTrue(action_result.data.underVoltageHasOccurred)
        self.assertTrue(action_result.data.armFrequencyCapped)
        self.assertTrue(action_result.data.armFrequencyCappingHasOccurred)
        self.assertTrue(action_result.data.softTemperatureLimitActive)
        self.assertFalse(action_result.data.softTemperatureLimitHasOccurred)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = 'throttled=0x3000F'
        action_result = read_throttle()
        self.assertTrue(action_result.success)
        self.assertTrue(action_result.data.throttling)
        self.assertFalse(action_result.data.throttlingHasOccurred)
        self.assertTrue(action_result.data.underVoltageDetected)
        self.assertTrue(action_result.data.underVoltageHasOccurred)
        self.assertTrue(action_result.data.armFrequencyCapped)
        self.assertTrue(action_result.data.armFrequencyCappingHasOccurred)
        self.assertTrue(action_result.data.softTemperatureLimitActive)
        self.assertFalse(action_result.data.softTemperatureLimitHasOccurred)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = 'throttled=0x1000F'
        action_result = read_throttle()
        self.assertTrue(action_result.success)
        self.assertTrue(action_result.data.throttling)
        self.assertFalse(action_result.data.throttlingHasOccurred)
        self.assertTrue(action_result.data.underVoltageDetected)
        self.assertTrue(action_result.data.underVoltageHasOccurred)
        self.assertTrue(action_result.data.armFrequencyCapped)
        self.assertFalse(action_result.data.armFrequencyCappingHasOccurred)
        self.assertTrue(action_result.data.softTemperatureLimitActive)
        self.assertFalse(action_result.data.softTemperatureLimitHasOccurred)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = 'throttled=0x0000F'
        action_result = read_throttle()
        self.assertTrue(action_result.success)
        self.assertTrue(action_result.data.throttling)
        self.assertFalse(action_result.data.throttlingHasOccurred)
        self.assertTrue(action_result.data.underVoltageDetected)
        self.assertFalse(action_result.data.underVoltageHasOccurred)
        self.assertTrue(action_result.data.armFrequencyCapped)
        self.assertFalse(action_result.data.armFrequencyCappingHasOccurred)
        self.assertTrue(action_result.data.softTemperatureLimitActive)
        self.assertFalse(action_result.data.softTemperatureLimitHasOccurred)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = 'throttled=0xF'
        action_result = read_throttle()
        self.assertTrue(action_result.success)
        self.assertTrue(action_result.data.throttling)
        self.assertFalse(action_result.data.throttlingHasOccurred)
        self.assertTrue(action_result.data.underVoltageDetected)
        self.assertFalse(action_result.data.underVoltageHasOccurred)
        self.assertTrue(action_result.data.armFrequencyCapped)
        self.assertFalse(action_result.data.armFrequencyCappingHasOccurred)
        self.assertTrue(action_result.data.softTemperatureLimitActive)
        self.assertFalse(action_result.data.softTemperatureLimitHasOccurred)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = 'throttled=0x00007'
        action_result = read_throttle()
        self.assertTrue(action_result.success)
        self.assertTrue(action_result.data.throttling)
        self.assertFalse(action_result.data.throttlingHasOccurred)
        self.assertTrue(action_result.data.underVoltageDetected)
        self.assertFalse(action_result.data.underVoltageHasOccurred)
        self.assertTrue(action_result.data.armFrequencyCapped)
        self.assertFalse(action_result.data.armFrequencyCappingHasOccurred)
        self.assertFalse(action_result.data.softTemperatureLimitActive)
        self.assertFalse(action_result.data.softTemperatureLimitHasOccurred)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = 'throttled=0x00003'
        action_result = read_throttle()
        self.assertTrue(action_result.success)
        self.assertFalse(action_result.data.throttling)
        self.assertFalse(action_result.data.throttlingHasOccurred)
        self.assertTrue(action_result.data.underVoltageDetected)
        self.assertFalse(action_result.data.underVoltageHasOccurred)
        self.assertTrue(action_result.data.armFrequencyCapped)
        self.assertFalse(action_result.data.armFrequencyCappingHasOccurred)
        self.assertFalse(action_result.data.softTemperatureLimitActive)
        self.assertFalse(action_result.data.softTemperatureLimitHasOccurred)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = 'throttled=0x00001'
        action_result = read_throttle()
        self.assertTrue(action_result.success)
        self.assertFalse(action_result.data.throttling)
        self.assertFalse(action_result.data.throttlingHasOccurred)
        self.assertTrue(action_result.data.underVoltageDetected)
        self.assertFalse(action_result.data.underVoltageHasOccurred)
        self.assertFalse(action_result.data.armFrequencyCapped)
        self.assertFalse(action_result.data.armFrequencyCappingHasOccurred)
        self.assertFalse(action_result.data.softTemperatureLimitActive)
        self.assertFalse(action_result.data.softTemperatureLimitHasOccurred)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = 'throttled=0x00000'
        action_result = read_throttle()
        self.assertTrue(action_result.success)
        self.assertFalse(action_result.data.throttling)
        self.assertFalse(action_result.data.throttlingHasOccurred)
        self.assertFalse(action_result.data.underVoltageDetected)
        self.assertFalse(action_result.data.underVoltageHasOccurred)
        self.assertFalse(action_result.data.armFrequencyCapped)
        self.assertFalse(action_result.data.armFrequencyCappingHasOccurred)
        self.assertFalse(action_result.data.softTemperatureLimitActive)
        self.assertFalse(action_result.data.softTemperatureLimitHasOccurred)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = 'throttled=0x0'
        action_result = read_throttle()
        self.assertTrue(action_result.success)
        self.assertFalse(action_result.data.throttling)
        self.assertFalse(action_result.data.throttlingHasOccurred)
        self.assertFalse(action_result.data.underVoltageDetected)
        self.assertFalse(action_result.data.underVoltageHasOccurred)
        self.assertFalse(action_result.data.armFrequencyCapped)
        self.assertFalse(action_result.data.armFrequencyCappingHasOccurred)
        self.assertFalse(action_result.data.softTemperatureLimitActive)
        self.assertFalse(action_result.data.softTemperatureLimitHasOccurred)
        self.assertIsNone(action_result.error)

    @patch('endrpi.actions.system.process_output')
    @patch('endrpi.actions.system.float', wraps=float)
    def test_read_uptime(self, float_mock, process_output_mock):
        # Ensure null process output propagates an error
        process_output_mock.return_value = None
        action_result = read_uptime()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': UpTimeMessage.ERROR_QUERY}, action_result.error)

        # Ensure empty process output propagates an error
        process_output_mock.return_value = ''
        action_result = read_uptime()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': UpTimeMessage.ERROR_QUERY}, action_result.error)

        # Ensure invalid process outputs propagate errors
        process_output_mock.return_value = 'qwerty'
        action_result = read_uptime()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': UpTimeMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.return_value = '1234'
        action_result = read_uptime()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': UpTimeMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.return_value = '1234 '
        action_result = read_uptime()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': UpTimeMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.return_value = '1234 q'
        action_result = read_uptime()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': UpTimeMessage.ERROR_PARSE}, action_result.error)

        # Ensure float conversion errors propagate
        # Note: A regex check in the code "essentially" prevents conversion errors so have mock float()
        process_output_mock.return_value = '1234 5'
        float_mock.side_effect = ValueError('Conversion error')
        action_result = read_uptime()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': UpTimeMessage.ERROR_PARSE}, action_result.error)
        float_mock.side_effect = None

        # Ensure validation errors are propagated
        with patch.object(UpTime, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            process_output_mock.return_value = '1234 5'
            action_result = read_uptime()
            self.assertFalse(action_result.success)
            self.assertIsNone(action_result.data)
            self.assertEqual({'message': UpTimeMessage.ERROR_VALIDATION}, action_result.error)

        # Ensure the uptime data is aggregated correctly for valid process outputs
        process_output_mock.return_value = '1234 5'
        action_result = read_uptime()
        self.assertTrue(action_result.success)
        self.assertEqual(1234, action_result.data.seconds)
        self.assertEqual('0:20:34', action_result.data.formatted)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = '12.34 5'
        action_result = read_uptime()
        self.assertTrue(action_result.success)
        self.assertEqual(12.34, action_result.data.seconds)
        self.assertEqual('0:00:12', action_result.data.formatted)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = '00123.45 0'
        action_result = read_uptime()
        self.assertTrue(action_result.success)
        self.assertEqual(123.45, action_result.data.seconds)
        self.assertEqual('0:02:03', action_result.data.formatted)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = '86400 0'
        action_result = read_uptime()
        self.assertTrue(action_result.success)
        self.assertEqual(86400, action_result.data.seconds)
        self.assertEqual('1 day, 0:00:00', action_result.data.formatted)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = '86401 0'
        action_result = read_uptime()
        self.assertTrue(action_result.success)
        self.assertEqual(86401, action_result.data.seconds)
        self.assertEqual('1 day, 0:00:01', action_result.data.formatted)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = '86399 0'
        action_result = read_uptime()
        self.assertTrue(action_result.success)
        self.assertEqual(86399, action_result.data.seconds)
        self.assertEqual('23:59:59', action_result.data.formatted)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = '9999999999 0'
        action_result = read_uptime()
        self.assertTrue(action_result.success)
        self.assertEqual(9999999999, action_result.data.seconds)
        self.assertEqual('115740 days, 17:46:39', action_result.data.formatted)
        self.assertIsNone(action_result.error)

    @patch('endrpi.actions.system.process_output')
    @patch('endrpi.actions.system.float', wraps=float)
    def test_read_frequency(self, float_mock, process_output_mock):
        # Ensure null process output propagates an error
        process_output_mock.side_effect = [None, None]
        action_result = read_frequency()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': FrequencyMessage.ERROR_ARM_QUERY}, action_result.error)

        # Ensure empty process output propagates an error
        process_output_mock.side_effect = ['', '']
        action_result = read_frequency()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': FrequencyMessage.ERROR_ARM_QUERY}, action_result.error)

        # Ensure partially null process output propagates an error
        process_output_mock.side_effect = ['arm frequency', None]
        action_result = read_frequency()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': FrequencyMessage.ERROR_CORE_QUERY}, action_result.error)

        # Ensure partially empty process output propagates an error
        process_output_mock.side_effect = ['arm frequency', '']
        action_result = read_frequency()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': FrequencyMessage.ERROR_CORE_QUERY}, action_result.error)

        # Ensure invalid process outputs propagate errors
        process_output_mock.side_effect = ['frequency(45)=', 'frequency(1)=']
        action_result = read_frequency()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': FrequencyMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.side_effect = ['frequency(45)=5', 'frequency(1)=']
        action_result = read_frequency()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': FrequencyMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.side_effect = ['frequency(45)=', 'frequency(1)=5']
        action_result = read_frequency()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': FrequencyMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.side_effect = ['frequency(45)=test', 'frequency(1)=5']
        action_result = read_frequency()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': FrequencyMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.side_effect = ['frequency(45)=5', 'frequency(1)=test']
        action_result = read_frequency()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': FrequencyMessage.ERROR_PARSE}, action_result.error)

        # Ensure float conversion errors propagate
        # Note: A regex check in the code "essentially" prevents conversion errors so have mock float()
        process_output_mock.side_effect = ['frequency(45)=600', 'frequency(1)=600']
        float_mock.side_effect = [ValueError('Conversion error'), 1234]
        action_result = read_frequency()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': FrequencyMessage.ERROR_PARSE}, action_result.error)
        float_mock.side_effect = None

        process_output_mock.side_effect = ['frequency(45)=600', 'frequency(1)=600']
        float_mock.side_effect = [1234, ValueError('Conversion error')]
        action_result = read_frequency()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': FrequencyMessage.ERROR_PARSE}, action_result.error)
        float_mock.side_effect = None

        # Ensure validation errors are propagated
        with patch.object(Frequency, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            process_output_mock.side_effect = ['frequency(45)=600000', 'frequency(1)=400000']
            action_result = read_frequency()
            self.assertFalse(action_result.success)
            self.assertIsNone(action_result.data)
            self.assertEqual({'message': FrequencyMessage.ERROR_VALIDATION}, action_result.error)

        # Ensure the frequency data is aggregated correctly for valid process output
        process_output_mock.side_effect = ['frequency(45)=600000', 'frequency(1)=400000']
        action_result = read_frequency()
        self.assertTrue(action_result.success)
        self.assertEqual(600000, action_result.data.arm.quantity)
        self.assertIsNone(action_result.data.arm.prefix)
        self.assertEqual(FrequencyUnit.HERTZ, action_result.data.arm.unitOfMeasurement)
        self.assertEqual(400000, action_result.data.core.quantity)
        self.assertIsNone(action_result.data.core.prefix)
        self.assertEqual(FrequencyUnit.HERTZ, action_result.data.core.unitOfMeasurement)

    @patch('endrpi.actions.system.process_output')
    @patch('endrpi.actions.system.int', wraps=int)
    def test_read_memory(self, int_mock, process_output_mock):
        # Ensure null process output propagates an error
        process_output_mock.return_value = None
        action_result = read_memory()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': MemoryMessage.ERROR_QUERY}, action_result.error)

        # Ensure empty process output propagates an error
        process_output_mock.return_value = ''
        action_result = read_memory()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': MemoryMessage.ERROR_QUERY}, action_result.error)

        # Ensure invalid process outputs propagate errors
        process_output_mock.return_value = 'qwerty'
        action_result = read_memory()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': MemoryMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.return_value = '1234'
        action_result = read_memory()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': MemoryMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.return_value = 'MemTotal: 1234 kB ' \
                                           'MemAvailable: 1234 kB'
        action_result = read_memory()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': MemoryMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.return_value = 'MemTotal: 1234 kB ' \
                                           'MemFree: 1234 kB '
        action_result = read_memory()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': MemoryMessage.ERROR_PARSE}, action_result.error)

        process_output_mock.return_value = 'MemTotal: kB ' \
                                           'MemFree: kB ' \
                                           'MemAvailable: kB'
        action_result = read_memory()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': MemoryMessage.ERROR_PARSE}, action_result.error)

        # Ensure int conversion errors propagate
        # Note: A regex check in the code "essentially" prevents conversion errors so have mock int()
        process_output_mock.return_value = 'MemTotal: 1 kB ' \
                                           'MemFree: 1 kB ' \
                                           'MemAvailable: 1 kB'
        int_mock.side_effect = ValueError('Conversion error')
        action_result = read_memory()
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': MemoryMessage.ERROR_PARSE}, action_result.error)
        int_mock.side_effect = None

        # Ensure validations errors propagate
        with patch.object(Memory, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            process_output_mock.return_value = 'MemTotal: 1 kB ' \
                                               'MemFree: 1 kB ' \
                                               'MemAvailable: 1 kB'
            action_result = read_memory()
            self.assertFalse(action_result.success)
            self.assertIsNone(action_result.data)
            self.assertEqual({'message': MemoryMessage.ERROR_VALIDATION}, action_result.error)

        # Ensure the memory data is aggregated correctly for valid process output
        process_output_mock.return_value = 'MemTotal: 1 kB ' \
                                           'MemFree: 1 kB ' \
                                           'MemAvailable: 1 kB'
        action_result = read_memory()
        self.assertTrue(action_result.success)
        self.assertEqual(action_result.data.total.quantity, 1.0)
        self.assertEqual(action_result.data.total.prefix, UnitPrefix.KILO)
        self.assertEqual(action_result.data.total.unitOfMeasurement, InformationUnit.BYTE)
        self.assertEqual(action_result.data.free.quantity, 1.0)
        self.assertEqual(action_result.data.free.prefix, UnitPrefix.KILO)
        self.assertEqual(action_result.data.free.unitOfMeasurement, InformationUnit.BYTE)
        self.assertEqual(action_result.data.available.quantity, 1.0)
        self.assertEqual(action_result.data.available.prefix, UnitPrefix.KILO)
        self.assertEqual(action_result.data.available.unitOfMeasurement, InformationUnit.BYTE)
        self.assertIsNone(action_result.error)

        process_output_mock.return_value = 'MemTotal: 012 kB ' \
                                           'MemFree: 340 kB ' \
                                           'MemAvailable: 0560 kB'
        action_result = read_memory()
        self.assertTrue(action_result.success)
        self.assertEqual(action_result.data.total.quantity, 12.0)
        self.assertEqual(action_result.data.total.prefix, UnitPrefix.KILO)
        self.assertEqual(action_result.data.total.unitOfMeasurement, InformationUnit.BYTE)
        self.assertEqual(action_result.data.free.quantity, 340.0)
        self.assertEqual(action_result.data.free.prefix, UnitPrefix.KILO)
        self.assertEqual(action_result.data.free.unitOfMeasurement, InformationUnit.BYTE)
        self.assertEqual(action_result.data.available.quantity, 560.0)
        self.assertEqual(action_result.data.available.prefix, UnitPrefix.KILO)
        self.assertEqual(action_result.data.available.unitOfMeasurement, InformationUnit.BYTE)
        self.assertIsNone(action_result.error)


if __name__ == '__main__':
    unittest.main()
