from .client import MomentumClient
from .functionality.borgere import BorgereClient

class MomentumClientManager:
    def __init__(
            self,
            base_url: str,
            client_id: str,
            client_secret: str,
            api_key: str,
            resource: str
    ) -> None:
        # initialize functionality classes
        self._client = MomentumClient(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            api_key=api_key,
            resource=resource
        )

        self._borgere_client = BorgereClient(self._client)

    @property
    def borgere(self) -> BorgereClient:
        """Access to the BorgereClient for citizen-related operations."""
        return self._borgere_client
