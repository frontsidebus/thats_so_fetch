# **Shai-Hulud Threat Intel Fetcher**

## **Overview**

This tool automates the retrieval of npm packages compromised by the **Shai-Hulud** (and **Sha1-Hulud**) supply chain attack. It queries the [GitHub Advisory Database](https://github.com/advisories) via GraphQL to fetch the latest confirmed compromised packages and versions.  
The output is a JSON file structured for ingestion by detection engineering pipelines (e.g., Wiz, Sentinel, or custom CI/CD blockers).

## **Prerequisites**

* Python 3.8+  
* A GitHub Personal Access Token (PAT) with public\_repo or read:packages scope.

## **Installation**

1. **Clone this repository:**  
   Bash  
   git clone https://github.com/your-org/shai-hulud-fetcher.git  
   cd shai-hulud-fetcher

2. **Install dependencies:**  
   Bash  
   pip install requests

3. Configure Environment:  
   Export your GitHub Token as an environment variable to avoid hardcoding credentials.  
   Bash  
   export GITHUB\_TOKEN="your\_pat\_here"

   *(Note: Ensure the Python script is updated to read this from os.environ)*

## **Usage**

Run the script to generate the latest threat list:

Bash

python3 fetch\_threats.py

### **Output Format**

The script generates a file named shai\_hulud\_affected\_packages.json.  
**Example Output:**

JSON

{  
  "eslint-config-standard-extended": \[  
    "\>= 14.0.0 \< 15.0.0"  
  \],  
  "faker-colors": \[  
    "= 1.0.9"  
  \]  
}

## **Automation (GitHub Actions)**

To ensure the list is always up to date without manual intervention, use the following GitHub Action workflow. This will run the scanner every 6 hours and commit the updated JSON list back to the repository.  
Create .github/workflows/update-threat-intel.yml:

YAML

name: Update Shai-Hulud Threat List

on:  
  schedule:  
    \- cron: '0 \*/6 \* \* \*' \# Runs every 6 hours  
  workflow\_dispatch:      \# Allows manual trigger

jobs:  
  update-list:  
    runs-on: ubuntu-latest  
    steps:  
      \- uses: actions/checkout@v3

      \- name: Set up Python  
        uses: actions/setup-python@v4  
        with:  
          python-version: '3.9'

      \- name: Install Dependencies  
        run: pip install requests

      \- name: Fetch Latest Intelligence  
        env:  
          GITHUB\_TOKEN: ${{ secrets.GH\_PAT }} \# Add this to Repo Secrets  
        run: python fetch\_threats.py

      \- name: Commit and Push Changes  
        run: |  
          git config \--global user.name 'ThreatBot'  
          git config \--global user.email 'secops@yourcompany.com'  
          git add shai\_hulud\_affected\_packages.json  
          git commit \-m "Update threat intel list \[skip ci\]" || exit 0  
          git push

## **Integration with Wiz**

To use this data in Wiz:

1. **Ingest:** Point your Wiz automation to the raw URL of the generated JSON file in this repo.  
2. **Query:** Use the JSON keys (package names) to update a "Malicious Package List" in your Wiz runtime policies.  
3. **Detect:** Wiz will now flag any container or repo containing packages matching the names in shai\_hulud\_affected\_packages.json.

---

**Would you like me to write a quick Python snippet that reads this JSON output and converts it into a specific Wiz CLI query format?**
