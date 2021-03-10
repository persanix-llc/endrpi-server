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

import json
import unittest
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient
from pydantic import ValidationError, BaseModel

from endrpi.model.action_result import error_action_result, success_action_result
from endrpi.model.frequency import Frequency
from endrpi.model.memory import Memory
from endrpi.model.message import PlatformMessage, TemperatureMessage, ThrottleMessage, \
    UpTimeMessage, FrequencyMessage, MemoryMessage
from endrpi.model.platform import Platform
from endrpi.model.temperature import Temperature
from endrpi.model.throttle import Throttle
from endrpi.model.up_time import UpTime
from endrpi.server import app
from test.constants import get_valid_system, get_valid_platform, get_valid_temperature, get_valid_throttle, \
    get_valid_uptime, get_valid_frequency, get_valid_memory


class TestSystemRoutes(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.client = TestClient(app)

    @patch('endrpi.actions.system.read_memory')
    @patch('endrpi.actions.system.read_frequency')
    @patch('endrpi.actions.system.read_uptime')
    @patch('endrpi.actions.system.read_throttle')
    @patch('endrpi.actions.system.read_temperature')
    @patch('endrpi.actions.system.read_platform')
    def test_get_system_route(self,
                              read_platform_mock,
                              read_temperature_mock,
                              read_throttle_mock,
                              read_uptime_mock,
                              read_frequency_mock,
                              read_memory_mock):
        # Ensure action result errors are propagated
        read_platform_mock.return_value = error_action_result('Failed')
        read_temperature_mock.return_value = success_action_result(get_valid_temperature())
        read_throttle_mock.return_value = success_action_result(get_valid_throttle())
        read_uptime_mock.return_value = success_action_result(get_valid_uptime())
        read_frequency_mock.return_value = success_action_result(get_valid_frequency())
        read_memory_mock.return_value = success_action_result(get_valid_memory())
        response = self.client.get('/system')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': 'Failed'}, response_json)

        # Ensure valid system responses are returned
        system = get_valid_system()
        read_platform_mock.return_value = success_action_result(get_valid_platform())
        read_temperature_mock.return_value = success_action_result(get_valid_temperature())
        read_throttle_mock.return_value = success_action_result(get_valid_throttle())
        read_uptime_mock.return_value = success_action_result(get_valid_uptime())
        read_frequency_mock.return_value = success_action_result(get_valid_frequency())
        read_memory_mock.return_value = success_action_result(get_valid_memory())
        response = self.client.get('/system')
        response_json = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(system, response_json)

    @patch('endrpi.actions.system.system_platform')
    def test_get_platform_route(self, platform_mock):
        # Ensure validation errors are propagated
        with patch.object(Platform, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            response = self.client.get('/system/platform')
            response_json = json.loads(response.content)
            self.assertEqual(500, response.status_code)
            self.assertEqual({'message': PlatformMessage.ERROR_VALIDATION}, response_json)

        # Ensure valid platforms are returned
        platform = get_valid_platform()
        platform_mock.system.return_value = platform.operatingSystem.name
        platform_mock.release.return_value = platform.operatingSystem.release
        platform_mock.version.return_value = platform.operatingSystem.version
        platform_mock.machine.return_value = platform.machineType
        platform_mock.node.return_value = platform.networkName
        response = self.client.get('/system/platform')
        response_json = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(platform, response_json)

    @patch('endrpi.actions.system.process_output')
    def test_get_temperature_route(self, process_output_mock):
        # Ensure empty process output propagates an error
        process_output_mock.return_value = ''
        response = self.client.get('/system/temperature')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': TemperatureMessage.ERROR_SOC_QUERY}, response_json)

        # Ensure invalid process output propagates an error
        process_output_mock.return_value = 'qwerty'
        response = self.client.get('/system/temperature')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': TemperatureMessage.ERROR_SOC_PARSE}, response_json)

        # Ensure validation errors are propagated
        with patch.object(Temperature, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            process_output_mock.return_value = '1'
            response = self.client.get('/system/temperature')
            response_json = json.loads(response.content)
            self.assertEqual(500, response.status_code)
            self.assertEqual({'message': TemperatureMessage.ERROR_VALIDATION}, response_json)

        # Ensure valid temperatures are returned
        temperature = get_valid_temperature()
        process_output_mock.return_value = '20000'
        response = self.client.get('/system/temperature')
        response_json = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(temperature, response_json)

    @patch('endrpi.actions.system.process_output')
    @patch('endrpi.actions.system.int', wraps=int)
    def test_get_throttle_route(self, int_mock, process_output_mock):
        # Ensure empty process output propagates an error
        process_output_mock.return_value = ''
        response = self.client.get('/system/throttle')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': ThrottleMessage.ERROR_QUERY}, response_json)

        # Ensure invalid process output propagates an error
        process_output_mock.return_value = 'qwerty'
        response = self.client.get('/system/throttle')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': ThrottleMessage.ERROR_PARSE}, response_json)

        process_output_mock.return_value = 'throttled=0x12345'
        int_mock.side_effect = ValueError('Conversion error')
        response = self.client.get('/system/throttle')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': ThrottleMessage.ERROR_PARSE}, response_json)
        int_mock.side_effect = None

        # Ensure validation errors are propagated
        with patch.object(Throttle, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            process_output_mock.return_value = 'throttled=0x12345'
            response = self.client.get('/system/throttle')
            response_json = json.loads(response.content)
            self.assertEqual(500, response.status_code)
            self.assertEqual({'message': ThrottleMessage.ERROR_VALIDATION}, response_json)

        # Ensure valid throttles are returned
        throttle = get_valid_throttle()
        process_output_mock.return_value = 'throttled=0xE000D'
        response = self.client.get('/system/throttle')
        response_json = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(throttle, response_json)

    @patch('endrpi.actions.system.process_output')
    @patch('endrpi.actions.system.float', wraps=float)
    def test_get_uptime_route(self, float_mock, process_output_mock):
        # Ensure empty process output propagates an error
        process_output_mock.return_value = ''
        response = self.client.get('/system/uptime')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': UpTimeMessage.ERROR_QUERY}, response_json)

        # Ensure invalid process output propagates an error
        process_output_mock.return_value = 'qwerty'
        response = self.client.get('/system/uptime')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': UpTimeMessage.ERROR_PARSE}, response_json)

        process_output_mock.return_value = '1234 5'
        float_mock.side_effect = ValueError('Conversion error')
        response = self.client.get('/system/uptime')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': UpTimeMessage.ERROR_PARSE}, response_json)
        float_mock.side_effect = None

        # Ensure validation errors are propagated
        with patch.object(UpTime, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            process_output_mock.return_value = '1234 5'
            response = self.client.get('/system/uptime')
            response_json = json.loads(response.content)
            self.assertEqual(500, response.status_code)
            self.assertEqual({'message': UpTimeMessage.ERROR_VALIDATION}, response_json)

        # Ensure valid uptime responses are returned
        uptime = get_valid_uptime()
        process_output_mock.return_value = '123456 123456'
        response = self.client.get('/system/uptime')
        response_json = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(uptime, response_json)

    @patch('endrpi.actions.system.process_output')
    @patch('endrpi.actions.system.float', wraps=float)
    def test_get_frequency_route(self, float_mock, process_output_mock):
        # Ensure empty process output propagates an error
        process_output_mock.side_effect = [None, 'core frequency']
        response = self.client.get('/system/frequency')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': FrequencyMessage.ERROR_ARM_QUERY}, response_json)

        process_output_mock.side_effect = ['arm frequency', None]
        response = self.client.get('/system/frequency')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': FrequencyMessage.ERROR_CORE_QUERY}, response_json)

        # Ensure invalid process output propagates an error
        process_output_mock.side_effect = ['frequency(45)=', 'frequency(1)=']
        response = self.client.get('/system/frequency')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': FrequencyMessage.ERROR_PARSE}, response_json)

        process_output_mock.side_effect = ['frequency(45)=600000', 'frequency(1)=400000']
        float_mock.side_effect = [ValueError('Conversion error'), 1234]
        response = self.client.get('/system/frequency')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': FrequencyMessage.ERROR_PARSE}, response_json)
        float_mock.side_effect = None

        process_output_mock.side_effect = ['frequency(45)=600000', 'frequency(1)=400000']
        float_mock.side_effect = [1234, ValueError('Conversion error')]
        response = self.client.get('/system/frequency')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': FrequencyMessage.ERROR_PARSE}, response_json)
        float_mock.side_effect = None

        # Ensure validation errors are propagated
        with patch.object(Frequency, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            process_output_mock.side_effect = ['frequency(45)=600000', 'frequency(1)=500000']
            response = self.client.get('/system/frequency')
            response_json = json.loads(response.content)
            self.assertEqual(500, response.status_code)
            self.assertEqual({'message': FrequencyMessage.ERROR_VALIDATION}, response_json)

        # Ensure valid frequency responses are returned
        frequency = get_valid_frequency()
        process_output_mock.side_effect = ['frequency(45)=600000', 'frequency(1)=500000']
        response = self.client.get('/system/frequency')
        response_json = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(frequency, response_json)

    @patch('endrpi.actions.system.process_output')
    @patch('endrpi.actions.system.int', wraps=int)
    def test_get_memory_route(self, int_mock, process_output_mock):
        # Ensure empty process output propagates an error
        process_output_mock.return_value = ''
        response = self.client.get('/system/memory')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': MemoryMessage.ERROR_QUERY}, response_json)

        # Ensure invalid process output propagates an error
        process_output_mock.return_value = 'qwerty'
        response = self.client.get('/system/memory')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': MemoryMessage.ERROR_PARSE}, response_json)

        process_output_mock.return_value = 'MemTotal: 1 kB ' \
                                           'MemFree: 1 kB ' \
                                           'MemAvailable: 1 kB'
        int_mock.side_effect = ValueError('Conversion error')
        response = self.client.get('/system/memory')
        response_json = json.loads(response.content)
        self.assertEqual(500, response.status_code)
        self.assertEqual({'message': MemoryMessage.ERROR_PARSE}, response_json)
        int_mock.side_effect = None

        # Ensure validation errors are propagated
        with patch.object(Memory, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            process_output_mock.return_value = 'MemTotal: 1 kB ' \
                                               'MemFree: 1 kB ' \
                                               'MemAvailable: 1 kB'
            response = self.client.get('/system/memory')
            response_json = json.loads(response.content)
            self.assertEqual(500, response.status_code)
            self.assertEqual({'message': MemoryMessage.ERROR_VALIDATION}, response_json)

        # Ensure valid memory responses are returned
        memory = get_valid_memory()
        process_output_mock.return_value = 'MemTotal: 4000 kB ' \
                                           'MemFree: 100 kB ' \
                                           'MemAvailable: 200 kB'
        response = self.client.get('/system/memory')
        response_json = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(memory, response_json)


if __name__ == '__main__':
    unittest.main()
