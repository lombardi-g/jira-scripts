import csv
import os
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


load_dotenv()

API_TOKEN = os.getenv("JIRA_API_TOKEN")
EMAIL = os.getenv("JIRA_EMAIL")
BASE_URL = os.getenv("JIRA_BASE_URL", "").rstrip("/")
FIELD_NUMBER = os.getenv("JIRA_FIELD_NUMBER")
INPUT_FILE_PATH = os.getenv("INPUT_FILE_PATH", "OptionsList.csv")

REQUIRED_VARS = {
    "JIRA_API_TOKEN": API_TOKEN,
    "JIRA_EMAIL": EMAIL,
    "JIRA_BASE_URL": BASE_URL,
    "JIRA_FIELD_NUMBER": FIELD_NUMBER,
}
missing = [key for key, value in REQUIRED_VARS.items() if not value]
if missing:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing)}"
    )

AUTH = HTTPBasicAuth(EMAIL, API_TOKEN)
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def get_field_context_id(field_num):
    url = f"{BASE_URL}/rest/api/3/field/customfield_{field_num}/context"
    response = requests.get(url, headers=HEADERS, auth=AUTH)

    if response.status_code == 200:
        data = response.json()
        contexts = data.get("values", [])
        if contexts:
            return contexts[0].get("id")
    print(
        f"[ERROR] Could not fetch contexts for customfield_{field_num}: {response.text}"
    )
    return None


def add_custom_field_options(context_id, options):
    """Creates new options using the current Jira Cloud v3 endpoint."""
    url = f"{BASE_URL}/rest/api/3/field/customfield_{FIELD_NUMBER}/context/{context_id}/option"
    payload = {"options": [{"value": opt} for opt in options]}
    return requests.post(url, json=payload, headers=HEADERS, auth=AUTH)


def process_options():
    print("Starting option import...")

    if not os.path.exists(INPUT_FILE_PATH):
        print(f"[ERROR] File not found at: {os.path.abspath(INPUT_FILE_PATH)}")
        return

    context_id = get_field_context_id(FIELD_NUMBER)
    if not context_id:
        print("[ABORTED] Missing Context ID.")
        return

    options_to_add = []
    with open(INPUT_FILE_PATH, mode="r", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            option_val = row.get("Options", "").strip()
            if option_val:
                options_to_add.append(option_val)

    if not options_to_add:
        print("[WARNING] No options found in CSV.")
        return

    print(
        f"Found {len(options_to_add)} options. Adding to field customfield_{FIELD_NUMBER} (Context: {context_id})..."
    )

    response = add_custom_field_options(context_id, options_to_add)

    if response.status_code in (200, 201):
        print(
            f"[SUCCESS] Successfully added {len(options_to_add)} options to context '{context_id}'."
        )
    else:
        print(f"[FAILED] HTTP {response.status_code}: {response.text}")


if __name__ == "__main__":
    process_options()