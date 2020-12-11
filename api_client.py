from typing import Dict, List

import requests
import json
import time

from requests.models import Response

class ApiClient:
  API = "https://www.strava.com/api/v3"
  TOKENS_FILE = "tokens.json"
  ACCOUNT_FILE = "account.json"

  def __init__(self) -> None:
    self.access_token = None

  def authenticate(self, code):
    with open(self.ACCOUNT_FILE) as file:
      account = json.load(file)

    response = requests.post(f"{self.API}/oauth/token", {
      "client_id": account["client_id"],
      "client_secret": account["client_secret"],
      "code": code,
      "grant_type": "authorization_code"
    })

    tokens = response.json()
    with open(self.TOKENS_FILE, "w") as file:
      json.dump(tokens, file)

    self.access_token = tokens["access_token"]

  def refresh_tokens(self) -> None:
    with open(self.ACCOUNT_FILE) as json_file:
      account = json.load(json_file)
    with open(self.TOKENS_FILE) as json_file:
      strava_tokens = json.load(json_file)

    if strava_tokens["expires_at"] < time.time():
      response = requests.post(f"{self.API}/oauth/token", {
        "client_id": account["client_id"],
        "client_secret": account["client_secret"],
        "refresh_token": strava_tokens["refresh_token"],
        "grant_type": "refresh_token"
      })

      new_tokens = response.json()
      with open(self.TOKENS_FILE, "w") as json_file:
        json.dump(new_tokens, json_file)

      self.access_token = new_tokens["access_token"]

    self.access_token = strava_tokens["access_token"]

  def make_authorised_request(self, endpoint: str, method: str) -> Response:
    self.refresh_tokens()
    print(f"Making request: {endpoint}")
    request = getattr(requests, method)

    return request(f"{self.API}{endpoint}", headers={"Authorization": f"Bearer {self.access_token}"})

  def get_activity_list(self, per_page = 200, page = 1) -> List[Dict]:
    response = self.make_authorised_request(
      f"/athlete/activities?per_page={per_page}&page={page}",
      "get",
    )

    return response.json()

  def get_activity(self, id: int) -> Dict:
    response = self.make_authorised_request(
      f"/activities/{id}",
      "get",
    )

    return response.json()