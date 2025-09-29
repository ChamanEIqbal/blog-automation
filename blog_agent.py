"""
Blog Writing Agent - Main CLI Interface
Created: 24 Sept 2025
Author: mstf

Epic blog writing agent that reads from Google Sheets, generates
markdown blog posts using AI, AND publishes to WordPress!
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
from blog_engine import BlogEngine
from utils import print_banner, print_success, print_error, print_info

def main():
    """Main CLI interface for the blog writing agent"""

    print_banner()

    parser = argparse.ArgumentParser(
        description="🚀 Epic Blog Writing Agent - Generate awesome blog posts from Google Sheets data!",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python blog_agent.py --list                              # List all available blog topics
  python blog_agent.py --generate 1                        # Generate blog post for row 1 (markdown only)
  python blog_agent.py --generate 1 --to-wordpress         # Generate and publish to WordPress
  python blog_agent.py --generate-all --to-wordpress       # Generate ALL posts and publish (BEAST MODE!)
  python blog_agent.py --custom "AI trends" --to-wordpress # Generate custom post and publish
        """
    )

    parser.add_argument('--list', '-l', action='store_true',
                        help='📋 List all available blog topics from Google Sheets')

    parser.add_argument('--generate', '-g', type=int, metavar='ROW',
                        help='✍️ Generate blog post for specific row number')

    parser.add_argument('--generate-all', '-a', action='store_true',
                        help='🔥 Generate blog posts for ALL topics (BEAST MODE!)')

    parser.add_argument('--custom', '-c', type=str, metavar='TOPIC',
                        help='🎨 Generate custom blog post for any topic')

    parser.add_argument('--to-wordpress', '-w', action='store_true',
                        help='🚀 Publish generated posts to WordPress (instead of just saving as markdown)')

    parser.add_argument('--wp-status', type=str, default='draft',
                        choices=['draft', 'publish', 'private'],
                        help='📝 WordPress post status (default: draft)')

    parser.add_argument('--output-dir', '-o', type=str, default='blog_posts',
                        help='📁 Output directory for markdown files (default: blog_posts)')

    parser.add_argument('--model', '-m', type=str, default='openai/gpt-4o-mini',
                        help='🤖 AI model to use (default: openai/gpt-4o-mini)')

    args = parser.parse_args()

    # Initialize the blog engine
    try:
        print_info("🔧 Initializing Blog Engine...")
        blog_engine = BlogEngine(
            output_dir=args.output_dir,
            ai_model=args.model,
            wordpress_enabled=args.to_wordpress,
            wp_status=args.wp_status
        )
        print_success("✅ Blog Engine initialized successfully!")

    except Exception as e:
        print_error(f"❌ Failed to initialize Blog Engine: {e}")
        sys.exit(1)

    # Handle different commands
    if args.list:
        blog_engine.list_topics()

    elif args.generate is not None:
        blog_engine.generate_blog_post(row_number=args.generate)

    elif args.generate_all:
        blog_engine.generate_all_blog_posts()

    elif args.custom:
        blog_engine.generate_custom_blog_post(topic=args.custom)

    else:
        parser.print_help()
        print_info("\\n💡 Pro tip: Start with --list to see available topics!")
        print_info("💡 Add --to-wordpress to publish directly to WordPress!")

if __name__ == "__main__":
    main()
