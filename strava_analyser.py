from typing import Any, Dict, List

import json
import time
import datetime
import sys
from api_client import ApiClient
from colorama import Fore, Style

class StravaAnalyser:
  ACTIVITIES_FILE = "activities.json"

  def __init__(self):
    self.api_client = ApiClient()
  
  @staticmethod
  def print_efforts(efforts) -> None:
    print("--------------------------------------------------------------")
    print(f"Segment: {efforts[0]['name']}")
    print("--------------------------------------------------------------")

    efforts.sort(key=lambda x: x["elapsed_time"])
    top = list(map(lambda x : x["id"], efforts))
    efforts.sort(key=lambda x: x["start_date"], reverse=True)
    
    for effort in efforts:
      seconds = effort["elapsed_time"]
      date =  datetime.datetime.strptime(effort["start_date"],"%Y-%m-%dT%H:%M:%SZ").strftime("%d.%m.%Y")
      text = f"{date}: {datetime.timedelta(seconds=seconds)}"

      if top.index(effort["id"]) == 0:
        print(Fore.LIGHTYELLOW_EX, f"{text} PR")
      elif top.index(effort["id"]) == 1:
        print(Fore.LIGHTBLUE_EX, text)
      elif top.index(effort["id"]) == 2:
        print(Fore.RED, text)
      else:
        print(Style.RESET_ALL, text)

  def get_activity_list(self) -> List[Dict]:
    PER_PAGE = 200
    page = 1
    activities = []

    while True:
      activities_response = self.api_client.get_activity_list(PER_PAGE, page)

      if (not activities_response):
        break

      activities.extend(activities_response)
      page += 1

    return activities

  def update_activities(self) -> None:
    REQUEST_LIMIT = 85
    TWENTY_MINS_IN_SEC = 60*20
    all_fetched_activities = []
    
    fetched_list = self.get_activity_list()

    with open(self.ACTIVITIES_FILE) as file:
      stored_activities: List = json.load(file)

    fetched_ids = [activity["id"] for activity in fetched_list]
    stored_activities_ids = [activity["id"] for activity in stored_activities]
    activities_to_fetch = list(filter(lambda x: x not in stored_activities_ids, fetched_ids))

    print(f"Stored activity list updated by {len(activities_to_fetch)} activities.")

    while activities_to_fetch:
      iteration_count = len(activities_to_fetch) if len(activities_to_fetch) < REQUEST_LIMIT else REQUEST_LIMIT

      for _ in range(iteration_count):
        id = activities_to_fetch.pop()
        print(f"Fetching activity: {id}")
        activity_response = self.api_client.get_activity(id)
        all_fetched_activities.append(activity_response)

      if not activities_to_fetch:
        break

      print(f"Fetched {len(all_fetched_activities)} activities. Remaining {len(activities_to_fetch)}. Wait 20 minutes for next fetch.")
      time.sleep(TWENTY_MINS_IN_SEC)

    stored_activities.extend(all_fetched_activities)

    with open(self.ACTIVITIES_FILE, "w") as file:
      json.dump(stored_activities, file)

  def get_segment_efforts(self, id: int) -> None:
    print(f"Getting efforts for segment id: {id}")

    segment_map = {}

    with open(self.ACTIVITIES_FILE) as file:
      stored_activities: List = json.load(file)

    for activity in stored_activities:
      for segment_effort in activity["segment_efforts"]:
        segment_id = segment_effort["segment"]["id"]

        if (segment_id in segment_map):
          segment_map[segment_id].append(segment_effort)
        else:
          segment_map[segment_id] = [segment_effort]

    try:
      current_segment_efforts: List[Any] = segment_map[id]
      self.print_efforts(current_segment_efforts)
    
    except KeyError as err:
      print(f"Requested segment id {err} not available. Ensure that id is correct or try to update activity list.")


if __name__ == "__main__":
  if len(sys.argv) < 2:
    print("Argument segment ID missing.")
  else:
    requested_segment_id = int(sys.argv[1])
    strava_analyser = StravaAnalyser()

    if len(sys.argv) > 2 and sys.argv[2] == "update":
      strava_analyser.update_activities()

    strava_analyser.get_segment_efforts(requested_segment_id)
