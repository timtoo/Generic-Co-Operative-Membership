# Generic Co-operative Membership System.
# Copyright 2011 Tim Middleton
#
# Generic Co-operative Membership System is free software: you can
# redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# Generic Co-operative Membership System is distributed in the hope
# that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Generic Co-operative Membership System.  If not, see
# <http://www.gnu.org/licenses/>.

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from coop import models
import time


class DatabaseTest(TestCase):
    def test_001_database_city_prov_country(self):
        """Verify models for county, province, and city
        """
        canada_data = {"alpha2": "CA", "alpha3": "CAN", "languages": "en-CA,fr-CA,iu", "area": 9984670.0, "geonameid": "6251999", "postal_code_regex": "^([a-zA-Z]\\d[a-zA-Z]\\d[a-zA-Z]\\d)$", "tld": ".ca", "alpha2_year": 1974, "numeric_code": 124, "currency_name": "Dollar", "phone": "1", "neighbours": "US", "country_norm": "canada", "fips": "CA", "postal_code_format": "@#@ #@#", "alpha2_note": "", "capital": "Ottawa", "country_name": "Canada", "equiv_fips": "", "continent": "NA", "currency_code": "CAD", "population": 33679000}
        models.Country.objects.create(**canada_data).save()

        canada = models.Country.objects.get(pk='CA')
        self.assertEqual(canada.country_name, u'Canada')

        models.Province.objects.create(province_id=7,
                province_name='Ontario', province_norm='ontario',
                prcode=35, province_code='ON', country_id=124).save()
        ontario = models.Province.objects.get(province_norm='ontario')
        self.assertEqual(ontario.country_id, canada.numeric_code)
        self.assertEqual(ontario.country.numeric_code, ontario.country_id)

        models.City.objects.create(city_name=unicode('Qu\xe9bec City', 'latin-1'),
                province_id=6115047).save()
        city = models.City.objects.all()
        self.assertEqual(len(city), 1)
        if city[0].city_norm == u'qu_bec_city':
            # see issue documented in setupdb.sql -- this is hopefully a temporary workaround
            print "WARNING: accent normalization is not set up properly"
        else:
            self.assertEqual(city[0].city_norm, u'quebec_city')
        self.assertEqual(city[0].city_id, 1)

        # province_id=-1 doesn't raise an error because ref check is deferred
        models.City.objects.create(city_name=u'Toronto', province_id=-1).save()
        city = models.City.objects.get(city_id=2)
        self.assertEqual(city.city_norm, u'toronto')

        # look up non-existant city
        with self.assertRaises(models.City.DoesNotExist):
            models.City.objects.get(city_name=u'Mem Basin')

        # make sure city_id is available after creation
        city = models.City.objects.create(city_name=u'Winnipeg', province_id=6065171)
        self.assertEqual(city.city_id, 3)
        city.save()
        self.assertEqual(city.city_id, 3)

    def test_002_member_add(self):
        """Verify adding member does the right things

            - set up any auto-create group types
            - apply any auto-matic loan types
            - set up membership fee owing
            - (emit signal that member is created)

        """

    def test_appsettings(self):
        #print repr(list(models.AppSettings.objects.all()))
        models.AppSettings.objects.create(name='test',
                label='test label', value='Test Value')
        a = models.AppSettings.get('test')
        self.assertEqual(a, 'Test Value')
        self.failUnless('test' in models.AppSettings.get.cached.keys())

        # default data isn't available?
        #a = models.AppSettings.get('coop_name')
        #self.assertEqual(a, 'Generic Co-op')

    def test_999(self):
        print "sleeping",
        time.sleep(8)

