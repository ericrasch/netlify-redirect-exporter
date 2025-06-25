# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Python utility that exports WordPress redirect rules from LocalWP installations to Netlify's `_redirects` format. The script connects to a LocalWP MySQL database and extracts redirects from the WordPress Redirection plugin.

## Architecture
The project consists of a single Python script (`extract_netlify_redirects.py`) with these key components:

1. **Auto-setup mechanism** (lines 14-32): Automatically creates a virtual environment and installs dependencies
2. **LocalWP site discovery** (lines 57-96): Scans LocalWP's application support directory to find available WordPress sites
3. **Database connection** (lines 117-124): Connects to MySQL via Unix socket using LocalWP's default credentials
4. **Redirect extraction** (lines 128-133): Queries the `wp_redirection_items` table for enabled redirects
5. **URL normalization** (lines 136-150): Converts relative URLs to absolute ones and ensures proper formatting

## Key Commands

### Running the script
```bash
# Export redirects from a LocalWP site
python3 extract_netlify_redirects.py

# Export with custom site URL
python3 extract_netlify_redirects.py --site-url https://example.com

# Clean up virtual environment
python3 extract_netlify_redirects.py --cleanup
```

## Important Implementation Details

- The script uses hardcoded database credentials that match LocalWP defaults: `DB_USER="root"`, `DB_PASSWORD="root"`, `DB_NAME="local"`
- LocalWP sites are identified by their hash directories in `~/Library/Application Support/Local/run/`
- Site names are resolved from `~/Library/Application Support/Local/sites.json`
- Only active LocalWP sites (with running MySQL) can be accessed
- The script automatically installs `pymysql` in a local virtual environment on first run
- Output is written to `_redirects` file in the current directory

## Development Notes

- This is a standalone script without build, test, or linting infrastructure
- The script is macOS-specific (uses LocalWP's macOS paths)
- Error handling is minimal - the script will exit on database connection failures
- The virtual environment management is built into the script's entry point