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

import logging
import unittest
from unittest import TestCase
from unittest.mock import patch

from endrpi.utils.process import process_output


class TestProcessUtils(TestCase):

    def setUp(self):
        logging.disable(logging.CRITICAL)

    @patch('endrpi.utils.process.subprocess.Popen')
    def test_process_output(self, mocked_popen_constructor):

        # Instantiate a mocked popen object
        mocked_popen = mocked_popen_constructor.return_value

        # Ensure errors in stderr propagate
        mocked_popen.communicate.return_value = (b'Value', b'Error')
        output = process_output(['example', 'command'])
        self.assertIsNone(output)

        mocked_popen.communicate.return_value = (b'', b'E')
        output = process_output(['example', 'command'])
        self.assertIsNone(output)

        # Ensure errors caught while running the command propagate
        mocked_popen.communicate.side_effect = OSError('An error occurred')
        output = process_output(['example', 'command'])
        self.assertIsNone(output)
        mocked_popen.communicate.side_effect = None

        mocked_popen.communicate.side_effect = ValueError('An error occurred')
        output = process_output(['example', 'command'])
        self.assertIsNone(output)
        mocked_popen.communicate.side_effect = None

        mocked_popen.communicate.side_effect = OSError('An error occurred')
        output = process_output(['example', 'command'])
        self.assertIsNone(output)
        mocked_popen.communicate.side_effect = None

        # Ensure valid inputs return their expected results
        mocked_popen.communicate.return_value = (b'Value', None)
        output = process_output(['example', 'command'])
        self.assertIsNotNone(output)
        self.assertEqual(output, 'Value')

        mocked_popen.communicate.return_value = (b'', None)
        output = process_output(['example', 'command'])
        self.assertIsNotNone(output)
        self.assertEqual(output, '')

        mocked_popen.communicate.return_value = (b'', b'')
        output = process_output(['example', 'command'])
        self.assertIsNotNone(output)
        self.assertEqual(output, '')


if __name__ == '__main__':
    unittest.main()
