import csv
import os
import requests
from requests.auth import HTTPBasicAuth

# Configuration
api_token = "abc"
email = "abc@example.com"
base_url = "https://instancename.atlassian.net/"
field_number = 12345
input_file_path = "OptionsList.csv"

auth = HTTPBasicAuth(email, api_token)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
}


def get_field_context_id(field_num):
    """Retrieves the primary context ID for the custom field."""
    url = f"{base_url}/rest/api/3/field/customfield_{field_num}/context"
    response = requests.get(url, headers=headers, auth=auth)

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
    # Updated path: /field/customfield_{id}/context/{contextId}/option
    url = f"{base_url}/rest/api/3/field/customfield_{field_number}/context/{context_id}/option"

    payload = {"options": [{"value": opt} for opt in options]}

    response = requests.post(url, json=payload, headers=headers, auth=auth)
    return response


def process_options():
    print("Starting option import...")

    if not os.path.exists(input_file_path):
        print(f"[ERROR] File not found at: {os.path.abspath(input_file_path)}")
        return

    context_id = get_field_context_id(field_number)
    if not context_id:
        print("[ABORTED] Missing Context ID.")
        return

    options_to_add = []
    with open(input_file_path, mode="r", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        for row in reader:
            option_val = row.get("Options", "").strip()
            if option_val:
                options_to_add.append(option_val)

    if not options_to_add:
        print("[WARNING] No options found in CSV.")
        return

    print(
        f"Found {len(options_to_add)} options. Adding to field customfield_{field_number} (Context: {context_id})..."
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
