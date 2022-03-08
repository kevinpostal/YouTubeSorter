from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse
from django.conf import settings
from django.shortcuts import redirect

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import os

from .models import Credentials

if settings.DEBUG:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

CLIENT_SECRETS_FILE = os.path.join(os.getcwd(), "Youtube-OAuth-client_secret.json")
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def oauth2callback(request):
    state = {}
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.get_full_path()
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    obj, _ = Credentials.objects.get_or_create(client_id=flow.credentials.client_id)
    Credentials.objects.filter(client_id=flow.credentials.client_id).update(**credentials_to_dict(credentials))
    request.session['credentials'] = credentials_to_dict(credentials)
    return redirect(reverse('list-videos'))

def auth(request):
    if request.session.get('credentials', False):
        return redirect(reverse('list-videos'))

    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.

    flow.redirect_uri = request.build_absolute_uri(reverse('oauth2callback'))

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    return redirect(authorization_url)