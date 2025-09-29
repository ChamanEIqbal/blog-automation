"""
Utilities for Blog Writing Agent
Created: 24 Sept 2025
Author: mstf

Cool terminal output functions with colors and emojis!
"""

import sys
from datetime import datetime
from colorama import init, Fore, Back, Style
import os

# Initialize colorama for Windows
init(autoreset=True)

def print_banner():
    """Print epic ASCII banner"""
    banner = f"""
{Fore.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🚀 EPIC BLOG WRITING AGENT v2.0 🚀                     ║
║                                                              ║
║  📊 Google Sheets + 🤖 AI + 🚀 WordPress = 📝 BEAST MODE   ║
║                                                              ║
║     Created by: mstf | Date: {datetime.now().strftime("%Y-%m-%d")}                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)

def print_success(message: str):
    """Print success message in green"""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message: str):
    """Print error message in red"""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_warning(message: str):
    """Print warning message in yellow"""
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET_ALL}")

def print_info(message: str):
    """Print info message in blue"""
    print(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")

def print_highlight(message: str):
    """Print highlighted message"""
    print(f"{Fore.MAGENTA}🌟 {message}{Style.RESET_ALL}")

def create_progress_bar(current: int, total: int, width: int = 50) -> str:
    """Create a cool progress bar"""
    progress = current / total
    filled = int(width * progress)
    bar = "█" * filled + "░" * (width - filled)
    percentage = int(progress * 100)
    return f"[{bar}] {percentage}% ({current}/{total})"

def safe_filename(text: str, max_length: int = 50) -> str:
    """Convert text to safe filename"""
    import re
    # Remove special characters
    filename = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
    # Replace spaces with hyphens
    filename = re.sub(r'\s+', '-', filename.strip())
    # Convert to lowercase and limit length
    filename = filename.lower()[:max_length]
    return filename.strip('-')

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"
