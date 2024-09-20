# %User

Here is a long python file with many dunder methods:

```python
import webbrowser
from pathlib import Path

import requests
from oauthlib.oauth2 import WebApplicationClient
from pydantic import BaseModel, field_validator


class User(BaseModel):
    """Oject to store user configuration information.

    Parameters
    ----------
    oauth_client_id: str
        OAuth2 client ID.
    oauth_client_secret: str
        OAuth2 client secret.
    credentials_path: str
        Path to a user credentials JSON file. If this does not exist, this will
        be the path where the user credentials will be stored.

    Raises
    ------
    ValidationError
        If:
        - arguments are not of the correct type.
        - `oauth_client_id` does not end with '.apps.googleusercontent.com'.
        - `credentials_path` is not a JSON file.
        - `port` is not between 1024 and 65535 (privileged ports).
    """

    oauth_client_id: str
    oauth_client_secret: str
    credentials_path: str

    @field_validator("oauth_client_id", mode="after")
    def validate_oauth_client_id(cls, v):
        """Validate `oauth_client_id` to ensure correct format."""
        if not v.endswith(".apps.googleusercontent.com"):
            raise ValueError(
                "`oauth_client_id` must end with "
                "'.apps.googleusercontent.com'."
            )
        return v

    @field_validator("credentials_path", mode="after")
    def validate_and_convertcredentials_path(cls, v):
        """Validate `credentials_path` is JSON file and convert to Pathlib."""
        path = Path(v).resolve()
        if path.suffix != ".json":
            raise ValueError("`credentials_path` must be a valid JSON file.")
        return path


class _UserCredentials(BaseModel):
    """Object to store user credentials."""

    expires_at: datetime.datetime
    id_token: str
    refresh_token: str

    @staticmethod
    def from_dict(creds: dict) -> "_UserCredentials":
        """Create a `_UserCredentials` object from a dictionary."""
        # convert the expires_in to expires_at if it exists
        if "expires_at" not in creds.keys():
            creds["expires_at"] = datetime.datetime.now(
                datetime.timezone.utc
            ) + datetime.timedelta(seconds=creds["expires_in"])
        return _UserCredentials(
            expires_at=creds["expires_at"],
            id_token=creds["id_token"],
            refresh_token=creds["refresh_token"],
        )

    @staticmethod
    def from_json(path: str) -> "_UserCredentials":
        """Create a `_UserCredentials` object from a JSON file."""
        with open(path, "r") as f:
            creds = json.load(f)
        return _UserCredentials.from_dict(creds)

    def to_dict(self) -> dict:
        """Convert the `_UserCredentials` object to a dictionary."""
        return {
            "expires_at": self.expires_at.isoformat(),
            "id_token": self.id_token,
            "refresh_token": self.refresh_token,
        }

    def to_json(self, path: str) -> None:
        """Write the user credentials to a JSON file."""
        with open(path, "w") as f:
            json.dump(
                self.to_dict(),
                f,
                ensure_ascii=True,
                indent=4,
                sort_keys=True,
            )

    def token_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.datetime.now(datetime.timezone.utc) >= self.expires_at


class UserIAPClient:
    """Client to handle user IAP authentication and requests.

    Parameters
    ----------
    user: User
        User object with the OAuth2 client ID and secret.
    port: int, optional
        Port to run the local server on. Default is 4444.

    Raises
    ------
    ValueError
        If:
        - `user` is not a `gcp_iap_auth.user.User` object.
        - `port` is not an integer.
        - `port` is not between 1024 and 65535 (privileged ports).
    """

    def __init__(self, user: User, port: int = 4444):
        if not isinstance(user, User):
            raise TypeError(
                f"`user` must be a `User` object. Got "
                f"type '{type(user).__name__}"
            )
        if not isinstance(port, int):
            raise TypeError(
                f"`port` must be an integer. Got port={port} "
                f"(type '{type(port).__name__}')"
            )
        if port < 1024 or port > 65535:
            raise ValueError(
                "`port` must be between 1024 and 65535 (non privileged ports)."
                f" Got port={port}"
            )
        self.__user = user
        self.__port = port
        self.__host = "127.0.0.1"
        self.__redirect_uri = f"http://localhost:{port}"
        self.__auth_uri = "https://accounts.google.com/o/oauth2/v2/auth"
        self.__token_uri = "https://oauth2.googleapis.com/token"  # noqa: S105
        self.__local_creds_available = self.__user.credentials_path.exists()
        self.__user_authenticated = False
        self.__creds = None

    def request(self, url, method="GET", **kwargs):
        """Make a request to the IAP-protected URL.

        Parameters
        ----------
        url: str
            URL to make the request to.
        method: str, optional
            HTTP method to use for the request. Default is 'GET'.
        **kwargs:
            Additional keyword arguments to pass to the request.

        Returns
        -------
        requests.Response
            Response object from the request.

        Raises
        ------
        ValueError
            If `method` is not a valid HTTP method.
        """
        if method not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError(
                f"`method` must be a valid HTTP method. Got method={method}"
            )
        if not self.__user_authenticated:
            self.__authenticate()
        else:
            # refresh the token if it has expired
            if self.__creds.token_expired():
                self.__refresh_token()
        return self.__make_request(url, method, **kwargs)

    def __authenticate(self):
        """Authenticate the user and store the credentials if needed."""
        if self.__local_creds_available:
            self.__get_or_refresh_local_creds()
        else:
            self.__get_user_authentication()
        self.__user_authenticated = True

    def __get_user_authentication(self):
        """Authenticate user using the OAuth2 flow."""
        auth_code = self.__get_auth_code()
        self.__get_creds_from_auth_code(auth_code)

    def __get_auth_code(self):
        """Get the client code from the user."""
        oauth2_code_url = self.__prepare_oauth2_code_url()

        # open a socket to listen for the oauth2 code
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.__host, self.__port))
            webbrowser.open_new(oauth2_code_url)
            s.listen(1)
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if data != b"":
                        break

        # remind the user to close the webpage before continuing
        _ = input("Please close the webpage. Press enter to continue...")

        if code_search := re.search("code=(.*)&scope", data.decode("utf-8")):
            code = code_search.group(1)
        else:
            raise ValueError("Could not find the OAuth2 code in the response.")

        return code

    def __prepare_oauth2_code_url(self):
        """Prepare the OAuth2 code URL for the user."""
        code_client = WebApplicationClient(
            client_id=self.__user.oauth_client_id,
            response_type="code",
        )
        return code_client.prepare_request_uri(
            uri=self.__auth_uri,
            scope=["openid", "email"],
            access_type="offline",
            redirect_uri=self.__redirect_uri,
            cred_ref="true",
        )

    def __get_creds_from_auth_code(self, auth_code):
        """Get and store the OAuth2 token credential using the auth code."""
        r = requests.post(
            self.__token_uri,
            json=self.__prepare_oauth2_token_payload_auth_code(auth_code),
            timeout=10,
        )
        if not r.ok:
            raise ValueError(
                f"Failed to get credentials from auth code. "
                f"Status code: {r.status_code}"
            )
        self.__creds = _UserCredentials.from_dict(r.json())
        self.__creds.to_json(self.__user.credentials_path)

    def __prepare_oauth2_token_payload_auth_code(self, auth_code):
        """Prepare the OAuth2 token payload using the auth code."""
        return {
            "client_id": self.__user.oauth_client_id,
            "client_secret": self.__user.oauth_client_secret,
            "code": auth_code.replace("%2F", "/"),
            "redirect_uri": self.__redirect_uri,
            "grant_type": "authorization_code",
        }

    def __get_or_refresh_local_creds(self):
        """Get or refresh the user credentials from the local file."""
        self.__creds = _UserCredentials.from_json(self.__user.credentials_path)
        if self.__creds.token_expired():
            self.__refresh_token()

    def __refresh_token(self):
        """Refresh the user token using the refresh token."""
        r = requests.post(
            self.__token_uri,
            json=self.__prepare_oauth2_token_payload_refresh_token(),
            timeout=10,
        )
        if not r.ok:
            raise ValueError(
                f"Failed to refresh token. Status code: {r.status_code}"
            )

        # add the refresh token back to the response and update the creds
        response = r.json()
        response["refresh_token"] = self.__creds.refresh_token
        self.__creds = _UserCredentials.from_dict(response)
        self.__creds.to_json(self.__user.credentials_path)

    def __prepare_oauth2_token_payload_refresh_token(self):
        """Prepare the OAuth2 token payload using the refresh token."""
        return {
            "client_id": self.__user.oauth_client_id,
            "client_secret": self.__user.oauth_client_secret,
            "refresh_token": self.__creds.refresh_token,
            "grant_type": "refresh_token",
        }

    def __make_request(self, url, method, **kwargs):
        """Make a request to the IAP-protected URL."""
        # set a default timeout of 60 seconds if not provided
        if "timeout" not in kwargs.keys():
            kwargs["timeout"] = 60

        # using noqa: S113 since timeout is always made a valid kwarg
        return requests.request(  # noqa: S113
            method,
            url,
            headers={
                "Authorization": f"Bearer {self.__creds.id_token}",
            },
            **kwargs,
        )
```

