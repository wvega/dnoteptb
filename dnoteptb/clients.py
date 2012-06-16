# -*- coding: utf8 -*-

from google.appengine.api import urlfetch

from django.http import HttpResponseRedirect
from dnoteptb.oauth.oauth import OAuthClient, OAuthToken, OAuthConsumer

class TwitterOAuthClient(OAuthClient):

    def __init__(self, request):
        self.request = request
        self.request_token_url = 'https://twitter.com/oauth/request_token'
        self.access_token_url = 'https://twitter.com/oauth/access_token'
        self.authorization_url = 'https://twitter.com/oauth/authorize'

    def fetch_request_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        response = urlfetch.fetch(url=self.request_token_url, method=oauth_request.http_method, headers=oauth_request.to_header())
        import cgi
        return OAuthToken.from_string(response.content)

    def fetch_access_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        response = urlfetch.fetch(url=self.access_token_url, method=oauth_request.http_method, headers=oauth_request.to_header())
        #oauth_token=15312579-gM5KtlpJydi8sjb6ZtVb5Tiic6hn9uVoWrXqNQ5hH&amp;oauth_token_secret=JN3ERoZyPlqhfivfY4uBSiosjRgjjhKvNp9U0KZTn0&amp;user_id=15312579&amp;screen_name=wvega
        return (OAuthToken.from_string(response.content), response)

    def authorize_token(self, oauth_request):
        # via url
        # -> typically just some okay response
        return HttpResponseRedirect(oauth_request.to_url())

    def access_resource(self, oauth_request):
        # via post body
        # -> some protected resources
        params = dict(url=oauth_request.http_url, method=oauth_request.http_method)
        if oauth_request.http_method in ['POST', 'PUT']:
            params['payload'] = oauth_request.to_postdata()
            params['headers'] = {'Content-Type' :'application/x-www-form-urlencoded'}
        else:
            params.update(url=oauth_request.to_url())
        response = urlfetch.fetch(**params)
        return response.content

consumer = OAuthConsumer('XpWhwQrBHaBBeA6L71ueQ', 'B9BhzNlSpHV3EYBdJUOqFb3bg7u1GQRIpMkto5XQN4')