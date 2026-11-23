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
CONTEXT_ID = os.getenv("JIRA_CONTEXT_ID") 
INPUT_FILE_PATH = os.getenv("INPUT_FILE_PATH", "OptionsList.csv")

REQUIRED_VARS = {
    "JIRA_API_TOKEN": API_TOKEN,
    "JIRA_EMAIL": EMAIL,
    "JIRA_BASE_URL": BASE_URL,
    "JIRA_FIELD_NUMBER": FIELD_NUMBER,
    "JIRA_CONTEXT_ID": CONTEXT_ID,
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


def get_existing_options(context_id):
    """Fetches all existing option values in the target context (handles pagination)."""
    existing = set()
    start_at = 0

    while True:
        url = f"{BASE_URL}/rest/api/3/field/customfield_{FIELD_NUMBER}/context/{context_id}/option"
        response = requests.get(
            url, headers=HEADERS, auth=AUTH, params={"startAt": start_at}
        )
        if response.status_code != 200:
            print(
                f"[ERROR] Could not fetch existing options: {response.status_code} - {response.text}"
            )
            return None

        data = response.json()
        for opt in data.get("values", []):
            existing.add(opt.get("value", "").strip().lower())

        if data.get("isLast", True):
            break
        start_at += data.get("maxResults", 100)

    return existing


def add_custom_field_options(context_id, options):
    """Appends new options to the specified context (POST does not overwrite existing options)."""
    url = f"{BASE_URL}/rest/api/3/field/customfield_{FIELD_NUMBER}/context/{context_id}/option"
    payload = {"options": [{"value": opt} for opt in options]}
    return requests.post(url, json=payload, headers=HEADERS, auth=AUTH)


def process_options():
    print("Starting option import...")

    if not os.path.exists(INPUT_FILE_PATH):
        print(f"[ERROR] File not found at: {os.path.abspath(INPUT_FILE_PATH)}")
        return

    existing_options = get_existing_options(CONTEXT_ID)
    if existing_options is None:
        print("[ABORTED] Could not verify existing options.")
        return

    new_options = []
    skipped_count = 0

    with open(INPUT_FILE_PATH, mode="r", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            option_val = row.get("Options", "").strip()
            if not option_val:
                continue

            if option_val.lower() in existing_options:
                skipped_count += 1
            else:
                new_options.append(option_val)
                # Track locally so duplicate rows within the CSV itself are also skipped
                existing_options.add(option_val.lower())

    if skipped_count:
        print(f"Skipped {skipped_count} option(s) that already exist in context '{CONTEXT_ID}'.")

    if not new_options:
        print("[INFO] No new options to add.")
        return

    print(
        f"Adding {len(new_options)} new option(s) to customfield_{FIELD_NUMBER} (Context: {CONTEXT_ID})..."
    )

    response = add_custom_field_options(CONTEXT_ID, new_options)

    if response.status_code in (200, 201):
        print(
            f"[SUCCESS] Successfully added {len(new_options)} new option(s) to context '{CONTEXT_ID}'."
        )
    else:
        print(f"[FAILED] HTTP {response.status_code}: {response.text}")


if __name__ == "__main__":
    process_options()