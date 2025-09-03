"""
MomentumClientManager - A facade/factory for all Momentum functionality clients.

This manager simplifies the instantiation of multiple clients by providing
a single entry point with lazy-loaded properties for each functionality.
"""

from typing import Optional
from .client import MomentumClient
from .functionality.borgere import BorgereClient
from .functionality.virksomheder import VirksomhederClient
from .functionality.markeringer import MarkeringerClient


class MomentumClientManager:
    """
    Manager til nem adgang til alle Momentum funktionalitets-klienter.

    VIGTIGT: Brug altid denne manager i stedet for at oprette individuelle klienter.
    Dette sikrer korrekt konfiguration og lazy loading.

    Eksempel:
        momentum = MomentumClientManager(base_url="...", client_id="...", client_secret="...", api_key="...", resource="...")
        borger = momentum.borgere.hent_borger("1234567890")
        markering = momentum.borgere.opret_markering("test", borger, datetime.date.today())
        virksomheder = momentum.virksomheder.hent_virksomheder(filters={}, søgeterm="test")
    """

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        api_key: str,
        resource: str,
        timeout: float = 60.0
    ):
        """
        Initialize the MomentumClientManager.

        Args:
            base_url: The base URL for the Momentum API
            client_id: The OAuth2 client ID
            client_secret: The OAuth2 client secret
            api_key: The API key for authentication
            resource: The resource identifier
            timeout: Request timeout in seconds (default: 60.0)
        """
        self._base_url = base_url
        self._client_id = client_id
        self._client_secret = client_secret
        self._api_key = api_key
        self._resource = resource

        # Store configuration for lazy loading
        self._config = {"timeout": timeout}

        # Lazy-loaded clients
        self._momentum_client: Optional[MomentumClient] = None
        self._borgere_client: Optional[BorgereClient] = None
        self._virksomheder_client: Optional[VirksomhederClient] = None
        self._markeringer_client: Optional[MarkeringerClient] = None

    @property
    def momentum_client(self) -> MomentumClient:
        """Get the base MomentumClient (lazy-loaded with configuration)."""
        if self._momentum_client is None:
            self._momentum_client = MomentumClient(
                base_url=self._base_url,
                client_id=self._client_id,
                client_secret=self._client_secret,
                api_key=self._api_key,
                resource=self._resource,
            )
        return self._momentum_client

    @property
    def borgere(self) -> BorgereClient:
        """Get the BorgereClient (lazy-loaded)."""
        if self._borgere_client is None:
            self._borgere_client = BorgereClient(self.momentum_client)
        return self._borgere_client

    @property
    def virksomheder(self) -> VirksomhederClient:
        """Get the VirksomhederClient (lazy-loaded)."""
        if self._virksomheder_client is None:
            self._virksomheder_client = VirksomhederClient(self.momentum_client)
        return self._virksomheder_client

    @property
    def markeringer(self) -> MarkeringerClient:
        """Get the MarkeringerClient (lazy-loaded)."""
        if self._markeringer_client is None:
            self._markeringer_client = MarkeringerClient(self.momentum_client)
        return self._markeringer_client
