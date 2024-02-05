from unittest import TestCase

from ytmb.utils import *


class TestFilename(TestCase):
    def test_lower_and_num(self):
        self.assertTrue(is_ok_filename('abcdefg1234'))

    def test_all_char(self):
        self.assertTrue(is_ok_filename('Some_Test_Name-Version2'))

    def test_hashtag(self):
        self.assertFalse(is_ok_filename('#BadNames'))

    def test_dot(self):
        self.assertFalse(is_ok_filename('dots.dots.dots'))

    def test_slash(self):
        self.assertFalse(is_ok_filename('we/love/directories'))

    def test_empty(self):
        self.assertFalse(is_ok_filename(''))

    def test_backslash(self):
        self.assertFalse(is_ok_filename(r'c\windows\perhaps'))
