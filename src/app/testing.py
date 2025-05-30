import json
from urllib.parse import urlencode
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class AuthTokenTesting(APITestCase):

    def get_access_token(self, user):
        """
            Obtain Token for User
        """
        return str(RefreshToken.for_user(user).access_token)

    def get(self, url, token=None, params=None):
        """
            GET method with access token
        """
        kwargs = {}
        if token:
            kwargs['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        if params:
            kwargs['QUERY_STRING'] = urlencode(params, doseq=True)
        return self.client.get(url, **kwargs)

    def post(self, url, data, token=None):
        """
            POST method with access token
        """
        kwargs = {'content_type': 'application/json'}
        if token:
            kwargs['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return self.client.post(url, json.dumps(data), **kwargs)

    def patch(self, url, data, token):
        """
            PATCH method with access token
        """
        kwargs = {'content_type': 'application/json'}
        if token:
            kwargs['HTTP_AUTHORIZATION'] = f'Bearer {token}'
        return self.client.patch(url, json.dumps(data), **kwargs)

    def assert_status_200(self, response):
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def assert_status_201(self, response):
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def assert_status_403(self, response):
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

    def assert_status_400(self, response):
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
    