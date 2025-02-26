from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from watchlist_app.models import Watchlist, StreamPlatform, Review


class StreamPlatformTestCase(APITestCase):
    def setUp(self):
        self.non_admin_user = User.objects.create_user(username='testuser', password='testpass')
        self.non_admin_token = Token.objects.create(user=self.non_admin_user)

        self.admin_user = User.objects.create_user(username='adminuser', password='adminpass', is_staff=True)
        self.admin_token = Token.objects.create(user=self.admin_user)

        self.stream = StreamPlatform.objects.create(name='Netflix', about='Streaming Platform',
                                                    website='https://www.netflix.com')

    def test_streamplatform_create_non_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.non_admin_token.key)

        url = reverse('watchlist_app:streamplatform-list')
        data = {'name': 'Hulu', 'about': 'Streaming Platform', 'website': 'https://www.hulu.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_streamplatform_create(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('watchlist_app:streamplatform-list')
        data = {'name': 'Hulu', 'about': 'Streaming Service', 'website': 'https://www.hulu.com'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Expect success

    def test_streamplatform_list(self):
        url = reverse('watchlist_app:streamplatform-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_streamplatform_ind(self):
        url = reverse('watchlist_app:streamplatform-detail', args=[self.stream.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_streamplatform_update(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('watchlist_app:streamplatform-detail', args=[self.stream.id])
        data = {'name': 'Hulu', 'about': 'Streaming Platform', 'website': 'https://www.hulu.com'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_streamplatform_delete(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.admin_token.key)
        url = reverse('watchlist_app:streamplatform-detail', args=[self.stream.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class WatchlistTestCase(APITestCase):

    def setUp(self):
        self.non_admin_user = User.objects.create_user(username='testuser', password='testpass')
        self.non_admin_token = Token.objects.create(user=self.non_admin_user)

        self.admin_user = User.objects.create_user(username='adminuser', password='adminpass', is_staff=True)
        self.admin_token = Token.objects.create(user=self.admin_user)

        self.stream = StreamPlatform.objects.create(name='Netflix', about='Streaming Platform',
                                                    website='https://www.netflix.com')
        self.watchlist = Watchlist.objects.create(platform=self.stream, title='Test Watchlist',
                                                  description='Test Description', active=True)

    def test_watchlist_create(self):
        url = reverse('watchlist_app:movie-list')
        data = {'platform': self.stream.id, 'title': 'Test Watchlist', 'description': 'Test Description',
                'active': True}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_watchlist_list(self):
        url = reverse('watchlist_app:movie-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_watchlist_ind(self):
        url = reverse('watchlist_app:movie-detail', args=[self.watchlist.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Watchlist')


class ReviewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.stream = StreamPlatform.objects.create(name='Netflix', about='Streaming Platform',
                                                    website='https://www.netflix.com')
        self.watchlist = Watchlist.objects.create(platform=self.stream, title='Test Watchlist',
                                                  description='Test Description', active=True)

    def test_review_create(self):
        url = reverse('watchlist_app:review-create', args=[self.watchlist.id])
        data = {'rating': 4, 'description': 'Test Review', 'watchlist': self.watchlist.id, 'active': True,
                'review_user': self.user.id}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().rating, 4)
        self.assertEqual(Review.objects.get().description, 'Test Review')
        self.assertEqual(Review.objects.get().active, True)
        self.assertEqual(Review.objects.get().review_user, self.user)

    def test_review_create_unauthorized(self):
        self.client.force_authenticate(user=None)
        url = reverse('watchlist_app:review-create', args=[self.watchlist.id])
        data = {'rating': 4, 'description': 'Test Review', 'watchlist': self.watchlist.id, 'active': True,
                'review_user': self.user.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_review_update(self):
        review = Review.objects.create(rating=3, description='Test Review', watchlist=self.watchlist,
                                       active=True, review_user=self.user)
        url = reverse('watchlist_app:review-detail', args=[review.id])
        data = {'rating': 5, 'description': 'Updated Test Review', 'watchlist': self.watchlist.id, 'active': True,
                'review_user': self.user.id}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Review.objects.get().rating, 5)
        self.assertEqual(Review.objects.get().description, 'Updated Test Review')
        self.assertEqual(Review.objects.get().active, True)
        self.assertEqual(Review.objects.get().review_user, self.user)

    def test_review_list(self):
        url = reverse('watchlist_app:review-list', args=[self.watchlist.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_review_user(self):
        response = self.client.get('/watch/reviews/?username=' + str(self.user.username))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
