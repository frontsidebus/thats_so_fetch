import requests
import json

# Configuration
GITHUB_TOKEN = "YOUR_GITHUB_PAT"
OUTPUT_FILE = "shai_hulud_affected_packages.json"

def fetch_malware_advisories():
    url = "https://api.github.com/graphql"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    
    # GraphQL query to search security advisories
    # We search for "Shai-Hulud" specifically in the npm ecosystem
    query = """
    query {
      securityAdvisories(first: 100, ecosystem: NPM, query: "Shai-Hulud") {
        nodes {
          summary
          description
          vulnerabilities(first: 10) {
            nodes {
              package {
                name
              }
              vulnerableVersionRange
            }
          }
          references {
            url
          }
        }
      }
    }
    """
    
    response = requests.post(url, json={'query': query}, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed to run by returning code of {response.status_code}. {query}")

def parse_advisories(data):
    affected_packages = {}
    
    advisories = data.get("data", {}).get("securityAdvisories", {}).get("nodes", [])
    
    for advisory in advisories:
        # Double check description for the specific malware family name
        # This handles cases where the search might be too broad
        desc_text = (advisory['summary'] + advisory['description']).lower()
        if "shai-hulud" in desc_text or "shai hulud" in desc_text or "sha1-hulud" in desc_text:
            
            for vul in advisory['vulnerabilities']['nodes']:
                pkg_name = vul['package']['name']
                version_range = vul['vulnerableVersionRange']
                
                if pkg_name not in affected_packages:
                    affected_packages[pkg_name] = []
                
                affected_packages[pkg_name].append(version_range)
    
    return affected_packages

def main():
    print("[-] Querying GitHub Advisory Database for Shai-Hulud signatures...")
    raw_data = fetch_malware_advisories()
    
    print("[-] Parsing results...")
    clean_list = parse_advisories(raw_data)
    
    print(f"[-] Found {len(clean_list)} unique packages affected.")
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(clean_list, f, indent=2)
        
    print(f"[-] Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
