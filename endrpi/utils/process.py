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

import subprocess
from typing import Union

from endrpi.config.logging import get_logger


def process_output(process_args: [str]) -> Union[str, None]:
    """Returns the output of running a command if successful, otherwise returns None."""

    try:
        # Open a new process and get the output
        process = subprocess.Popen(process_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if stderr:
            get_logger().error(f'Command "{process_args}" wrote to stderr with the message "{stderr.decode()}"')
            return None
        else:
            return stdout.decode()
    except (OSError, ValueError) as error:
        get_logger().exception(error)
        return None
