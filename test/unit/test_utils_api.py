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

from fastapi import status
from fastapi.responses import JSONResponse

from endrpi.model.action_result import success_action_result, error_action_result
from endrpi.model.message import MessageData
from endrpi.model.websocket import WebSocketAction
from endrpi.utils.api import websocket_response, http_response, parse_websocket_action, parse_websocket_params, \
    validate_websocket_action, validate_websocket_params


class TestApiUtils(TestCase):

    def test_websocket_response(self):
        # Ensure websocket response data is aggregated correctly
        response = websocket_response(None, success_action_result('Message'))
        self.assertEqual({'action': None, 'success': True, 'data': 'Message', 'error': None}, response)

        response = websocket_response(None, success_action_result({'sample': 'data'}))
        self.assertEqual({'action': None, 'success': True, 'data': {'sample': 'data'}, 'error': None}, response)

        response = websocket_response(None, error_action_result(''))
        self.assertEqual({'action': None, 'success': False, 'data': None, 'error': {'message': ''}}, response)

        response = websocket_response('Action', error_action_result('Error'))
        self.assertEqual({'action': 'Action', 'success': False, 'data': None, 'error': {'message': 'Error'}}, response)

    def test_http_response(self):
        # Ensure http status codes are defaulted correctly
        response = http_response(success_action_result('Message'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = http_response(error_action_result('Message'))
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Ensure http response data is aggregated correctly
        response = http_response(success_action_result('Message'), status.HTTP_200_OK)
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(b'"Message"', response.body)

        response = http_response(success_action_result({'sample': 'data'}), status.HTTP_200_OK)
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(b'{"sample":"data"}', response.body)

        response = http_response(error_action_result('Error'), status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(b'{"message":"Error"}', response.body)

    def test_parse_websocket_action(self):
        # Ensure parsing invalid action fields return none
        action = parse_websocket_action({})
        self.assertIsNone(action)

        action = parse_websocket_action({'action': ''})
        self.assertIsNone(action)

        action = parse_websocket_action({'action_123': 'TEST_ACTION'})
        self.assertIsNone(action)

        # Ensure invalid parameters return none
        # noinspection PyTypeChecker
        action = parse_websocket_action(None)
        self.assertIsNone(action)

        # noinspection PyTypeChecker
        action = parse_websocket_action(['action'])
        self.assertIsNone(action)

        # Ensure parsing valid action fields return their corresponding action
        action = parse_websocket_action({'action': 'TEST_ACTION'})
        self.assertEqual('TEST_ACTION', action)

        action = parse_websocket_action({'action': 'T'})
        self.assertEqual('T', action)

    def test_parse_websocket_params(self):
        # Ensure parsing invalid params fields return none
        params = parse_websocket_action({})
        self.assertIsNone(params)

        params = parse_websocket_params({'params': ''})
        self.assertIsNone(params)

        params = parse_websocket_params({'params_123': 'TEST_PARAMS'})
        self.assertIsNone(params)

        # Ensure invalid parameters return none
        # noinspection PyTypeChecker
        action = parse_websocket_params(None)
        self.assertIsNone(action)

        # noinspection PyTypeChecker
        action = parse_websocket_params(['params'])
        self.assertIsNone(action)

        # Ensure parsing valid params fields return their corresponding params
        params = parse_websocket_params({'params': 'TEST_PARAMS'})
        self.assertEqual('TEST_PARAMS', params)

        params = parse_websocket_params({'params': {'nested': 'params'}})
        self.assertEqual({'nested': 'params'}, params)

    def test_validate_websocket_action(self):
        # Ensure invalid actions return none
        # noinspection PyTypeChecker
        validated_action = validate_websocket_action(None)
        self.assertIsNone(validated_action)

        validated_action = validate_websocket_action('')
        self.assertIsNone(validated_action)

        validated_action = validate_websocket_action('NOT A VALID ACTION')
        self.assertIsNone(validated_action)

        # Ensure a valid action is correctly validated
        validated_action = validate_websocket_action(WebSocketAction.READ_MEMORY)
        self.assertEqual(WebSocketAction.READ_MEMORY, validated_action)

    def test_validate_websocket_params(self):
        # Ensure invalid params return none
        # noinspection PyTypeChecker
        validated_action = validate_websocket_params(None, MessageData)
        self.assertIsNone(validated_action)

        validated_action = validate_websocket_params({}, MessageData)
        self.assertIsNone(validated_action)

        validated_action = validate_websocket_params({'message': None}, MessageData)
        self.assertIsNone(validated_action)

        # Ensure valid params are correctly validated
        validated_action = validate_websocket_params({'message': 'Test'}, MessageData)
        self.assertEqual({'message': 'Test'}, validated_action)


if __name__ == '__main__':
    unittest.main()
