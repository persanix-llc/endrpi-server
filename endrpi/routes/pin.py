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

from typing import Dict, Union

from fastapi import APIRouter, status

from endrpi.actions.pin import read_pin_configurations, read_pin_configuration, update_pin_configuration
from endrpi.model.action_result import ActionResult, error_action_result
from endrpi.model.message import MessageData, PinMessage
from endrpi.model.pin import PinConfiguration, RaspberryPiPinIds, PinIo
from endrpi.utils.api import http_response

# Router that is exported to the server
router = APIRouter()


@router.get(
    '/pins',
    name='All pin configurations.',
    description='Gets Pin configurations for each pin on the board.',
    responses={
        status.HTTP_200_OK: {
            'model': Union[ActionResult[Dict[str, PinConfiguration]], ActionResult[PinConfiguration]]
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': MessageData,
            'description': 'An error occurred',
        }
    }
)
async def get_pin_configurations_route():
    pin_ids = list(RaspberryPiPinIds)
    pin_states_action_result = read_pin_configurations(pin_ids)
    return http_response(pin_states_action_result)


@router.get(
    '/pins/{bcm_id}',
    name='Pin configuration.',
    description='Gets pin configuration for a specific pin using its BCM number (i.e. \'GPIO17\').',
    responses={
        status.HTTP_200_OK: {
            'model': PinConfiguration
        },
        status.HTTP_404_NOT_FOUND: {
            'model': MessageData,
            'description': PinMessage.ERROR_NOT_FOUND__PIN_ID__,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': MessageData,
            'description': 'An error occurred',
        }
    }
)
async def get_pin_configuration_route(bcm_id: str):
    valid_pin_id = RaspberryPiPinIds.from_bcm_id(bcm_id)
    if valid_pin_id:
        pin_action_result = read_pin_configuration(valid_pin_id)
        return http_response(pin_action_result)
    else:
        action_result = error_action_result(PinMessage.ERROR_NOT_FOUND__PIN_ID__.format(pin_id=bcm_id))
        return http_response(action_result, status.HTTP_404_NOT_FOUND)


@router.put(
    '/pins/{bcm_id}',
    description='Updates pin configuration for a specific pin using its BCM number (i.e. \'GPIO17\').',
    responses={
        status.HTTP_200_OK: {
            'model': PinConfiguration
        },
        status.HTTP_404_NOT_FOUND: {
            'model': MessageData,
            'description': PinMessage.ERROR_NOT_FOUND__PIN_ID__,
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': MessageData,
            'description': 'An error occurred',
        }
    }
)
async def put_pin_state_param_route(bcm_id: str, pin_configuration: PinConfiguration):
    valid_pin_id = RaspberryPiPinIds.from_bcm_id(bcm_id)
    if valid_pin_id:
        # Input configurations must specify a pin pull, output configurations must specify a state
        if pin_configuration.io is PinIo.INPUT and not pin_configuration.pull:
            action_result = error_action_result(PinMessage.ERROR_NO_INPUT_PULL)
            return http_response(action_result, status.HTTP_400_BAD_REQUEST)
        elif pin_configuration.io is PinIo.OUTPUT and pin_configuration.state is None:
            action_result = error_action_result(PinMessage.ERROR_NO_OUTPUT_STATE)
            return http_response(action_result, status.HTTP_400_BAD_REQUEST)

        action_result = update_pin_configuration(valid_pin_id, pin_configuration)
        return http_response(action_result)
    else:
        action_result = error_action_result(PinMessage.ERROR_NOT_FOUND__PIN_ID__.format(pin_id=bcm_id))
        return http_response(action_result, status.HTTP_404_NOT_FOUND)
