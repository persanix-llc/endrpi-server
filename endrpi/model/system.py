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

from pydantic import BaseModel

from endrpi.model.frequency import Frequency
from endrpi.model.memory import Memory
from endrpi.model.platform import Platform
from endrpi.model.temperature import Temperature
from endrpi.model.throttle import Throttle
from endrpi.model.up_time import UpTime


class System(BaseModel):
    """Interface for comprehensive system information."""
    platform: Platform
    temperature: Temperature
    throttle: Throttle
    uptime: UpTime
    frequency: Frequency
    memory: Memory
