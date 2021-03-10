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
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from gpiozero import Device
from gpiozero.pins.mock import MockFactory
from pydantic import ValidationError, BaseModel

from endrpi.model.message import PinMessage
from endrpi.model.pin import PinConfiguration, PinIo, PinPull, RaspberryPiPinIds
from endrpi.server import app


class TestPinRoutes(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.client = TestClient(app)

        Device.pin_factory = MockFactory()

    @patch('endrpi.actions.pin.Device')
    def test_get_pin_configurations_route(self, gpiozero_device_mock):
        # Ensure validation errors are propagated
        with patch.object(PinConfiguration, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            pin_mock = MagicMock()
            pin_mock.function = PinIo.OUTPUT
            pin_mock.state = 1
            pin_mock.pull = PinPull.FLOATING
            gpiozero_device_mock.pin_factory.pin.return_value = pin_mock
            response = self.client.get('/pins')
            response_json = json.loads(response.content)
            self.assertEqual(500, response.status_code)
            self.assertEqual({'message': PinMessage.ERROR_VALIDATION}, response_json)

        # Ensure successful pin actions respond with correct json
        pin_mock = MagicMock()
        pin_mock.function = PinIo.OUTPUT
        pin_mock.state = 1
        pin_mock.pull = PinPull.FLOATING
        gpiozero_device_mock.pin_factory.pin.return_value = pin_mock
        response = self.client.get('/pins')
        response_json = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        available_pin_ids = list(RaspberryPiPinIds)
        for pin_id, pin_configuration in response_json.items():
            valid_pin = RaspberryPiPinIds.from_bcm_id(pin_id)
            self.assertIn(pin_id, available_pin_ids)
            self.assertIsNotNone(valid_pin)
            self.assertEqual(PinIo.OUTPUT, pin_configuration['io'])
            self.assertEqual(1, pin_configuration['state'])
            self.assertEqual(PinPull.FLOATING, pin_configuration['pull'])
            available_pin_ids.remove(pin_id)

    @patch('endrpi.actions.pin.Device')
    def test_get_pin_configuration_route(self, gpiozero_device_mock):
        # Ensure unknown pin errors are propagated
        pin_mock = MagicMock()
        pin_mock.function = PinIo.OUTPUT
        pin_mock.state = 1
        pin_mock.pull = PinPull.FLOATING
        gpiozero_device_mock.pin_factory.pin.return_value = pin_mock
        pin_id = '9999999'
        response = self.client.get(f'/pins/{pin_id}')
        response_json = json.loads(response.content)
        self.assertEqual(404, response.status_code)
        self.assertEqual({'message': PinMessage.ERROR_NOT_FOUND__PIN_ID__.format(pin_id=pin_id)}, response_json)

        # Ensure validation errors are propagated
        with patch.object(PinConfiguration, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            pin_mock = MagicMock()
            pin_mock.function = PinIo.OUTPUT
            pin_mock.state = 1
            pin_mock.pull = PinPull.FLOATING
            gpiozero_device_mock.pin_factory.pin.return_value = pin_mock
            pin_id = RaspberryPiPinIds.GPIO17
            response = self.client.get(f'/pins/{pin_id}')
            response_json = json.loads(response.content)
            self.assertEqual(500, response.status_code)
            self.assertEqual({'message': PinMessage.ERROR_VALIDATION}, response_json)

        # Ensure successful pin actions respond with correct json
        pin_mock = MagicMock()
        pin_mock.function = PinIo.OUTPUT
        pin_mock.state = 1
        pin_mock.pull = PinPull.FLOATING
        gpiozero_device_mock.pin_factory.pin.return_value = pin_mock
        pin_id = RaspberryPiPinIds.GPIO17
        response = self.client.get(f'/pins/{pin_id}')
        response_json = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual(PinIo.OUTPUT, response_json['io'])
        self.assertEqual(1, response_json['state'])
        self.assertEqual(PinPull.FLOATING, response_json['pull'])

    @patch('endrpi.actions.pin.Device')
    def test_put_pin_configuration_route(self, gpiozero_device_mock):
        # Ensure unknown pin errors are propagated
        pin_id = '9999999'
        pin_configuration = PinConfiguration(io=PinIo.OUTPUT, state=1.0, pull=PinPull.FLOATING)
        response = self.client.put(f'/pins/{pin_id}', json.dumps(pin_configuration.__dict__))
        response_json = json.loads(response.content)
        self.assertEqual(404, response.status_code)
        self.assertEqual({'message': PinMessage.ERROR_NOT_FOUND__PIN_ID__.format(pin_id=pin_id)}, response_json)

        # Ensure bad put body errors are propagated
        pin_id = RaspberryPiPinIds.GPIO17
        response = self.client.put(f'/pins/{pin_id}')
        self.assertEqual(400, response.status_code)

        pin_id = RaspberryPiPinIds.GPIO17
        pin_configuration = PinConfiguration(io=PinIo.INPUT)
        response = self.client.put(f'/pins/{pin_id}', json.dumps(pin_configuration.__dict__))
        response_json = json.loads(response.content)
        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': PinMessage.ERROR_NO_INPUT_PULL}, response_json)

        pin_id = RaspberryPiPinIds.GPIO17
        pin_configuration = PinConfiguration(io=PinIo.OUTPUT)
        response = self.client.put(f'/pins/{pin_id}', json.dumps(pin_configuration.__dict__))
        response_json = json.loads(response.content)
        self.assertEqual(400, response.status_code)
        self.assertEqual({'message': PinMessage.ERROR_NO_OUTPUT_STATE}, response_json)

        # Ensure successful pin actions respond with correct json
        pin_mock = MagicMock()
        gpiozero_device_mock.pin_factory.pin.return_value = pin_mock
        pin_id = RaspberryPiPinIds.GPIO17
        pin_configuration = PinConfiguration(io=PinIo.OUTPUT, state=1.0)
        response = self.client.put(f'/pins/{pin_id}', json.dumps(pin_configuration.__dict__))
        response_json = json.loads(response.content)
        self.assertEqual(200, response.status_code)
        self.assertEqual({'message': PinMessage.SUCCESS_UPDATED__PIN_ID__.format(pin_id=pin_id)}, response_json)
        self.assertEqual(PinIo.OUTPUT.name.lower(), pin_mock.function)
        self.assertEqual(1, pin_mock.state)
        self.assertIsInstance(pin_mock.pull, MagicMock)

        pin_mock = MagicMock()
        gpiozero_device_mock.pin_factory.pin.return_value = pin_mock
        pin_id = RaspberryPiPinIds.GPIO17
        pin_configuration = PinConfiguration(io=PinIo.INPUT, pull=PinPull.FLOATING)
        response = self.client.put(f'/pins/{pin_id}', json.dumps(pin_configuration.__dict__))
        self.assertEqual(200, response.status_code)
        self.assertEqual({'message': PinMessage.SUCCESS_UPDATED__PIN_ID__.format(pin_id=pin_id)}, response_json)
        self.assertEqual(PinIo.INPUT.name.lower(), pin_mock.function)
        self.assertIsInstance(pin_mock.state, MagicMock)
        self.assertEqual(PinPull.FLOATING.name.lower(), pin_mock.pull)


if __name__ == '__main__':
    unittest.main()
