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

import os
import sys
import uvicorn
import argparse

# Fix endrpi module not found error
sys.path.append(os.path.abspath('.'))

from endrpi.config.logging import configure_logger, get_logging_configuration, get_logger
from endrpi.config.pin_factory import configure_pin_factory
from endrpi.server import app




def main():
    # Configure arguments that can be passed to endrpi
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-p', '--port',
                        dest='port',
                        type=int,
                        default=5000,
                        help='set the port to start the server on')
    parser.add_argument('-h', '--host',
                        dest='host',
                        type=str,
                        default='0.0.0.0',
                        help='set the host to start the server on')
    args = parser.parse_args()

    # Initialize the custom log format and set both the endrpi logger and uvicorn logger to use it
    configure_logger()
    uvicorn_logging_config = get_logging_configuration()

    # Initialize the raspberry pi pin factory if possible, otherwise initialize a mock factory
    configure_pin_factory()

    try:
        # Run the endrpi server programmatically (see: https://www.uvicorn.org/deployment)
        uvicorn.run(app, host=args.host, port=args.port, log_config=uvicorn_logging_config)
    except Exception as exception:
        get_logger().error(exception)


if __name__ == '__main__':
    main()
