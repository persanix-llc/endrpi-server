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
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from gpiozero import PinUnsupported, Device
from gpiozero.pins.mock import MockFactory

from endrpi.model.measurement import TemperatureUnit, FrequencyUnit, UnitPrefix, InformationUnit
from endrpi.model.message import WebSocketMessage, TemperatureMessage, ThrottleMessage, UpTimeMessage, \
    FrequencyMessage, MemoryMessage, PinMessage
from endrpi.model.pin import PinIo, PinPull, RaspberryPiPinIds
from endrpi.model.websocket import WebSocketAction
from endrpi.server import app


class TestWebsocketRoutes(TestCase):

    def setUp(self) -> None:
        super().setUp()

        # Setup the fast api testing client
        self.client = TestClient(app)

        # Websocket client doesn't close its event loop in __exit__ resulting in a resource warning
        def close_websocket_test_client(websocket):
            websocket.close(1000)
            websocket._thread.join()
            websocket._loop.close()

        self.close_websocket_test_client = close_websocket_test_client

        Device.pin_factory = MockFactory()

    def test_message_decode(self):
        with self.client.websocket_connect("/") as websocket:
            websocket.send_text('not json')
            response = websocket.receive_json()
            self.assertIsNone(response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': WebSocketMessage.ERROR_INVALID_DATA}, response['error'])

            # Ensure the websocket client is closed
            self.close_websocket_test_client(websocket)

    def test_invalid_action(self):
        with self.client.websocket_connect("/") as websocket:
            websocket.send_json({})
            response = websocket.receive_json()
            self.assertIsNone(response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': WebSocketMessage.ERROR_MISSING_ACTION_FIELD}, response['error'])

            websocket.send_json({'params': {'sample': 'params'}})
            response = websocket.receive_json()
            self.assertIsNone(response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': WebSocketMessage.ERROR_MISSING_ACTION_FIELD}, response['error'])

            websocket.send_json({'action': 'INVALID_ACTION'})
            response = websocket.receive_json()
            self.assertIsNone(response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': WebSocketMessage.ERROR_INVALID_ACTION_FIELD}, response['error'])

            # Ensure the websocket client is closed
            self.close_websocket_test_client(websocket)

    @patch('endrpi.routes.websocket.validate_websocket_action')
    def test_unknown_action(self, validate_websocket_action_mock):
        with self.client.websocket_connect("/") as websocket:
            validate_websocket_action_mock.return_value.value = 'FAKE_VALID_ACTION'
            websocket.send_json({'action': 'FAKE_VALID_ACTION'})
            response = websocket.receive_json()
            self.assertEqual('FAKE_VALID_ACTION', response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': WebSocketMessage.ERROR_UNKNOWN_ACTION_VALUE}, response['error'])
            self.assertIsNone(response['data'])

            # Ensure the websocket client is closed
            self.close_websocket_test_client(websocket)

    @patch('endrpi.actions.system.process_output')
    def test_read_temperature_action(self, process_output_mock):
        with self.client.websocket_connect("/") as websocket:
            process_output_mock.return_value = 'qwerty'
            websocket.send_json({'action': WebSocketAction.READ_TEMPERATURE})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_TEMPERATURE, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': TemperatureMessage.ERROR_SOC_PARSE}, response['error'])
            self.assertIsNone(response['data'])

            process_output_mock.return_value = '123456'
            websocket.send_json({'action': WebSocketAction.READ_TEMPERATURE})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_TEMPERATURE, response['action'])
            self.assertTrue(response['success'])
            self.assertIsNone(response['error'])
            self.assertEqual(123.456, response['data']['systemOnChip']['quantity'])
            self.assertEqual(TemperatureUnit.CELSIUS, response['data']['systemOnChip']['unitOfMeasurement'])

            # Ensure the websocket client is closed
            self.close_websocket_test_client(websocket)

    @patch('endrpi.actions.system.process_output')
    def test_read_throttle_action(self, process_output_mock):
        with self.client.websocket_connect("/") as websocket:
            process_output_mock.return_value = 'qwerty'
            websocket.send_json({'action': WebSocketAction.READ_THROTTLE})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_THROTTLE, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': ThrottleMessage.ERROR_PARSE}, response['error'])
            self.assertIsNone(response['data'])

            process_output_mock.return_value = 'throttled=0xF000F'
            websocket.send_json({'action': WebSocketAction.READ_THROTTLE})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_THROTTLE, response['action'])
            self.assertTrue(response['success'])
            self.assertIsNone(response['error'])
            self.assertTrue(response['data']['throttling'])
            self.assertTrue(response['data']['throttlingHasOccurred'])
            self.assertTrue(response['data']['underVoltageDetected'])
            self.assertTrue(response['data']['underVoltageHasOccurred'])
            self.assertTrue(response['data']['armFrequencyCapped'])
            self.assertTrue(response['data']['armFrequencyCappingHasOccurred'])
            self.assertTrue(response['data']['softTemperatureLimitActive'])
            self.assertTrue(response['data']['softTemperatureLimitHasOccurred'])

            # Ensure the websocket client is closed
            self.close_websocket_test_client(websocket)

    @patch('endrpi.actions.system.process_output')
    def test_read_uptime_action(self, process_output_mock):
        with self.client.websocket_connect("/") as websocket:
            process_output_mock.return_value = 'qwerty'
            websocket.send_json({'action': WebSocketAction.READ_UPTIME})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_UPTIME, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': UpTimeMessage.ERROR_PARSE}, response['error'])
            self.assertIsNone(response['data'])

            process_output_mock.return_value = '1234 5'
            websocket.send_json({'action': WebSocketAction.READ_UPTIME})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_UPTIME, response['action'])
            self.assertTrue(response['success'])
            self.assertIsNone(response['error'])
            self.assertEqual(1234, response['data']['seconds'])
            self.assertEqual('0:20:34', response['data']['formatted'])

            # Ensure the websocket client is closed
            self.close_websocket_test_client(websocket)

    @patch('endrpi.actions.system.process_output')
    def test_read_frequency_action(self, process_output_mock):
        with self.client.websocket_connect("/") as websocket:
            process_output_mock.side_effect = ['qwerty', 'qwerty']
            websocket.send_json({'action': WebSocketAction.READ_FREQUENCY})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_FREQUENCY, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': FrequencyMessage.ERROR_PARSE}, response['error'])
            self.assertIsNone(response['data'])

            process_output_mock.side_effect = ['frequency(45)=600000', 'frequency(1)=400000']
            websocket.send_json({'action': WebSocketAction.READ_FREQUENCY})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_FREQUENCY, response['action'])
            self.assertTrue(response['success'])
            self.assertIsNone(response['error'])
            self.assertEqual(600000, response['data']['arm']['quantity'])
            self.assertIsNone(response['data']['arm']['prefix'])
            self.assertEqual(FrequencyUnit.HERTZ, response['data']['arm']['unitOfMeasurement'])
            self.assertEqual(400000, response['data']['core']['quantity'])
            self.assertIsNone(response['data']['core']['prefix'])
            self.assertEqual(FrequencyUnit.HERTZ, response['data']['core']['unitOfMeasurement'])

            # Ensure the websocket client is closed
            self.close_websocket_test_client(websocket)

    @patch('endrpi.actions.system.process_output')
    def test_read_memory_action(self, process_output_mock):
        with self.client.websocket_connect("/") as websocket:
            process_output_mock.return_value = 'qwerty'
            websocket.send_json({'action': WebSocketAction.READ_MEMORY})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_MEMORY, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': MemoryMessage.ERROR_PARSE}, response['error'])
            self.assertIsNone(response['data'])

            process_output_mock.return_value = 'MemTotal: 012 kB ' \
                                               'MemFree: 340 kB ' \
                                               'MemAvailable: 0560 kB'
            websocket.send_json({'action': WebSocketAction.READ_MEMORY})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_MEMORY, response['action'])
            self.assertTrue(response['success'])
            self.assertIsNone(response['error'])
            self.assertEqual(12.0, response['data']['total']['quantity'])
            self.assertEqual(UnitPrefix.KILO, response['data']['total']['prefix'])
            self.assertEqual(InformationUnit.BYTE, response['data']['total']['unitOfMeasurement'])
            self.assertEqual(340.0, response['data']['free']['quantity'])
            self.assertEqual(UnitPrefix.KILO, response['data']['free']['prefix'])
            self.assertEqual(InformationUnit.BYTE, response['data']['free']['unitOfMeasurement'])
            self.assertEqual(560.0, response['data']['available']['quantity'])
            self.assertEqual(UnitPrefix.KILO, response['data']['available']['prefix'])
            self.assertEqual(InformationUnit.BYTE, response['data']['available']['unitOfMeasurement'])

            # Ensure the websocket client is closed
            self.close_websocket_test_client(websocket)

    @patch('endrpi.actions.pin.Device')
    def test_read_pin_configurations_action(self, gpiozero_device_mock):
        with self.client.websocket_connect("/") as websocket:
            # Ensure invalid param errors are propagated
            websocket.send_json({'action': WebSocketAction.READ_PIN_CONFIGURATIONS})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_PIN_CONFIGURATIONS, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': WebSocketMessage.ERROR_MISSING_PARAMS_FIELD}, response['error'])
            self.assertIsNone(response['data'])

            websocket.send_json({'action': WebSocketAction.READ_PIN_CONFIGURATIONS,
                                 'params': {'pins': ['INVALID_PIN_ID']}})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_PIN_CONFIGURATIONS, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': WebSocketMessage.ERROR_INVALID_PARAMS_FIELD}, response['error'])
            self.assertIsNone(response['data'])

            # Ensure successful pin actions respond with correct json
            pin_mock = MagicMock()
            pin_mock.function = PinIo.OUTPUT
            pin_mock.state = 1
            pin_mock.pull = PinPull.FLOATING
            gpiozero_device_mock.pin_factory.pin.return_value = pin_mock
            websocket.send_json({'action': WebSocketAction.READ_PIN_CONFIGURATIONS,
                                 'params': {'pins': list(RaspberryPiPinIds)}})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.READ_PIN_CONFIGURATIONS, response['action'])
            self.assertTrue(response['success'])
            self.assertIsNone(response['error'])
            available_pin_ids = list(RaspberryPiPinIds)
            for pin_id, pin_configuration in response['data'].items():
                valid_pin = RaspberryPiPinIds.from_bcm_id(pin_id)
                self.assertIn(pin_id, available_pin_ids)
                self.assertIsNotNone(valid_pin)
                self.assertEqual(PinIo.OUTPUT, pin_configuration['io'])
                self.assertEqual(1, pin_configuration['state'])
                self.assertEqual(PinPull.FLOATING, pin_configuration['pull'])
                available_pin_ids.remove(pin_id)

            # Ensure the websocket client is closed
            self.close_websocket_test_client(websocket)

    @patch('endrpi.actions.pin.Device')
    def test_update_pin_configurations_action(self, gpiozero_device_mock):
        with self.client.websocket_connect("/") as websocket:
            # Ensure invalid param errors are propagated
            websocket.send_json({'action': WebSocketAction.UPDATE_PIN_CONFIGURATIONS})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.UPDATE_PIN_CONFIGURATIONS, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': WebSocketMessage.ERROR_MISSING_PARAMS_FIELD}, response['error'])
            self.assertIsNone(response['data'])

            websocket.send_json({'action': WebSocketAction.UPDATE_PIN_CONFIGURATIONS,
                                 'params': {'INVALID': {}}})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.UPDATE_PIN_CONFIGURATIONS, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': WebSocketMessage.ERROR_INVALID_PARAMS_FIELD}, response['error'])
            self.assertIsNone(response['data'])

            websocket.send_json({'action': WebSocketAction.UPDATE_PIN_CONFIGURATIONS,
                                 'params': {'pins': {}}})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.UPDATE_PIN_CONFIGURATIONS, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': WebSocketMessage.ERROR_MISSING_PIN_ID}, response['error'])
            self.assertIsNone(response['data'])

            websocket.send_json({'action': WebSocketAction.UPDATE_PIN_CONFIGURATIONS,
                                 'params': {
                                     'pins': {
                                         'INVALID_PIN_ID': {'io': PinIo.OUTPUT}
                                     }
                                 }})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.UPDATE_PIN_CONFIGURATIONS, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({'message': WebSocketMessage.ERROR_INVALID_PARAMS_FIELD}, response['error'])
            self.assertIsNone(response['data'])

            gpiozero_device_mock.pin_factory.pin.side_effect = PinUnsupported('Error')
            websocket.send_json({'action': WebSocketAction.UPDATE_PIN_CONFIGURATIONS,
                                 'params': {
                                     'pins': {
                                         RaspberryPiPinIds.GPIO17: {'io': PinIo.OUTPUT, 'state': 1}
                                     }
                                 }})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.UPDATE_PIN_CONFIGURATIONS, response['action'])
            self.assertFalse(response['success'])
            self.assertEqual({
                'message': PinMessage.ERROR_UNSUPPORTED__PIN_ID__.format(pin_id=RaspberryPiPinIds.GPIO17)},
                response['error'])
            self.assertIsNone(response['data'])
            gpiozero_device_mock.pin_factory.pin.side_effect = None

            # Ensure successful pin actions respond with correct json
            pin_mock = MagicMock()
            gpiozero_device_mock.pin_factory.pin.return_value = pin_mock
            websocket.send_json({'action': WebSocketAction.UPDATE_PIN_CONFIGURATIONS,
                                 'params': {
                                     'pins': {
                                         RaspberryPiPinIds.GPIO17: {'io': PinIo.OUTPUT, 'state': 1}
                                     }
                                 }})
            response = websocket.receive_json()
            self.assertEqual(WebSocketAction.UPDATE_PIN_CONFIGURATIONS, response['action'])
            self.assertTrue(response['success'])
            self.assertIsNone(response['error'])
            self.assertEqual(WebSocketMessage.SUCCESS_PIN_CONFIGS_UPDATED, response['data'])
            self.assertEqual(PinIo.OUTPUT.name.lower(), pin_mock.function)
            self.assertEqual(1, pin_mock.state)
            self.assertIsInstance(pin_mock.pull, MagicMock)

            # Ensure the websocket client is closed
            self.close_websocket_test_client(websocket)


if __name__ == '__main__':
    unittest.main()
