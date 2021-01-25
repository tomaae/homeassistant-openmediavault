"""OpenMediaVault API."""

import json
import logging
from os import path
from pickle import dump as pickle_dump
from pickle import load as pickle_load
from threading import Lock
from time import time

import requests
from voluptuous import Optional

_LOGGER = logging.getLogger(__name__)

# ---------------------------
#   load_cookies
# ---------------------------
def load_cookies(filename: str) -> Optional(dict):
    """Load cookies from file."""
    if path.isfile(filename):
        with open(filename, "rb") as f:
            return pickle_load(f)
    return None


# ---------------------------
#   save_cookies
# ---------------------------
def save_cookies(filename: str, data: dict):
    """Save cookies to file."""
    with open(filename, "wb") as f:
        pickle_dump(data, f)


# ---------------------------
#   OpenMediaVaultAPI
# ---------------------------
class OpenMediaVaultAPI(object):
    """Handle all communication with OMV."""

    def __init__(self, hass, host, username, password, use_ssl=False, verify_ssl=True):
        """Initialize the OMV API."""
        self._hass = hass
        self._host = host
        self._use_ssl = use_ssl
        self._username = username
        self._password = password
        self._protocol = "https" if self._use_ssl else "http"
        self._ssl_verify = verify_ssl
        if not self._use_ssl:
            self._ssl_verify = True
        self._resource = f"{self._protocol}://{self._host}/rpc.php"

        self.lock = Lock()

        self._connection = None
        self._cookie_jar = None
        self._cookie_jar_file = self._hass.config.path(".omv_cookies.json")
        self._connected = False
        self._reconnected = False
        self._connection_epoch = 0
        self._connection_retry_sec = 58
        self.error = None
        self.connection_error_reported = False
        self.accounting_last_run = None

    # ---------------------------
    #   has_reconnected
    # ---------------------------
    def has_reconnected(self) -> bool:
        """Check if API has reconnected."""
        if self._reconnected:
            self._reconnected = False
            return True

        return False

    # ---------------------------
    #   connection_check
    # ---------------------------
    def connection_check(self) -> bool:
        """Check if API is connected."""
        if not self._connected or not self._connection:
            if self._connection_epoch > time() - self._connection_retry_sec:
                return False

            if not self.connect():
                return False

        return True

    # ---------------------------
    #   disconnect
    # ---------------------------
    def disconnect(self, location="unknown", error=None):
        """Disconnect API."""
        if not error:
            error = "unknown"

        if not self.connection_error_reported:
            if location == "unknown":
                _LOGGER.error("OpenMediaVault %s connection closed", self._host)
            else:
                _LOGGER.error(
                    "OpenMediaVault %s error while %s : %s", self._host, location, error
                )

            self.connection_error_reported = True

        self._reconnected = False
        self._connected = False
        self._connection = None
        self._connection_epoch = 0

    # ---------------------------
    #   connect
    # ---------------------------
    def connect(self) -> bool:
        """Connect API."""
        self.error = ""
        self._connected = False
        self._connection_epoch = time()
        self._connection = requests.Session()
        self._cookie_jar = requests.cookies.RequestsCookieJar()

        # Load cookies
        cookies = load_cookies(self._cookie_jar_file)
        if cookies:
            self._connection.cookies.update(cookies)

        self.lock.acquire()
        try:
            response = self._connection.post(
                self._resource,
                data=json.dumps(
                    {
                        "service": "session",
                        "method": "login",
                        "params": {
                            "username": self._username,
                            "password": self._password,
                        },
                    }
                ),
                verify=self._ssl_verify,
            )
            data = response.json()

            if data["error"] is not None:
                if not self.connection_error_reported:
                    _LOGGER.error(
                        "OpenMediaVault %s unable to connect: %s",
                        self._host,
                        data["error"]["message"],
                    )
                    self.connection_error_reported = True

                self.error_to_strings("%s" % data["error"]["message"])
                self._connection = None
                self.lock.release()
                return False

            if not data["response"]["authenticated"]:
                _LOGGER.error("OpenMediaVault %s authentication failed", self._host)
                self.error_to_strings()
                self._connection = None
                self.lock.release()
                return False

        except requests.exceptions.ConnectionError as api_error:
            _LOGGER.error(
                "OpenMediaVault %s connection error: %s", self._host, api_error
            )
            self.error_to_strings("%s" % api_error)
            self._connection = None
            self.lock.release()
            return False
        except:
            self.disconnect("connect")
            self.lock.release()
            return None

        else:
            if self.connection_error_reported:
                _LOGGER.warning("OpenMediaVault %s reconnected", self._host)
                self.connection_error_reported = False
            else:
                _LOGGER.debug("OpenMediaVault %s connected", self._host)

            self._connected = True
            self._reconnected = True
            self.lock.release()

        # Save cookies
        if self._connected:
            for cookie in self._connection.cookies:
                self._cookie_jar.set_cookie(cookie)

            save_cookies(self._cookie_jar_file, self._cookie_jar)

        return self._connected

    # ---------------------------
    #   error_to_strings
    # ---------------------------
    def error_to_strings(self, error=""):
        """Translate error output to error string."""
        self.error = "cannot_connect"
        if "Incorrect username or password" in error:
            self.error = "invalid_auth"

        if "certificate verify failed" in error:
            self.error = "ssl_verify_failed"

    # ---------------------------
    #   connected
    # ---------------------------
    def connected(self) -> bool:
        """Return connected boolean."""
        return self._connected

    # ---------------------------
    #   query
    # ---------------------------
    def query(self, service, method, params=None, options=None) -> Optional(list):
        """Retrieve data from OMV."""
        if not self.connection_check():
            return None

        if not params:
            params = {}

        if not options:
            options = {"updatelastaccess": False}

        self.lock.acquire()
        try:
            _LOGGER.debug(
                "OpenMediaVault %s query: %s, %s, %s, %s",
                self._host,
                service,
                method,
                params,
                options,
            )
            response = self._connection.post(
                self._resource,
                data=json.dumps(
                    {
                        "service": service,
                        "method": method,
                        "params": params,
                        "options": options,
                    }
                ),
                verify=self._ssl_verify,
            )

            data = response.json()
            _LOGGER.debug("OpenMediaVault %s query response: %s", self._host, data)

        except (
            requests.exceptions.ConnectionError,
            json.decoder.JSONDecodeError,
        ) as api_error:
            _LOGGER.warning("OpenMediaVault %s unable to fetch data", self._host)
            self.disconnect("query", api_error)
            self.lock.release()
            return None
        except:
            self.disconnect("query")
            self.lock.release()
            return None

        self.lock.release()
        if data is not None and data["error"] is not None:
            error_message = data["error"]["message"]
            error_code = data["error"]["code"]
            if (
                error_code == 5001
                or error_code == 5002
                or error_message == "Session not authenticated."
                or error_message == "Session expired."
            ):
                _LOGGER.debug("OpenMediaVault %s session expired", self._host)
                if self.connect():
                    return self.query(service, method, params, options)

        return data["response"]
