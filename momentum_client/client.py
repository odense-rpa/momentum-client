import httpx
import logging

from urllib.parse import urljoin
from .hooks import create_response_logging_hook
from authlib.integrations.httpx_client import OAuth2Client

class MomentumClient:
    
    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        api_key: str, 
        resource: str
    ) -> None:
        # Set up logging
        self.logger = logging.getLogger(__name__)
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("httpcore").setLevel(logging.WARNING)

        # Create response logging hook
        response_hook = create_response_logging_hook(logger=self.logger)
        hooks = {'response': [response_hook]}
        
        # Store configuration
        self.api_key = api_key
        self._base_url = base_url
        self._token_url = "https://login.microsoftonline.com/momentumb2c.onmicrosoft.com/oauth2/token"
        self._timeout = 30

        self._client = OAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            token_endpoint=self._token_url,
            timeout=self._timeout,
            event_hooks=hooks
        )

        # Automatically fetch the token during initialization using client credentials grant
        self._client.fetch_token(
            grant_type='client_credentials',
            resource=resource
        )

        # Set default headers on the client
        self._client.headers.update({
            'apikey': self.api_key,
            'Authorization': f'Bearer {self._client.token["access_token"]}'
        })


    def _normalize_url(self, endpoint: str) -> str:
        """Ensure the URL is absolute, handling relative URLs."""
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        
        # Remove leading slash from endpoint to avoid urljoin replacing the base path
        endpoint = endpoint.lstrip("/")
        return urljoin(self._base_url + "/", endpoint)

    def get(self, endpoint: str, **kwargs) -> httpx.Response:
        """
        Perform GET request to the specified endpoint.

        :param endpoint: API endpoint (relative or absolute URL)
        :param kwargs: Additional arguments passed to httpx
        :return: HTTP response
        """
        url = self._normalize_url(endpoint)
        response = self._client.get(url, **kwargs)
        response.raise_for_status()
        return response

    def post(self, endpoint: str, json: dict | None = None, **kwargs) -> httpx.Response:
        """
        Perform POST request to the specified endpoint.

        :param endpoint: API endpoint (relative or absolute URL)
        :param json: JSON data to send in request body
        :param kwargs: Additional arguments passed to httpx
        :return: HTTP response
        """
        url = self._normalize_url(endpoint)
        response = self._client.post(url, json=json, **kwargs)
        response.raise_for_status()
        return response

    def put(self, endpoint: str, json: dict | None = None, **kwargs) -> httpx.Response:
        """
        Perform PUT request to the specified endpoint.

        :param endpoint: API endpoint (relative or absolute URL)
        :param json: JSON data to send in request body
        :param kwargs: Additional arguments passed to httpx
        :return: HTTP response
        """
        url = self._normalize_url(endpoint)
        response = self._client.put(url, json=json, **kwargs)
        response.raise_for_status()
        return response

    def delete(self, endpoint: str, **kwargs) -> httpx.Response:
        """
        Perform DELETE request to the specified endpoint.

        :param endpoint: API endpoint (relative or absolute URL)
        :param kwargs: Additional arguments passed to httpx
        :return: HTTP response
        """
        url = self._normalize_url(endpoint)
        response = self._client.delete(url, **kwargs)
        response.raise_for_status()
        return response
