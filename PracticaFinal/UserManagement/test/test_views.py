import unittest
from django.test import TestCase
from django.test import Client
from django.contrib.auth import models


class TestViews(TestCase):
    def setUp(self):
        models.User.objects.create(username="test", password="testpass")
        
    def test_login(self):
        c = Client()
        response = c.post(
            '/login', {'username': 'test', 'password': 'testpass'})
        self.assertEquals(response.status_code, 200)
        
    def test_register(self):
        c = Client()
        response = c.post(
            '/register', {'username': 'test', 'email': 'pelicanitoClasico@gmail.com','password1': 'testpass', 'password2': 'testpass'})
        self.assertEquals(response.status_code, 200)
        
        
