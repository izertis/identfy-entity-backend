import json
from typing import Optional


class EntityAuthCredentials:
    """
    Class for storing authentication information.
    Supports API Key and OAuth2 Client Credentials.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        auth_header: Optional[str] = "Authorization",
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        token_url: Optional[str] = None,
    ):
        """
        Initializes the authentication credentials.

        :param api_key: API key for API Key–based authentication.
        :param auth_header: Name of the authorization header.
        :param client_id: Client ID for OAuth2 Client Credentials.
        :param client_secret: Client secret for OAuth2 Client Credentials.
        :param token_url: URL to obtain the token using OAuth2 Client Credentials.
        """

        self.api_key = api_key
        self.auth_header = auth_header
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url

    def is_api_key_valid(self) -> bool:
        """Validates whether the API Key is configured."""
        return self.api_key is not None and self.api_key.strip() != ""

    def is_oauth2_valid(self) -> bool:
        """Validates whether the OAuth2 credentials are configured."""
        return (
            self.client_id is not None
            and self.client_secret is not None
            and self.token_url is not None
            and self.client_id.strip() != ""
            and self.client_secret.strip() != ""
            and self.token_url.strip() != ""
        )

    def is_valid(self) -> bool:
        """Validates whether any authentication method is configured."""
        return self.is_api_key_valid() or self.is_oauth2_valid()

    @staticmethod
    def from_input(data: str) -> "EntityAuthCredentials":
        """
        Creates an AuthCredentials object from a string representing
        an API Key directly or a JSON object with the required fields.

        :param data: String containing either an API Key or a JSON object.
        :return: An instance of AuthCredentials.
        """

        if data.strip().startswith("{"):
            try:
                parsed_data = json.loads(data)
                return EntityAuthCredentials(
                    api_key=parsed_data.get("api_key"),
                    auth_header=parsed_data.get("auth_header", "Authorization"),
                    client_id=parsed_data.get("client_id"),
                    client_secret=parsed_data.get("client_secret"),
                    token_url=parsed_data.get("token_url"),
                )
            except json.JSONDecodeError:
                pass

        return EntityAuthCredentials(api_key=data, auth_header="Authorization")

    def __repr__(self):
        return (
            f"AuthCredentials(api_key={'*****' if self.api_key else None}, "
            f"auth_header={self.auth_header}, "
            f"client_id={'*****' if self.client_id else None}, "
            f"client_secret={'*****' if self.client_secret else None}, "
            f"token_url={self.token_url})"
        )
