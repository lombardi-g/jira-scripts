# ⚡ Jira Cloud Admin Automations

[![Jira](https://img.shields.io/badge/Jira-0052CC?logo=jira&logoColor=fff)](#)
[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Jira REST API](https://img.shields.io/badge/Jira%20REST%20API-v3-0052CC?logo=atlassian&logoColor=white)](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)

A personal collection of Python automation scripts designed to eliminate repetitive clicking in the Jira Cloud Admin UI. The scripts leverage the **Jira Cloud REST API v3** to handle bulk updates in seconds via CSV files.

---

## 🛠️ Included Automations

### 1. Bulk Custom Field Option Importer
Automates adding new selectable options to an existing Jira custom field (such as single-select or multi-select dropdowns).
* **How it works:** Automatically fetches the primary context ID for your target `customfield_<ID>`, reads a list of values from a CSV file, and pushes them in a single bulk API request.
* **Best for:** Populating massive lists (e.g., countries, departments, product catalogs) without manually typing each option in Jira.

### 2. Bulk Screen Field Assigner
Automates attaching multiple existing custom fields to a specific Jira Screen.
* **How it works:** Targets a specific `SCREEN_ID`, automatically resolves its default/first tab ID (usually `Field Tab`), reads a list of custom field IDs from a CSV, and adds them to the screen.
* **Smart Formatting & Handling:** Automatically formats raw numeric IDs (e.g., `10010` $\rightarrow$ `customfield_10010`) and gracefully skips fields that are already present on the screen.

---

## 📄 CSV Formatting & Usage

### Running Script 1: Bulk Custom Field Option Importer

1. Prepare your CSV file (e.g., `OptionsList.csv`) with a column header named **`Options`**:
   ```csv
   Options
   Option Alpha
   Option Beta
   Option Gamma
   ```
2. Ensure `JIRA_FIELD_NUMBER` is set in your `.env` file (just the numbers, e.g., `10045`).
3. Run the script:
   ```bash
   python import_options.py
   ```

### Running Script 2: Bulk Screen Field Assigner

1. Prepare your CSV file with a header row (skipped automatically) and list your custom field IDs in the first column. You can provide either the full ID or just the numeric part:
   ```csv
   Field_IDs
   10010
   customfield_10011
   10012
   ```
2. Update the `SCREEN_ID` variable directly inside the script to match your target Jira Screen ID (found in the URL when editing a screen in Jira Admin).
3. Run the script:
   ```bash
   python add_fields_to_screen.py
   ```
