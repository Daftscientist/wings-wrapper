from functools import partial
from typing import Union
from sanic import BadRequest, Request
from core.general import load_config
from requests_oauthlib import OAuth2Session
import urllib.parse

CLIENT_ID = load_config()["oauth"]["discord"]["client_id"]
CLIENT_SECRET = load_config()["oauth"]["discord"]["client_secret"]

API_BASE_URL = "https://discord.com/api"
AUTHORIZATION_BASE_URL = API_BASE_URL + "/oauth2/authorize"
TOKEN_URL = API_BASE_URL + "/oauth2/token"

class DiscordOAuth(object):
    """
    DiscordOAuth class for handling Discord OAuth2 authentication.

    This class provides methods for generating the OAuth2 authorization URL,
    fetching the OAuth2 token, and initializing the OAuth2 session.

    Args:
        redirect_uri (str): The redirect URI for the OAuth2 flow.
        scopes (list): A list of scopes to request during the OAuth2 flow.
        client_id (str): The client ID of your Discord application.
        client_secret (str): The client secret of your Discord application.
    """

    def __init__(self, redirect_uri: str, scopes: list, client_id: str, client_secret: str):
        """
        Initializes a DiscordOAuth object.

        Args:
            redirect_uri (str): The redirect URI for the OAuth2 flow.
            scopes (list): A list of scopes to request during the OAuth2 flow.
            client_id (str): The client ID of your Discord application.
            client_secret (str): The client secret of your Discord application.
        """
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.client_id = client_id
        self.client_secret = client_secret
        self.BASE_URL = API_BASE_URL
        self.CDN_URL = "https://cdn.discordapp.com/"

        # Initializing the OAuth2 session.
        self.oauth = OAuth2Session(self.client_id, redirect_uri=self.redirect_uri, scope=self.scopes)

    def get_login_url(self):
        """Returns the OAuth2 authorization URL.

        This method generates the OAuth2 authorization URL for Discord authentication.
        It adds the necessary parameters to the URL, such as access_type and state.

        Returns:
            A list containing the generated authorization URL and the state parameter.
        """
        login_url, state = self.oauth.authorization_url(AUTHORIZATION_BASE_URL)

        login_url = login_url.split('state=')[0]
        login_url += f'access_type=offline&state={state}'

        return [login_url, state]

    def fetch_token(self, request: Request):
        """
        Fetches the OAuth2 token from the provided request.

        Args:
            request (Request): The request object containing the URL.

        Returns:
            tuple: A tuple containing the token and the state.

        Raises:
            BadRequest: If the OAuth2 response is invalid.
        """
        url = str(request.url)
        parsed = urllib.parse.urlparse(url)
        state = urllib.parse.parse_qs(parsed.query).get('state')

        if not state:
            raise BadRequest("Invalid oauth2 response.")

        try:
            token = self.oauth.fetch_token(
                token_url=TOKEN_URL,
                client_secret=self.client_secret,
                authorization_response=url
            )
        except Exception as e:
            raise BadRequest("Invalid oauth2 response.")

        return token, state[0]