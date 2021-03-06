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

import unittest
from unittest import TestCase

from endrpi.utils.bitwise import is_bit_set


class TestBitwiseUtils(TestCase):

    def test_is_bit_set(self):

        self.assertTrue(is_bit_set(0b1, 0))
        self.assertTrue(is_bit_set(0b10, 1))
        self.assertTrue(is_bit_set(0b11110, 3))

        self.assertTrue(is_bit_set(1, 0))
        self.assertTrue(is_bit_set(17, 4))
        self.assertTrue(is_bit_set(63, 5))

        [self.assertTrue(is_bit_set(255, x)) for x in range(7)]

        self.assertFalse(is_bit_set(0, 0))
        self.assertFalse(is_bit_set(4, 1))

        [self.assertFalse(is_bit_set(256, x)) for x in range(7)]


if __name__ == '__main__':
    unittest.main()
