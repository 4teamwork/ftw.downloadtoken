from unittest2 import TestCase
from ftw.downloadtoken.testing import FTW_DOWNLOADTOKEN_INTEGRATION_TESTING


class TestStorage(TestCase):

    layer = FTW_DOWNLOADTOKEN_INTEGRATION_TESTING

    def test_storage_initialize(self):
        self.assertTrue(True)
