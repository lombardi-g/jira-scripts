import csv
import os
from requests.auth import HTTPBasicAuth
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("JIRA_BASE_URL", "").rstrip("/")
EMAIL = os.getenv("JIRA_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
CSV_PATH = os.getenv("INPUT_FILE_PATH")

SCREEN_ID = 40219


def get_screen_tab_id(auth: HTTPBasicAuth, screen_id: int) -> int:
    """Fetches the default/first tab ID for the specified screen.

    Jira adds fields to a tab within a screen.
    """
    url = f"{BASE_URL}/rest/api/3/screens/{screen_id}/tabs"
    response = requests.get(
        url, auth=auth, headers={"Accept": "application/json"}
    )
    response.raise_for_status()

    tabs = response.json()
    if not tabs:
        raise ValueError(f"No tabs found on screen {screen_id}.")

    # Returns the first tab (usually 'Field Tab')
    return tabs[0]["id"]


def add_field_to_tab(
    auth: HTTPBasicAuth, screen_id: int, tab_id: int, field_id: str
):
    """Adds a custom field to the specified screen tab."""
    url = f"{BASE_URL}/rest/api/3/screens/{screen_id}/tabs/{tab_id}/fields"
    payload = {"fieldId": field_id}
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    response = requests.post(url, json=payload, auth=auth, headers=headers)

    if response.status_code == 200:
        print(f" Successfully added {field_id} to screen {screen_id}.")
    elif response.status_code == 400:
        print(f" Skipping {field_id}: Already on screen or invalid ID.")
    elif response.status_code == 404:
        print(f" Error {field_id}: Field or Screen not found.")
    else:
        print(
            f" Failed to add {field_id} (HTTP {response.status_code}): {response.text}"
        )


def read_custom_fields_from_csv(file_path: str) -> list[str]:
    """Reads custom field IDs line-by-line from the CSV file, skipping the header."""
    fields = []
    with open(file_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip the header row ('Options')
        for row in reader:
            if row and row[0].strip():
                field_id = row[0].strip()
                # Ensure the ID format matches Jira's internal format (e.g. customfield_10010)
                if field_id.isdigit():
                    field_id = f"customfield_{field_id}"
                fields.append(field_id)
    return fields


def main():
    if not all([BASE_URL, EMAIL, API_TOKEN, CSV_PATH]):
        raise ValueError(
            "Missing one or more required variables in your .env file."
        )

    auth = HTTPBasicAuth(EMAIL, API_TOKEN)

    print(f"Reading fields from: {CSV_PATH}")
    custom_field_ids = read_custom_fields_from_csv(CSV_PATH)
    print(f"Found {len(custom_field_ids)} field(s) to add.")

    print(f"Retrieving tab information for screen ID {SCREEN_ID}...")
    tab_id = get_screen_tab_id(auth, SCREEN_ID)
    print(f"Targeting Screen {SCREEN_ID} -> Tab {tab_id}")

    for field_id in custom_field_ids:
        add_field_to_tab(auth, SCREEN_ID, tab_id, field_id)


if __name__ == "__main__":
    main()