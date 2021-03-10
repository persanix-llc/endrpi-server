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
from os import path
import webbrowser

from definitions import ROOT_DIRECTORY


def generate_code_coverage():
    """
    Generates code coverage report HTML and opens it in a browser

    Run: python -m scripts.code_coverage
    """

    try:
        print('Running code coverage...')
        command = ['coverage', 'run', '-m', 'unittest', 'discover']
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT_DIRECTORY)
        stdout, stderr = process.communicate()

        # Coverage writes to standard error even if successful, parse result for the string 'OK'
        output = stderr.decode()
        output_success = 'OK' in output
        print(output)

        if output_success:
            print('Generating HTML...')
            command = ['coverage', 'html']
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=ROOT_DIRECTORY)
            process.communicate()

            coverage_html_path = path.join(ROOT_DIRECTORY, 'coverage', 'index.html')
            if path.exists(coverage_html_path):
                print('Launching browser...')
                webbrowser.open(coverage_html_path)
            else:
                print('Failed to launch code coverage web page')
        else:
            print('Failed to generate code coverage report')
            print(output)
    except (OSError, ValueError) as error:
        print(error)


if __name__ == '__main__':
    generate_code_coverage()
