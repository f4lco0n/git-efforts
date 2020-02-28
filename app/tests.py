from django.test import TestCase
from django.urls import reverse, resolve
from .views import home, repositorys_board
from .models import Repository
# Create your tests here.

class HomeTests(TestCase):
    def test_home_view_status_code(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func, home)

class RepositoryBoardTtest(TestCase):
    def setUp(self):
        Repository.objects.create(url="https://github.com/nickname")

    def test_repository_board_view_success_status_code(self):
        url = reverse('repositorys_board', kwargs={'pk':1})
        respone = self.client.get(url)
        self.assertEquals(respone.status_code,200)

    def test_repository_board_view_not_found_status_code(self):
        url = reverse('repositorys_board', kwargs={'pk': 10})
        respone = self.client.get(url)
        self.assertEquals(respone.status_code, 404)


