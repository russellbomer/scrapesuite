"""Main entry point for running scrapesuite as a module."""

import sys

from scrapesuite.wizard import run_wizard

if __name__ == "__main__":
    # If called with 'python -m scrapesuite' or 'python -m scrapesuite.wizard'
    run_wizard()
