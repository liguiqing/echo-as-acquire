import unittest
from unittest import TestCase

from acquire.acquire_facility_factory import (FacilityFactoryMocker, facilities,
                                              facility_register, get_facility,install)
from config import logger


class MokerFacility:
    def __init__(self):
        self.type = 'mc'

    def __hash__(self):
        return hash(id(self.type))

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return hash(id(self.type))==hash(id(other.type))
        else:
            return False

    def play(self):
        logger.debug('Hello')

class TestAcquireFacilityFactory(TestCase):

    def test_register(self):
        self.assertEqual(0,len(facilities))
        facility_register(MokerFacility())
        self.assertEqual(1,len(facilities))
        facility_register(MokerFacility())
        self.assertEqual(1,len(facilities))
        install()
        self.assertTrue(len(facilities) > 1)
        self.assertTrue(l)

    def test_get_facility(self):
        facility_register(MokerFacility())
        self.assertEquals(MokerFacility(),get_facility('mc'))
        self.assertEquals(FacilityFactoryMocker(),get_facility('aa'))   