I would like to read and understand the control flow of the code, but the many dunder methods and other methods make it difficult to follow the flow. Please rewrite the code, in the following way:

* inline every method that is called from some other method.
* Only refactor variable names when the variable would otherwise be duplicated or ambiguous
* Keep all docstrings in the code above the place where the code has been inlined
* Add a comment line giving the original name of the dunder method that has been inlined

Make sure the code is functionally identical and DO NOT lose any code!



# %Assistant

Here's the refactored code with inlined methods and preserved functionality:

```python
import webbrowser
from pathlib import Path
import socket
import re
import datetime
import json

import requests
from oauthlib.oauth2 import WebApplicationClient
from pydantic import BaseModel, field_validator


class User(BaseModel):
    """Oject to store user configuration information.

    Parameters
    ----------
    oauth_client_id: str
        OAuth2 client ID.
    oauth_client_secret: str
        OAuth2 client secret.
    credentials_path: str
        Path to a user credentials JSON file. If this does not exist, this will
        be the path where the user credentials will be stored.

    Raises
    ------
    ValidationError
        If:
        - arguments are not of the correct type.
        - `oauth_client_id` does not end with '.apps.googleusercontent.com'.
        - `credentials_path` is not a JSON file.
        - `port` is not between 1024 and 65535 (privileged ports).
    """

    oauth_client_id: str
    oauth_client_secret: str
    credentials_path: str

    @field_validator("oauth_client_id", mode="after")
    def validate_oauth_client_id(cls, v):
        """Validate `oauth_client_id` to ensure correct format."""
        if not v.endswith(".apps.googleusercontent.com"):
            raise ValueError(
                "`oauth_client_id` must end with "
                "'.apps.googleusercontent.com'."
            )
        return v

    @field_validator("credentials_path", mode="after")
    def validate_and_convertcredentials_path(cls, v):
        """Validate `credentials_path` is JSON file and convert to Pathlib."""
        path = Path(v).resolve()
        if path.suffix != ".json":
            raise ValueError("`credentials_path` must be a valid JSON file.")
        return path


class _UserCredentials(BaseModel):
    """Object to store user credentials."""

    expires_at: datetime.datetime
    id_token: str
    refresh_token: str

    @staticmethod
    def from_dict(creds: dict) -> "_UserCredentials":
        """Create a `_UserCredentials` object from a dictionary."""
        # convert the expires_in to expires_at if it exists
        if "expires_at" not in creds.keys():
            creds["expires_at"] = datetime.datetime.now(
                datetime.timezone.utc
            ) + datetime.timedelta(seconds=creds["expires_in"])
        return _UserCredentials(
            expires_at=creds["expires_at"],
            id_token=creds["id_token"],
            refresh_token=creds["refresh_token"],
        )

    @staticmethod
    def from_json(path: str) -> "_UserCredentials":
        """Create a `_UserCredentials` object from a JSON file."""
        with open(path, "r") as f:
            creds = json.load(f)
        return _UserCredentials.from_dict(creds)

    def to_dict(self) -> dict:
        """Convert the `_UserCredentials` object to a dictionary."""
        return {
            "expires_at": self.expires_at.isoformat(),
            "id_token": self.id_token,
            "refresh_token": self.refresh_token,
        }

    def to_json(self, path: str) -> None:
        """Write the user credentials to a JSON file."""
        with open(path, "w") as f:
            json.dump(
                self.to_dict(),
                f,
                ensure_ascii=True,
                indent=4,
                sort_keys=True,
            )

    def token_expired(self) -> bool:
        """Check if the token has expired."""
        return datetime.datetime.now(datetime.timezone.utc) >= self.expires_at


class UserIAPClient:
    """Client to handle user IAP authentication and requests.

    Parameters
    ----------
    user: User
        User object with the OAuth2 client ID and secret.
    port: int, optional
        Port to run the local server on. Default is 4444.

    Raises
    ------
    ValueError
        If:
        - `user` is not a `gcp_iap_auth.user.User` object.
        - `port` is not an integer.
        - `port` is not between 1024 and 65535 (privileged ports).
    """

    def __init__(self, user: User, port: int = 4444):
        if not isinstance(user, User):
            raise TypeError(
                f"`user` must be a `User` object. Got "
                f"type '{type(user).__name__}"
            )
        if not isinstance(port, int):
            raise TypeError(
                f"`port` must be an integer. Got port={port} "
                f"(type '{type(port).__name__}')"
            )
        if port < 1024 or port > 65535:
            raise ValueError(
                "`port` must be between 1024 and 65535 (non privileged ports)."
                f" Got port={port}"
            )
        self.__user = user
        self.__port = port
        self.__host = "127.0.0.1"
        self.__redirect_uri = f"http://localhost:{port}"
        self.__auth_uri = "https://accounts.google.com/o/oauth2/v2/auth"
        self.__token_uri = "https://oauth2.googleapis.com/token"  # noqa: S105
        self.__local_creds_available = self.__user.credentials_path.exists()
        self.__user_authenticated = False
        self.__creds = None

    def request(self, url, method="GET", **kwargs):
        """Make a request to the IAP-protected URL.

        Parameters
        ----------
        url: str
            URL to make the request to.
        method: str, optional
            HTTP method to use for the request. Default is 'GET'.
        **kwargs:
            Additional keyword arguments to pass to the request.

        Returns
        -------
        requests.Response
            Response object from the request.

        Raises
        ------
        ValueError
            If `method` is not a valid HTTP method.
        """
        if method not in ["GET", "POST", "PUT", "DELETE"]:
            raise ValueError(
                f"`method` must be a valid HTTP method. Got method={method}"
            )
        if not self.__user_authenticated:
            # Inline __authenticate method
            """Authenticate the user and store the credentials if needed."""
            if self.__local_creds_available:
                # Inline __get_or_refresh_local_creds method
                """Get or refresh the user credentials from the local file."""
                self.__creds = _UserCredentials.from_json(self.__user.credentials_path)
                if self.__creds.token_expired():
                    # Inline __refresh_token method
                    """Refresh the user token using the refresh token."""
                    r = requests.post(
                        self.__token_uri,
                        json={
                            "client_id": self.__user.oauth_client_id,
                            "client_secret": self.__user.oauth_client_secret,
                            "refresh_token": self.__creds.refresh_token,
                            "grant_type": "refresh_token",
                        },
                        timeout=10,
                    )
                    if not r.ok:
                        raise ValueError(
                            f"Failed to refresh token. Status code: {r.status_code}"
                        )

                    # add the refresh token back to the response and update the creds
                    response = r.json()
                    response["refresh_token"] = self.__creds.refresh_token
                    self.__creds = _UserCredentials.from_dict(response)
                    self.__creds.to_json(self.__user.credentials_path)
            else:
                # Inline __get_user_authentication method
                """Authenticate user using the OAuth2 flow."""
                # Inline __get_auth_code method
                """Get the client code from the user."""
                # Inline __prepare_oauth2_code_url method
                """Prepare the OAuth2 code URL for the user."""
                code_client = WebApplicationClient(
                    client_id=self.__user.oauth_client_id,
                    response_type="code",
                )
                oauth2_code_url = code_client.prepare_request_uri(
                    uri=self.__auth_uri,
                    scope=["openid", "email"],
                    access_type="offline",
                    redirect_uri=self.__redirect_uri,
                    cred_ref="true",
                )

                # open a socket to listen for the oauth2 code
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self.__host, self.__port))
                    webbrowser.open_new(oauth2_code_url)
                    s.listen(1)
                    conn, addr = s.accept()
                    with conn:
                        while True:
                            data = conn.recv(1024)
                            if data != b"":
                                break

                # remind the user to close the webpage before continuing
                _ = input("Please close the webpage. Press enter to continue...")

                if code_search := re.search("code=(.*)&scope", data.decode("utf-8")):
                    auth_code = code_search.group(1)
                else:
                    raise ValueError("Could not find the OAuth2 code in the response.")

                # Inline __get_creds_from_auth_code method
                """Get and store the OAuth2 token credential using the auth code."""
                r = requests.post(
                    self.__token_uri,
                    json={
                        "client_id": self.__user.oauth_client_id,
                        "client_secret": self.__user.oauth_client_secret,
                        "code": auth_code.replace("%2F", "/"),
                        "redirect_uri": self.__redirect_uri,
                        "grant_type": "authorization_code",
                    },
                    timeout=10,
                )
                if not r.ok:
                    raise ValueError(
                        f"Failed to get credentials from auth code. "
                        f"Status code: {r.status_code}"
                    )
                self.__creds = _UserCredentials.from_dict(r.json())
                self.__creds.to_json(self.__user.credentials_path)

            self.__user_authenticated = True
        else:
            # refresh the token if it has expired
            if self.__creds.token_expired():
                # Inline __refresh_token method (same as above)
                """Refresh the user token using the refresh token."""
                r = requests.post(
                    self.__token_uri,
                    json={
                        "client_id": self.__user.oauth_client_id,
                        "client_secret": self.__user.oauth_client_secret,
                        "refresh_token": self.__creds.refresh_token,
                        "grant_type": "refresh_token",
                    },
                    timeout=10,
                )
                if not r.ok:
                    raise ValueError(
                        f"Failed to refresh token. Status code: {r.status_code}"
                    )

                # add the refresh token back to the response and update the creds
                response = r.json()
                response["refresh_token"] = self.__creds.refresh_token
                self.__creds = _UserCredentials.from_dict(response)
                self.__creds.to_json(self.__user.credentials_path)

        # Inline __make_request method
        """Make a request to the IAP-protected URL."""
        # set a default timeout of 60 seconds if not provided
        if "timeout" not in kwargs.keys():
            kwargs["timeout"] = 60

        # using noqa: S113 since timeout is always made a valid kwarg
        return requests.request(  # noqa: S113
            method,
            url,
            headers={
                "Authorization": f"Bearer {self.__creds.id_token}",
            },
            **kwargs,
        )
```

This refactored version inlines all the methods called from other methods within the `UserIAPClient` class. The docstrings are preserved above the inlined code, and comments indicate the original method names. The functionality remains identical to the original code.