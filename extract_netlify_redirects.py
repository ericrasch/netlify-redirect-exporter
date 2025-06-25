#!/usr/bin/env python3
"""
Netlify Redirect Exporter

This script connects to a LocalWP (Local by Flywheel) WordPress installation and exports 
redirect rules from the WordPress Redirection plugin to Netlify's _redirects format.

The script performs the following operations:
1. Auto-discovers LocalWP sites on the system
2. Allows user to select a specific site
3. Connects to the site's MySQL database via Unix socket
4. Extracts redirect rules from wp_redirection_items table
5. Converts WordPress redirects to Netlify format
6. Outputs to a _redirects file

Usage:
    python3 extract_netlify_redirects.py [--site-url SITE_URL]
    python3 extract_netlify_redirects.py --cleanup

Arguments:
    --site-url: Base URL to prepend to relative redirect targets (default: auto-detected)
    --cleanup: Remove the virtual environment and cache files

Requirements:
    - Python 3
    - LocalWP installed with at least one WordPress site
    - WordPress site must have Redirection plugin with configured redirects
    - macOS (uses macOS-specific LocalWP paths)

Example:
    # Basic usage - auto-detect site URL
    $ python3 extract_netlify_redirects.py
    
    # Specify custom site URL
    $ python3 extract_netlify_redirects.py --site-url https://example.com
    
    # Clean up after use
    $ python3 extract_netlify_redirects.py --cleanup

Output:
    Creates a _redirects file in the current directory with Netlify-formatted redirect rules

Author: ChatGPT + Eric Rasch
License: MIT
"""

# === CONFIG ===
DB_NAME = "local"
DB_USER = "root"
DB_PASSWORD = "root"
OUTPUT_FILE = "_redirects"

if __name__ == "__main__":
    import subprocess
    import sys
    import shutil
    import os

    if not sys.executable.startswith(os.path.join(os.getcwd(), "venv")):
        venv_path = os.path.join(os.getcwd(), "venv")
        python_bin = os.path.join(venv_path, "bin", "python")

        if not os.path.exists(python_bin):
            print("🔧 Creating virtual environment...")
            subprocess.run(["python3", "-m", "venv", "venv"], check=True)
            print("📦 Installing dependencies...")
            subprocess.run([python_bin, "-m", "pip", "install", "--quiet", "pymysql"], check=True)

        print("🚀 Re-running script inside virtual environment...")
        subprocess.run([python_bin, __file__] + sys.argv[1:])
        sys.exit(0)

    import pymysql
    if "--cleanup" in sys.argv:
        import os
        import shutil
        try:
            shutil.rmtree("venv")
            print("🧹 Virtual environment removed (venv/).")

            print("🧼 Removing all __pycache__ directories...")
            for root, dirs, files in os.walk("."):
                for d in dirs:
                    if d == "__pycache__":
                        pycache_path = os.path.join(root, d)
                        shutil.rmtree(pycache_path, ignore_errors=True)
                        print(f"   Removed {pycache_path}")
        except Exception as e:
            print(f"⚠️ Failed to remove venv: {e}")
        sys.exit(0)

import argparse
import os

# --- LocalWP hash selection ---
localwp_run_path = os.path.expanduser("~/Library/Application Support/Local/run")
hashes = [d for d in os.listdir(localwp_run_path)
          if os.path.isdir(os.path.join(localwp_run_path, d)) and d != "router"]
if not hashes:
    print("❌ No LocalWP socket directories found.")
    sys.exit(1)


import json
site_map = {}

# Build a hash → site name mapping from Local's sites.json
local_sites_json = os.path.expanduser("~/Library/Application Support/Local/sites.json")
if os.path.exists(local_sites_json):
    try:
        with open(local_sites_json, "r") as f:
            data = json.load(f)
            for hash_val, site_data in data.items():
                site_name = site_data.get("name", "(unnamed)")
                site_map[hash_val] = site_name
    except Exception as e:
        print(f"⚠️ Failed to read sites.json: {e}")

print("🔍 Found LocalWP environments:")
sorted_hashes = sorted(hashes, key=lambda h: site_map.get(h, "(unknown)").lower())
for i, h in enumerate(sorted_hashes):
    site_name = site_map.get(h, "(unknown)")
    socket_path = os.path.join(localwp_run_path, h, "mysql", "mysqld.sock")
    is_active = os.path.exists(socket_path)
    status = "🟢" if is_active else "⚪️"
    print(f"  [{i + 1}] {h} → {site_name} {status}")

print("\nℹ️ Only active 🟢 sites will work. Start the site in LocalWP before selecting it.\n")

choice = input("Select a site by number: ")
try:
    selected_hash = sorted_hashes[int(choice) - 1]
except (IndexError, ValueError):
    print("❌ Invalid selection.")
    sys.exit(1)

# Set default_site_url based on the selected site name
selected_site_name = site_map.get(selected_hash, "mysite.com")
import re
domain_parts = re.split(r"[^\w]+", selected_site_name.lower())
if len(domain_parts) >= 2:
    default_site_url = f"https://{domain_parts[0]}.{domain_parts[-1]}"
else:
    default_site_url = f"https://{''.join(domain_parts)}.com"

# Now parse arguments, using the selected site name for default
parser = argparse.ArgumentParser()
parser.add_argument("--site-url", default=default_site_url, help="Base site URL to prepend to relative targets")
args = parser.parse_args()

SITE_URL = args.site_url.rstrip('/')

DB_SOCKET = os.path.join(localwp_run_path, selected_hash, "mysql", "mysqld.sock")

# === CONNECT & QUERY ===
connection = pymysql.connect(
    unix_socket=DB_SOCKET,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

with connection:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT url, action_data, action_code
            FROM wp_redirection_items
            WHERE status = 'enabled' AND action_type = 'url' AND action_data IS NOT NULL
        """)
        redirects = cursor.fetchall()

# === FORMAT OUTPUT ===
def normalize_url(path):
    if not path.startswith('/'):
        return '/' + path
    return path

lines = []
for row in redirects:
    source = normalize_url(row['url'].strip())
    target = row['action_data'].strip()
    code = str(row['action_code']).strip() or '301'

    if not target.startswith('http'):
        target = SITE_URL + normalize_url(target)

    lines.append(f"{source}    {target}    {code}")

# === WRITE TO FILE ===
with open(OUTPUT_FILE, 'w') as f:
    f.write("\n".join(lines))

import os
output_path = os.path.abspath(OUTPUT_FILE)
print(f"✅ Export complete. {len(lines)} redirects written to:\n{output_path}")

print("\nℹ️  To clean up the virtual environment, run:\n   python3 extract_netlify_redirects.py --cleanup")