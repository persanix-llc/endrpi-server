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

from gpiozero import Device, PinUnsupported
from gpiozero.pins.mock import MockFactory
from pydantic import ValidationError, BaseModel

from endrpi.actions.pin import read_pin_configurations, read_pin_configuration, update_pin_configuration
from endrpi.model.message import MessageData, PinMessage
from endrpi.model.pin import PinIo, PinPull, RaspberryPiPinIds, PinConfiguration


class TestPinActions(TestCase):

    def setUp(self) -> None:
        super().setUp()

        Device.pin_factory = MockFactory()

    @patch('endrpi.actions.pin.Device.pin_factory.pin')
    def test_read_pin_configurations(self, gpiozero_pin_mock):
        # Ensure pin config read errors are propagated to the result
        pin_ids = list(RaspberryPiPinIds)
        gpiozero_pin_mock.side_effect = PinUnsupported('Pin not supported')
        action_result = read_pin_configurations(pin_ids)
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({
            'message': PinMessage.ERROR_UNSUPPORTED__PIN_ID__.format(pin_id=pin_ids[0])
        }, action_result.error)
        gpiozero_pin_mock.side_effect = None

        # Ensure validation errors are propagated
        with patch.object(PinConfiguration, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            pin_ids = list(RaspberryPiPinIds)
            pin_mock = MagicMock()
            pin_mock.function = PinIo.OUTPUT
            pin_mock.state = 1
            pin_mock.pull = PinPull.FLOATING
            gpiozero_pin_mock.return_value = pin_mock
            action_result = read_pin_configurations(pin_ids)
            self.assertFalse(action_result.success)
            self.assertIsNone(action_result.data)
            self.assertEqual({'message': PinMessage.ERROR_VALIDATION}, action_result.error)

        # Ensure floating output pin configurations can be read for all pins
        pin_ids = list(RaspberryPiPinIds)
        pin_mock = MagicMock()
        pin_mock.function = PinIo.OUTPUT
        pin_mock.state = 1
        pin_mock.pull = PinPull.FLOATING
        gpiozero_pin_mock.return_value = pin_mock
        action_result = read_pin_configurations(pin_ids)
        self.assertTrue(action_result.success)
        self.assertEqual(len(list(RaspberryPiPinIds)), len(action_result.data.keys()))
        self.assertIsNone(action_result.error)
        for pin_id in pin_ids:
            self.assertIn(pin_id, action_result.data)
            self.assertEqual(PinIo.OUTPUT, action_result.data[pin_id].io)
            self.assertEqual(1, action_result.data[pin_id].state)
            self.assertEqual(PinPull.FLOATING, action_result.data[pin_id].pull)

        # Ensure pulled-up input pin configurations can be read for all pins
        pin_ids = list(RaspberryPiPinIds)
        pin_mock = MagicMock()
        pin_mock.function = PinIo.INPUT
        pin_mock.state = 0
        pin_mock.pull = PinPull.UP
        gpiozero_pin_mock.return_value = pin_mock
        action_result = read_pin_configurations(pin_ids)
        self.assertTrue(action_result.success)
        self.assertEqual(len(list(RaspberryPiPinIds)), len(action_result.data.keys()))
        self.assertIsNone(action_result.error)
        for pin_id in pin_ids:
            self.assertIn(pin_id, action_result.data)
            self.assertEqual(PinIo.INPUT, action_result.data[pin_id].io)
            self.assertEqual(0, action_result.data[pin_id].state)
            self.assertEqual(PinPull.UP, action_result.data[pin_id].pull)

        # Ensure no pin configurations queried results in an empty result
        pin_ids = []
        pin_mock = MagicMock()
        pin_mock.function = PinIo.INPUT
        pin_mock.state = 0
        pin_mock.pull = PinPull.UP
        gpiozero_pin_mock.return_value = pin_mock
        action_result = read_pin_configurations(pin_ids)
        self.assertTrue(action_result.success)
        self.assertEqual(0, len(action_result.data.keys()))
        self.assertIsNone(action_result.error)
        pin_mock.assert_not_called()

    @patch('endrpi.actions.pin.Device.pin_factory.pin')
    def test_read_pin_configuration(self, gpiozero_pin_mock):
        # Ensure pin config read errors are propagated
        gpiozero_pin_mock.side_effect = PinUnsupported('Pin not supported')
        action_result = read_pin_configuration(RaspberryPiPinIds.GPIO17)
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': PinMessage.ERROR_UNSUPPORTED__PIN_ID__.format(pin_id=RaspberryPiPinIds.GPIO17)},
                         action_result.error)
        gpiozero_pin_mock.side_effect = None

        # Ensure validation errors are propagated
        with patch.object(PinConfiguration, '__init__', side_effect=ValidationError(['Failed validation'], BaseModel)):
            pin_mock = MagicMock()
            pin_mock.function = PinIo.OUTPUT
            pin_mock.state = 1
            pin_mock.pull = PinPull.FLOATING
            gpiozero_pin_mock.return_value = pin_mock
            action_result = read_pin_configuration(RaspberryPiPinIds.GPIO2)
            self.assertFalse(action_result.success)
            self.assertIsNone(action_result.data)
            self.assertEqual({'message': PinMessage.ERROR_VALIDATION}, action_result.error)

        # Ensure floating output pin config can be read for an arbitrary pin
        pin_mock = MagicMock()
        pin_mock.function = PinIo.OUTPUT
        pin_mock.state = 1
        pin_mock.pull = PinPull.FLOATING
        gpiozero_pin_mock.return_value = pin_mock
        action_result = read_pin_configuration(RaspberryPiPinIds.GPIO2)
        self.assertTrue(action_result.success)
        self.assertEqual(PinIo.OUTPUT, action_result.data.io)
        self.assertEqual(1, action_result.data.state)
        self.assertEqual(PinPull.FLOATING, action_result.data.pull)
        self.assertIsNone(action_result.error)

        # Ensure pulled-down input pin config can be read for an arbitrary pin
        pin_mock = MagicMock()
        pin_mock.function = PinIo.INPUT
        pin_mock.state = 0
        pin_mock.pull = PinPull.DOWN
        gpiozero_pin_mock.return_value = pin_mock
        action_result = read_pin_configuration(RaspberryPiPinIds.GPIO27)
        self.assertTrue(action_result.success)
        self.assertEqual(PinIo.INPUT, action_result.data.io)
        self.assertEqual(0, action_result.data.state)
        self.assertEqual(PinPull.DOWN, action_result.data.pull)
        self.assertIsNone(action_result.error)

    @patch('endrpi.actions.pin.Device.pin_factory.pin')
    def test_update_pin_configuration(self, gpiozero_pin_mock):
        # Ensure unknown pin errors are propagated
        gpiozero_pin_mock.side_effect = PinUnsupported('Pin not supported')
        pin_configuration = PinConfiguration(io=PinIo.INPUT, state=1, pull=PinPull.UP)
        action_result = update_pin_configuration(RaspberryPiPinIds.GPIO17, pin_configuration)
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertEqual({'message': PinMessage.ERROR_UNSUPPORTED__PIN_ID__.format(pin_id=RaspberryPiPinIds.GPIO17)},
                         action_result.error)
        gpiozero_pin_mock.side_effect = None

        # Ensure missing parameter errors are propagated
        gpiozero_pin_mock.return_value = MagicMock()
        pin_configuration = PinConfiguration(io=PinIo.INPUT)
        action_result = update_pin_configuration(RaspberryPiPinIds.GPIO17, pin_configuration)
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertIsInstance(gpiozero_pin_mock().function, MagicMock)
        self.assertIsInstance(gpiozero_pin_mock().state, MagicMock)
        self.assertIsInstance(gpiozero_pin_mock().pull, MagicMock)
        self.assertEqual({'message': PinMessage.ERROR_NO_INPUT_PULL}, action_result.error)

        gpiozero_pin_mock.return_value = MagicMock()
        pin_configuration = PinConfiguration(io=PinIo.OUTPUT)
        action_result = update_pin_configuration(RaspberryPiPinIds.GPIO17, pin_configuration)
        self.assertFalse(action_result.success)
        self.assertIsNone(action_result.data)
        self.assertIsInstance(gpiozero_pin_mock().function, MagicMock)
        self.assertIsInstance(gpiozero_pin_mock().state, MagicMock)
        self.assertIsInstance(gpiozero_pin_mock().pull, MagicMock)
        self.assertEqual({'message': PinMessage.ERROR_NO_OUTPUT_STATE}, action_result.error)

        # Ensure valid parameters are correctly set
        gpiozero_pin_mock.return_value = MagicMock()
        pin_configuration = PinConfiguration(io=PinIo.INPUT, state=1, pull=PinPull.UP)
        action_result = update_pin_configuration(RaspberryPiPinIds.GPIO17, pin_configuration)
        self.assertTrue(action_result.success)
        self.assertEqual(
            MessageData(message=PinMessage.SUCCESS_UPDATED__PIN_ID__.format(pin_id=RaspberryPiPinIds.GPIO17)),
            action_result.data)
        self.assertEqual(PinIo.INPUT.lower(), gpiozero_pin_mock().function)
        self.assertIsInstance(gpiozero_pin_mock().state, MagicMock)
        self.assertEqual(PinPull.UP.lower(), gpiozero_pin_mock().pull)
        self.assertIsNone(action_result.error)

        gpiozero_pin_mock.return_value = MagicMock()
        pin_configuration = PinConfiguration(io=PinIo.INPUT, state=0, pull=PinPull.DOWN)
        action_result = update_pin_configuration(RaspberryPiPinIds.GPIO17, pin_configuration)
        self.assertTrue(action_result.success)
        self.assertEqual(
            MessageData(message=PinMessage.SUCCESS_UPDATED__PIN_ID__.format(pin_id=RaspberryPiPinIds.GPIO17)),
            action_result.data)
        self.assertEqual(PinIo.INPUT.lower(), gpiozero_pin_mock().function)
        self.assertIsInstance(gpiozero_pin_mock().state, MagicMock)
        self.assertEqual(PinPull.DOWN.lower(), gpiozero_pin_mock().pull)
        self.assertIsNone(action_result.error)

        gpiozero_pin_mock.return_value = MagicMock()
        pin_configuration = PinConfiguration(io=PinIo.OUTPUT, state=0, pull=PinPull.DOWN)
        action_result = update_pin_configuration(RaspberryPiPinIds.GPIO17, pin_configuration)
        self.assertTrue(action_result.success)
        self.assertEqual(
            MessageData(message=PinMessage.SUCCESS_UPDATED__PIN_ID__.format(pin_id=RaspberryPiPinIds.GPIO17)),
            action_result.data)
        self.assertEqual(PinIo.OUTPUT.lower(), gpiozero_pin_mock().function)
        self.assertEqual(0, gpiozero_pin_mock().state)
        self.assertIsInstance(gpiozero_pin_mock().pull, MagicMock)
        self.assertIsNone(action_result.error)

        gpiozero_pin_mock.return_value = MagicMock()
        pin_configuration = PinConfiguration(io=PinIo.OUTPUT, state=1, pull=PinPull.FLOATING)
        action_result = update_pin_configuration(RaspberryPiPinIds.GPIO17, pin_configuration)
        self.assertTrue(action_result.success)
        self.assertEqual(
            MessageData(message=PinMessage.SUCCESS_UPDATED__PIN_ID__.format(pin_id=RaspberryPiPinIds.GPIO17)),
            action_result.data)
        self.assertEqual(PinIo.OUTPUT.lower(), gpiozero_pin_mock().function)
        self.assertEqual(1, gpiozero_pin_mock().state)
        self.assertIsInstance(gpiozero_pin_mock().pull, MagicMock)
        self.assertIsNone(action_result.error)


if __name__ == '__main__':
    unittest.main()
