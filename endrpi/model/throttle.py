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


class Throttle(BaseModel):
    """Interface for system throttle statuses."""
    throttling: bool
    throttlingHasOccurred: bool
    underVoltageDetected: bool
    underVoltageHasOccurred: bool
    armFrequencyCapped: bool
    armFrequencyCappingHasOccurred: bool
    softTemperatureLimitActive: bool
    softTemperatureLimitHasOccurred: bool
