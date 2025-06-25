# Netlify Redirect Exporter

A Python utility that exports WordPress redirect rules from LocalWP installations to Netlify's `_redirects` format.

## Overview

This tool connects to a LocalWP (Local by Flywheel) WordPress installation and extracts redirect rules managed by the WordPress Redirection plugin, converting them into Netlify's redirect format. This is particularly useful when migrating WordPress sites to static hosting on Netlify.

## Features

- 🔍 **Auto-discovery** of LocalWP sites on your system
- 🚀 **Zero configuration** - automatically sets up virtual environment and dependencies
- 🔗 **Smart URL handling** - converts relative URLs to absolute ones
- 🧹 **Clean up option** - removes virtual environment when done
- 📄 **Direct export** to Netlify `_redirects` format

## Requirements

- Python 3
- LocalWP (Local by Flywheel) installed with at least one WordPress site
- macOS (currently only supports macOS paths for LocalWP)
- WordPress site must have the Redirection plugin with configured redirects

## Installation

Clone this repository:

```bash
git clone https://github.com/yourusername/netlify-redirect-exporter.git
cd netlify-redirect-exporter
```

## Usage

### Basic Usage

Simply run the script and select your LocalWP site:

```bash
python3 extract_netlify_redirects.py
```

The script will:
1. Scan for available LocalWP sites
2. Show you a list of sites (🟢 = active, ⚪️ = inactive)
3. Let you select which site to export from
4. Export redirects to a `_redirects` file in the current directory

### Advanced Usage

Specify a custom site URL:

```bash
python3 extract_netlify_redirects.py --site-url https://example.com
```

### Cleanup

Remove the virtual environment after use:

```bash
python3 extract_netlify_redirects.py --cleanup
```

## How It Works

1. **Site Discovery**: Scans `~/Library/Application Support/Local/run/` for LocalWP site instances
2. **Database Connection**: Connects to the selected site's MySQL database via Unix socket
3. **Redirect Extraction**: Queries the `wp_redirection_items` table for enabled redirects
4. **Format Conversion**: Converts WordPress redirect format to Netlify format
5. **File Generation**: Creates a `_redirects` file with properly formatted rules

## Output Format

The tool generates a `_redirects` file with entries in Netlify's format:

```
/old-path    https://example.com/new-path    301
/another-old-path    /relative-new-path    302
```

## Limitations

- Currently only supports macOS (LocalWP paths are macOS-specific)
- Requires LocalWP site to be running (MySQL must be active)
- Only exports redirects managed by the WordPress Redirection plugin
- Uses LocalWP's default database credentials (root/root)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created by ChatGPT + Eric Rasch