import requests
import json
import re
import time
import os

# Configuration settings
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "application/json",
}

WILDCARD_REGEX = r"\*\.?([a-zA-Z0-9-]+\.(?:[a-zA-Z0-9-]+\.?){1,})"


def display_logo():
    """Display TROJAN logo ASCII art"""
    red = "\033[91m"
    reset = "\033[0m"

    logo = f"""
{red}
████████╗██████╗░░█████╗░░░░░░██╗░░█████╗░░███╗░░██╗
╚══██╔══╝██╔══██╗██╔══██╗░░░░░██║░██╔══██╗░████╗░██║
░░░██║░░░██████╔╝██║░░██║░░░░░██║░██║░░╚═╝██╔██╗██║
░░░██║░░░██╔══██╗██║░░██║██╗░░██║░██║░░██╗██║╚████║
░░░██║░░░██║░░██║╚█████╔╝╚█████╔╝░╚█████╔╝██║░╚███║
░░░╚═╝░░░╚═╝░░╚═╝░╚════╝░░╚════╝░░░╚════╝░╚═╝░░╚══╝

Trojan Wild it's tool for Hunters to collect live wildcards.
Powerd by @0xTroj3n.
{reset}
    """
    print(logo)
    time.sleep(1)


def fetch_hackerone_data():
    """Fetch data from a trusted external source"""
    try:
        response = requests.get(
            "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/main/data/hackerone_data.json",
            headers=HEADERS,
        )
        response.raise_for_status()  # Check for errors
        return json.loads(response.text)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None


def extract_wildcards(program):
    """Extract wildcards from program data"""
    wildcards = set()

    # First method: search in structured_scopes
    for scope in program.get("structured_scopes", []):
        if scope.get("eligible_for_submission", False):
            identifier = scope.get("identifier", "")
            if "*." in identifier:
                wildcards.add(identifier)

    # Backup method: search via Regex
    if not wildcards:
        program_str = json.dumps(program)
        found = re.findall(WILDCARD_REGEX, program_str)
        wildcards.update([f"*.{match}" for match in found if match.count(".") >= 1])

    return wildcards


def main():
    display_logo()

    # Fetch the data
    data = fetch_hackerone_data()
    if not data:
        return

    print(f"Loaded {len(data)} programs")

    results = set()

    # Process the first 20 programs for testing
    for idx, program in enumerate(data[:20], 1):
        try:
            print(f"Processing program {idx}: {program.get('name')}")
            wildcards = extract_wildcards(program)
            if wildcards:
                results.update(wildcards)
                print(f"Found {len(wildcards)} wildcards")
            time.sleep(1)
        except Exception as e:
            print(f"Error: {str(e)[:50]}")

    # Save the results in script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_name = "trojan-wilds.txt"
    file_path = os.path.join(script_dir, file_name)

    with open(file_path, "w") as f:
        for item in sorted(results):
            f.write(f"{item}\n")

    print(f"\nSuccessfully collected {len(results)} wildcards")
    print(f"Results saved to: {file_path}")


if __name__ == "__main__":
    main()
