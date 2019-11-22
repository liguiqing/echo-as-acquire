import unittest
from unittest import TestCase

from acquire.acquire_facility_factory import (facilities, facility_register, get_facility,install,get_facilities_connected)
from acquire.facility import VirtualFacilityFactory
from config import logger


class TestAcquireFacilityFactory(TestCase):

    def test_register(self):
        self.assertEqual(0,len(facilities))
        facility_register(VirtualFacilityFactory())
        self.assertEqual(1,len(facilities))
        facility_register(VirtualFacilityFactory())
        self.assertEqual(1,len(facilities))
        install()
        self.assertTrue(len(facilities) > 1)
        fs = get_facilities_connected()
        self.assertIsNotNone(fs)

    def test_get_facility(self):
        facility_register(VirtualFacilityFactory())
        self.assertEquals(VirtualFacilityFactory(),get_facility('Virtual'))

