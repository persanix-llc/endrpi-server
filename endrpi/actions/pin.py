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

from typing import Dict, List

from gpiozero import Device, PinUnsupported
from pydantic import ValidationError

from endrpi.model.action_result import ActionResult, error_action_result, success_action_result
from endrpi.model.message import MessageData, PinMessage
from endrpi.model.pin import PinConfiguration, RaspberryPiPinIds, PinIo, PinPull, PinConfigurationMap


def read_pin_configurations(pin_ids: List[RaspberryPiPinIds]) -> ActionResult[PinConfigurationMap]:
    """Returns the result of attempting to read the :class:`~endrpi.model.pin.PinConfiguration` of every pin.

    .. note:: A read error on a single pin will cause an error result.
    """

    pin_state_map: Dict[RaspberryPiPinIds, PinConfiguration] = {}

    for pin_id in pin_ids:
        pin_state_action_result = read_pin_configuration(pin_id)
        if pin_state_action_result.success:
            pin_state_map[pin_id] = pin_state_action_result.data
        else:
            return error_action_result(pin_state_action_result.error.message)

    return success_action_result(pin_state_map)


def read_pin_configuration(pin_id: RaspberryPiPinIds) -> ActionResult[PinConfiguration]:
    """Returns the result of attempting to read the :class:`~endrpi.model.pin.PinConfiguration` of a given pin."""

    try:
        gpiozero_pin = Device.pin_factory.pin(pin_id)
    except PinUnsupported:
        return error_action_result(PinMessage.ERROR_UNSUPPORTED__PIN_ID__.format(pin_id=pin_id))

    # Uppercase both gpiozero string values because pin enumerations are uppercase
    gpiozero_pin_function = gpiozero_pin.function.upper()
    gpiozero_pin_pull = gpiozero_pin.pull.upper()

    pin_io = PinIo(gpiozero_pin_function)
    pin_state = gpiozero_pin.state
    pin_pull = PinPull(gpiozero_pin_pull)

    try:
        pin_configuration = PinConfiguration(io=pin_io, state=pin_state, pull=pin_pull)
        return success_action_result(pin_configuration)
    except ValidationError:
        return error_action_result(PinMessage.ERROR_VALIDATION)


def update_pin_configuration(pin_id: RaspberryPiPinIds,
                             pin_configuration: PinConfiguration) -> ActionResult[MessageData]:
    """
    Returns the result of updating the :class:`~endrpi.model.pin.PinConfiguration` of a given pin.

    .. note::
        Ignores 'state' when 'io' is set to INPUT.

    .. note::
        Ignores 'pull' when 'io' is set to OUTPUT.
    """

    try:
        gpiozero_pin = Device.pin_factory.pin(pin_id)
    except PinUnsupported:
        return error_action_result(PinMessage.ERROR_UNSUPPORTED__PIN_ID__.format(pin_id=pin_id))

    if pin_configuration.io is PinIo.INPUT:
        if not pin_configuration.pull:
            return error_action_result(PinMessage.ERROR_NO_INPUT_PULL)
        # Don't set pin output state on an input pin
        gpiozero_pin.function = pin_configuration.io.lower()
        gpiozero_pin.pull = pin_configuration.pull.lower()
    else:
        if pin_configuration.state is None:
            return error_action_result(PinMessage.ERROR_NO_OUTPUT_STATE)
        # Don't set pin pull on an output pin
        gpiozero_pin.function = pin_configuration.io.lower()
        gpiozero_pin.state = pin_configuration.state

    message_data = MessageData(message=PinMessage.SUCCESS_UPDATED__PIN_ID__.format(pin_id=pin_id))
    return success_action_result(message_data)
