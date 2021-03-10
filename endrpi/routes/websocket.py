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

from json.decoder import JSONDecodeError

from fastapi import APIRouter
from fastapi.websockets import WebSocket, WebSocketDisconnect

from endrpi.actions.pin import read_pin_configurations, update_pin_configuration
from endrpi.actions.system import read_temperature, read_throttle, read_uptime, read_frequency, read_memory
from endrpi.model.action_result import error_action_result, success_action_result
from endrpi.model.message import WebSocketMessage
from endrpi.model.pin import PinConfigurationMap
from endrpi.model.websocket import WebSocketAction, ReadPinConfigurationsParams, \
    UpdatePinConfigurationsParams
from endrpi.utils.api import parse_websocket_action, \
    validate_websocket_action, websocket_response, validate_websocket_params, parse_websocket_params

# Router that is exported to the server
router = APIRouter()


@router.websocket('/')
async def websocket_route(websocket: WebSocket):
    # Wait for the websocket to finish connecting
    await websocket.accept()

    while True:

        try:
            received_message = await websocket.receive_json()
        except JSONDecodeError:
            error_result = error_action_result(WebSocketMessage.ERROR_INVALID_DATA)
            error_response = websocket_response(action=None, action_result=error_result)
            await websocket.send_json(error_response)
            continue
        except WebSocketDisconnect:
            break

        action = parse_websocket_action(received_message)
        if not action:
            action_result = error_action_result(WebSocketMessage.ERROR_MISSING_ACTION_FIELD)
            response = websocket_response(action=None, action_result=action_result)
            await websocket.send_json(response)
            continue

        validated_action = validate_websocket_action(action)
        if not validated_action:
            action_result = error_action_result(WebSocketMessage.ERROR_INVALID_ACTION_FIELD)
            response = websocket_response(action=None, action_result=action_result)
            await websocket.send_json(response)
            continue

        params = parse_websocket_params(received_message)

        if validated_action is WebSocketAction.READ_TEMPERATURE:
            action_result = read_temperature()
        elif validated_action is WebSocketAction.READ_THROTTLE:
            action_result = read_throttle()
        elif validated_action is WebSocketAction.READ_UPTIME:
            action_result = read_uptime()
        elif validated_action is WebSocketAction.READ_FREQUENCY:
            action_result = read_frequency()
        elif validated_action is WebSocketAction.READ_MEMORY:
            action_result = read_memory()
        elif validated_action is WebSocketAction.READ_PIN_CONFIGURATIONS:
            action_result = __read_pin_configurations(params)
        elif validated_action is WebSocketAction.UPDATE_PIN_CONFIGURATIONS:
            action_result = __update_pin_configurations(params)
        else:
            action_result = error_action_result(WebSocketMessage.ERROR_UNKNOWN_ACTION_VALUE)

        response = websocket_response(action=validated_action.value, action_result=action_result)
        await websocket.send_json(response)
        continue


def __read_pin_configurations(params):
    if not params:
        return error_action_result(WebSocketMessage.ERROR_MISSING_PARAMS_FIELD)

    validated_params = validate_websocket_params(params, ReadPinConfigurationsParams)
    if not validated_params:
        return error_action_result(WebSocketMessage.ERROR_INVALID_PARAMS_FIELD)

    return read_pin_configurations(validated_params.pins)


def __update_pin_configurations(params):
    if not params:
        return error_action_result(WebSocketMessage.ERROR_MISSING_PARAMS_FIELD)

    validated_params = validate_websocket_params(params, UpdatePinConfigurationsParams)
    if not validated_params:
        return error_action_result(WebSocketMessage.ERROR_INVALID_PARAMS_FIELD)

    pin_configuration_map: PinConfigurationMap = validated_params.pins
    if not pin_configuration_map or len(pin_configuration_map) <= 0:
        return error_action_result(WebSocketMessage.ERROR_MISSING_PIN_ID)

    for pin_id, pin_configuration in pin_configuration_map.items():
        action_result = update_pin_configuration(pin_id, pin_configuration)

        if not action_result.success:
            return action_result

    return success_action_result(WebSocketMessage.SUCCESS_PIN_CONFIGS_UPDATED)
