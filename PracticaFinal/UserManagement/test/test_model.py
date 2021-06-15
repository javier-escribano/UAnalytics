import unittest
from django.test import TestCase
from UserManagement.models import History
from django.urls import reverse

class TestModel(TestCase):

    def setUp(self):
        History.objects.create(username="Paco", searchquery = "Rubiu5" , platform="Twitter" , dateandtime = "12-05-2020 12:05:50")
        History.objects.create(username="Pepe", searchquery = "elxokas" , platform="Twitch" , dateandtime = "12-05-2020 10:22:05")
        History.objects.create(username="Pamela", searchquery = "TheWillyrex" , platform="Youtube" , dateandtime = "12-05-2020 13:55:12")

    def test_historys(self):
        # Recuperamos las busquedas del historial y comprobamos sus campos
        h = History.objects.get(id=1)
        self.assertEquals(h.id, 1)
        self.assertEquals(h.username, "Paco")
        self.assertEquals(h.searchquery, "Rubiu5")
        self.assertEquals(h.platform, "Twitter")
        self.assertEquals(h.dateandtime, "12-05-2020 12:05:50")
        
        h = History.objects.get(id=2)
        self.assertEquals(h.id, 2)
        self.assertEquals(h.username, "Pepe")
        self.assertEquals(h.searchquery, "elxokas")
        self.assertEquals(h.platform, "Twitch")
        self.assertEquals(h.dateandtime, "12-05-2020 10:22:05")
        
        h = History.objects.get(id=3)
        self.assertEquals(h.id, 3)
        self.assertEquals(h.username, "Pamela")
        self.assertEquals(h.searchquery, "TheWillyrex")
        self.assertEquals(h.platform, "Youtube")
        self.assertEquals(h.dateandtime, "12-05-2020 13:55:12")
    
    @unittest.expectedFailure
    def test_history(self):
        # Test que debe fallar porque no hay tantas reviews
        r = History.objects.get(id=2434234)
