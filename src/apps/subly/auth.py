"""
Steps:


flow = OAuth2WebServerFlow(client_id,
                           client_secret,
                           'https://www.googleapis.com/auth/youtube',
                           redirect_uri='urn:ietf:wg:oauth:2.0:oob')

... User gets redirected to to google auth.. they click through and we get a token back

credentials = flow.step2_exchange(token)

http = credentials.authorize(httplib2.Http())
service = build('youtube', 'v3', http=http)

request = service.playlists().list(part='snippet', mine=True)
# Returns a dict
playlists = request.execute()

"""
import httplib2

from oauth2client import client
from apiclient.discovery import build

from models import YTCredentials
import settings
import exceptions


class YTAuth(object):
    """
    Expected flow:

    auth = YTAuth()
    try:
        service = auth.get_service(user)
        playlists = service.playlists().list(part='snippet', mine=True).execute()
    except InvalidCredentials:
        redirect(auth.get_auth_uri(redirect='http://someurl/'))
    """
    def __init__(self, redirect=None):
        super(YTAuth, self).__init__()
        self._redirect = redirect
        self.flow = self._get_flow()

    def _get_flow(self):
        return client.OAuth2WebServerFlow(settings.SUBLY_CLIENT_ID,
                                          settings.SUBLY_CLIENT_SECRET,
                                          self._get_scope(),
                                          redirect_uri=self._redirect or 'urn:ietf:wg:oauth:2.0:oob')

    def _get_scope(self):
        """
        Get the scope that authorization will be asked for.
        :rtype: str
        """
        return 'https://www.googleapis.com/auth/youtube'

    def get_auth_uri(self):
        """
        Get the URI that can be used to allow a user to authorize the flow.
        :rtype: str
        """
        # TODO: Figure out how to get the access token from the redirect.
        return self.flow.step1_get_authorize_url()

    def get_credentials(self, user):
        """
        Get the current credentials for the specified user.
        :rtype: client.Credentials
        """
        credentials = YTCredentials.objects.most_recent(user)
        if credentials:
            if not credentials.creds.invalid:
                return credentials.creds
            else:
                raise exceptions.InvalidCredentials()
        raise exceptions.CredentialsNotAdded()

    def save_credentials(self, user, token):
        """
        Update credentials for the specified user.
        :param user:
        :param creds:
        :return:
        """
        creds = self.flow.step2_exchange(token)
        credentials = YTCredentials.objects.most_recent(user)
        if not credentials:
            credentials = YTCredentials(user=user)
        credentials.creds = creds
        credentials.save()
        return credentials.creds

    def get_service(self, user):
        """
        Get an object that can be used to create API calls.
        """
        http = self.get_credentials(user).authorize(httplib2.Http())
        return build('youtube', 'v3', http=http)
