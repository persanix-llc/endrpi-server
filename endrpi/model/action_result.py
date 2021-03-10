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

from typing import Generic, TypeVar, Optional

from pydantic.generics import GenericModel

from endrpi.model.message import MessageData

# Pydantic generic
T = TypeVar('T')


class ActionResult(GenericModel, Generic[T]):
    """
    Interface used to represent the result of performing a generic action (i.e. running a command).

    Example of a successful generic temperature action result:
        ActionResult[str](success=True, data='System temperature: 50F', error=None)

    Example of a failed generic temperature action result:
        ActionResult[str](success=False, data=None, error='Requires elevated privilege.')
    """
    success: bool
    data: Optional[T]
    error: Optional[MessageData]


def success_action_result(data: any = None) -> ActionResult:
    """Returns an :class:`ActionResult` preconfigured for successful actions"""
    return ActionResult(success=True, data=data, error=None)


def error_action_result(message: str) -> ActionResult:
    """Returns an :class:`ActionResult` preconfigured for failed actions"""
    message_data = MessageData(message=message)
    return ActionResult(success=False, data=None, error=message_data)
