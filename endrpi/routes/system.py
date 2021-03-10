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

from fastapi import APIRouter, status

from endrpi.actions.system import read_platform, read_temperature, read_throttle, read_uptime, read_frequency, \
    read_memory, read_system
from endrpi.model.frequency import Frequency
from endrpi.model.memory import Memory
from endrpi.model.message import MessageData
from endrpi.model.platform import Platform
from endrpi.model.system import System
from endrpi.model.temperature import Temperature
from endrpi.model.throttle import Throttle
from endrpi.model.up_time import UpTime
from endrpi.utils.api import http_response

# Router that is exported to the server
router = APIRouter()


@router.get(
    '/system',
    name='Comprehensive system information.',
    description='Returns comprehensive information about the system including platform, temperature, throttling, '
                'uptime, frequency, and memory.',
    responses={
        status.HTTP_200_OK: {
            'model': System
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': MessageData,
            'description': 'An error occurred',
        }
    }
)
async def get_system_route():
    system_action_result = read_system()
    return http_response(system_action_result)


@router.get(
    '/system/platform',
    name='Basic platform information',
    responses={
        status.HTTP_200_OK: {
            'model': Platform
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': MessageData,
            'description': 'An error occurred',
        }
    })
async def get_platform_route():
    platform_action_result = read_platform()
    return http_response(platform_action_result)


@router.get(
    '/system/temperature',
    name='System on chip temperature',
    responses={
        status.HTTP_200_OK: {
            'model': Temperature
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': MessageData,
            'description': 'An error occurred',
        }
    })
async def get_temperature_route():
    temperature_action_result = read_temperature()
    return http_response(temperature_action_result)


@router.get(
    '/system/throttle',
    name='Past and present throttling',
    responses={
        status.HTTP_200_OK: {
            'model': Throttle
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': MessageData,
            'description': 'An error occurred',
        }
    })
async def get_throttle_route():
    throttle_action_result = read_throttle()
    return http_response(throttle_action_result)


@router.get(
    '/system/uptime',
    name='System uptime',
    responses={
        status.HTTP_200_OK: {
            'model': UpTime
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': MessageData,
            'description': 'An error occurred',
        }
    })
async def get_uptime_route():
    uptime_action_result = read_uptime()
    return http_response(uptime_action_result)


@router.get(
    '/system/frequency',
    name='Chip clock frequencies',
    responses={
        status.HTTP_200_OK: {
            'model': Frequency
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': MessageData,
            'description': 'An error occurred',
        }
    })
async def get_frequency_route():
    frequency_action_result = read_frequency()
    return http_response(frequency_action_result)


@router.get(
    '/system/memory',
    name='Memory usage',
    responses={
        status.HTTP_200_OK: {
            'model': Memory
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            'model': MessageData,
            'description': 'An error occurred',
        }
    }
)
async def get_memory_route():
    memory_action_result = read_memory()
    return http_response(memory_action_result)
