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

from typing import Union, TypeVar, Optional, Dict, Type

from fastapi import status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from endrpi.model.action_result import ActionResult
from endrpi.model.websocket import WebSocketAction

# Generic type used in generic function parameters
T = TypeVar('T')


def websocket_response(action: Optional[str], action_result: ActionResult) -> Dict[str, any]:
    """
    Returns a :class:`Dict` of :class:`~endrpi.model.action_result.ActionResult` values with an optional action
    field for a given action result and websocket action.
    """
    return jsonable_encoder({'action': action, **action_result.__dict__})


def http_response(action_result: ActionResult, status_code: status = None) -> JSONResponse:
    """Returns a :class:`~fastapi.responses.JSONResponse` for a given status code and action result."""

    if action_result.success:
        json_content = jsonable_encoder(action_result.data)
        if not status_code:
            status_code = status.HTTP_200_OK
    else:
        json_content = jsonable_encoder(action_result.error)
        if not status_code:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(status_code=status_code, content=json_content)


def parse_websocket_action(data: Dict[str, str]) -> Union[str, None]:
    """
    Returns the websocket action from a given decoded websocket message or None if the action
    doesn't exist or isn't a valid string.
    """

    if isinstance(data, Dict):
        websocket_action = data.get('action', None)

        if websocket_action and isinstance(websocket_action, str):
            return websocket_action

    return None


def parse_websocket_params(data: Dict[str, any]) -> Union[any, None]:
    """Returns the websocket params from a given decoded websocket message or None if the params don't exist."""

    if isinstance(data, Dict):
        websocket_action = data.get('params', None)

        if websocket_action:
            return websocket_action

    return None


def validate_websocket_action(action: str) -> Optional[Type[WebSocketAction]]:
    """Returns a :class:`~endrpi.routes.websocket_route.WebSocketActions` if valid, otherwise returns None."""

    if action and isinstance(action, str):

        try:
            validated_action = WebSocketAction[action]
            return validated_action
        except KeyError:
            pass

    return None


def validate_websocket_params(params: Dict, model: Type[T]) -> Union[T, None]:
    """
    Returns an instantiated parameter model if given params are successfully validated against the given params model,
    otherwise returns None.
    """

    if params and isinstance(params, Dict):

        try:
            validated_params = model(**params)
            return validated_params
        except ValidationError:
            # A validation error signifies the given params were not valid constructor arguments for the model
            # Note: Invalid params could mean missing or incorrect type
            pass

    return None
