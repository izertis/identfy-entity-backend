import requests

from common.utils.entity_auth_credentials import EntityAuthCredentials


def get_bearer_token(token_url: str, client_id: str, client_secret: str) -> str:
    """
    Obtains a Bearer Token using OAuth2 Client Credentials.

    :param token_url: URL of the authentication server to obtain the token.
    :param client_id: Client ID registered with the authentication server.
    :param client_secret: Secret associated with the client.
    :return: The Bearer Token as a string.
    :raises: Exception if an error occurs while obtaining the token.
    """
    try:
        response = requests.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token", "")
    except requests.RequestException as e:
        raise Exception(f"Error al obtener el Bearer Token: {e}")


def add_entity_auth_headers(original_headers: dict, entity_auth_config: any) -> dict:
    """
    Adds the necessary headers to authenticate with the entity's API.

    :param headers: Current headers.
    :param entity_auth_config: Authentication configuration for the entity.
    :return: Current headers including the required ones.
    """

    if original_headers is None:
        headers = {}
    else:
        headers = original_headers.copy()

    if entity_auth_config is None:
        return headers

    auth_credentials = EntityAuthCredentials.from_input(entity_auth_config)
    if auth_credentials.is_valid():
        if auth_credentials.is_api_key_valid():
            headers[auth_credentials.auth_header] = auth_credentials.api_key
        elif auth_credentials.is_oauth2_valid():
            token = get_bearer_token(
                auth_credentials.token_url,
                auth_credentials.client_id,
                auth_credentials.client_secret,
            )
            headers[auth_credentials.auth_header] = f"Bearer {token}"

    return headers
