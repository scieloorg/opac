# coding: utf-8

from base import BaseTestCase

from opac_schema.v1 import models


class TestCase(BaseTestCase):

    def test_one_sponsor(self):
        item = {'name': 'bar', '_id': '123'}
        sponsor = models.Sponsor(**item).save()
        self.assertEqual(item['name'], sponsor.name)

    def test_all_sponsors(self):
        item1 = {'name': 'bar1', '_id': '1'}
        sponsor = models.Sponsor(**item1).save()
        item2 = {'name': 'bar2', '_id': '2'}
        sponsor = models.Sponsor(**item2).save()
        sponsors = [sponsor for sponsor in models.Sponsor.objects.all()]

        self.assertEqual(2, len(sponsors))
