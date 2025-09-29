"""
Blog Engine - Core logic for generating blog posts
Created: 24 Sept 2025
Author: mstf

Handles Google Sheets integration, AI generation, file output, AND WordPress publishing!
"""

import gspread
from google.oauth2.service_account import Credentials
from openai import OpenAI
import os
import re
import markdown
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from utils import print_success, print_error, print_info, print_warning
from wordpress_client import WordPressClient

class BlogEngine:
    """Core blog writing engine that combines Google Sheets + AI + WordPress"""

    def __init__(self, output_dir: str = "blog_posts", ai_model: str = "openai/gpt-4o-mini",
                 wordpress_enabled: bool = False, wp_status: str = "draft"):
        """Initialize the blog engine"""
        self.output_dir = Path(output_dir)
        self.ai_model = ai_model
        self.wordpress_enabled = wordpress_enabled
        self.wp_status = wp_status
        self.sheet_data = []

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Initialize Google Sheets client
        self._init_sheets_client()

        # Initialize OpenAI client
        self._init_ai_client()

        # Initialize WordPress client if needed
        if self.wordpress_enabled:
            self._init_wordpress_client()

        # Load data from Google Sheets
        self._load_sheet_data()

    def _init_sheets_client(self):
        """Initialize Google Sheets client"""
        try:
            SCOPES = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]

            credentials = Credentials.from_service_account_file(
                'sheets-api-cloud-66011387df21.json',
                scopes=SCOPES
            )

            self.gc = gspread.authorize(credentials)
            print_info("📊 Google Sheets client initialized")

        except Exception as e:
            raise Exception(f"Failed to initialize Google Sheets: {e}")

    def _init_ai_client(self):
        """Initialize OpenAI client"""
        try:
            # Load API key from environment variable
            api_key = os.environ.get("OPENROUTER_API_KEY")
            if not api_key:
                raise Exception("OPENROUTER_API_KEY not found in environment. Please set it in your .env file.")
            self.ai_client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )
            print_info("🤖 AI client initialized")

        except Exception as e:
            raise Exception(f"Failed to initialize AI client: {e}")

    def _init_wordpress_client(self):
        """Initialize WordPress client"""
        try:
            self.wp_client = WordPressClient()
            if self.wp_client.test_connection():
                print_info("🚀 WordPress client initialized and connected!")
            else:
                print_warning("⚠️ WordPress client initialized but connection failed")
                print_info("📝 Posts will be saved as markdown only")
                self.wordpress_enabled = False

        except Exception as e:
            print_error(f"❌ WordPress initialization failed: {e}")
            print_info("📝 Falling back to markdown-only mode")
            self.wordpress_enabled = False

    def _load_sheet_data(self):
        """Load data from Google Sheets"""
        try:
            SPREADSHEET_ID = "1Ek6eNBGc2X0RIynWh-_MgfHDAeX-9Xyoa7VL43LaoZI"

            # Open the spreadsheet
            sheet = self.gc.open_by_key(SPREADSHEET_ID)
            worksheet = sheet.worksheets()[0]  # First worksheet

            # Get headers
            headers = worksheet.get("A1:C1")[0]

            # Get all data
            all_data = worksheet.get("A2:C")

            # Format data as list of dictionaries
            self.sheet_data = []
            for i, row in enumerate(all_data, 1):
                if len(row) >= 3:
                    self.sheet_data.append({
                        'row_number': i,
                        'primary_keywords': row[0],
                        'auxiliary_keywords': row[1],
                        'title': row[2]
                    })

            print_info(f"📋 Loaded {len(self.sheet_data)} blog topics from Google Sheets")

        except Exception as e:
            raise Exception(f"Failed to load sheet data: {e}")

    def list_topics(self):
        """List all available blog topics"""
        print_info("\\n📋 Available Blog Topics:")
        print("=" * 80)

        if not self.sheet_data:
            print_warning("No topics found in Google Sheets!")
            return

        for item in self.sheet_data:
            print(f"Row {item['row_number']}: {item['title']}")
            print(f"   🎯 Primary: {item['primary_keywords']}")
            print(f"   🔗 Auxiliary: {item['auxiliary_keywords']}")
            print("-" * 60)

        print(f"\\n💡 Total: {len(self.sheet_data)} blog topics available")

        if self.wordpress_enabled:
            print_info("🚀 WordPress publishing is ENABLED")
        else:
            print_info("📝 Markdown-only mode (add --to-wordpress to publish)")

    def generate_blog_post(self, row_number: int):
        """Generate a blog post for a specific row"""
        # Find the topic
        topic_data = None
        for item in self.sheet_data:
            if item['row_number'] == row_number:
                topic_data = item
                break

        if not topic_data:
            print_error(f"❌ Row {row_number} not found!")
            return

        print_info(f"✍️ Generating blog post for: {topic_data['title']}")

        # Generate the blog content
        ai_content = self._generate_ai_content(topic_data)

        # Extract meta description and clean content
        meta_description, blog_content = self._extract_meta_description(ai_content)
        print_info(f"📋 Meta description: {meta_description}")

        # Save to markdown file
        filename = self._save_blog_post(topic_data, blog_content, meta_description)
        print_success(f"📝 Markdown saved: {filename}")

        # Publish to WordPress if enabled
        if self.wordpress_enabled:
            wp_post_id = self._publish_to_wordpress(topic_data, blog_content, meta_description)
            if wp_post_id:
                print_success(f"🚀 Published to WordPress! Post ID: {wp_post_id}")
            else:
                print_error("❌ WordPress publishing failed")

    def generate_all_blog_posts(self):
        """Generate blog posts for ALL topics (BEAST MODE!)"""
        print_info(f"🔥 BEAST MODE ACTIVATED! Generating {len(self.sheet_data)} blog posts...")

        if self.wordpress_enabled:
            print_info("🚀 WordPress publishing is ENABLED for all posts!")

        generated_count = 0
        published_count = 0

        for topic_data in self.sheet_data:
            try:
                print_info(f"✍️ Generating: {topic_data['title']}")

                # Generate content
                ai_content = self._generate_ai_content(topic_data)

                # Extract meta description and clean content
                meta_description, blog_content = self._extract_meta_description(ai_content)

                # Save markdown
                filename = self._save_blog_post(topic_data, blog_content, meta_description)
                generated_count += 1
                print_success(f"📝 Markdown: {filename}")

                # Publish to WordPress if enabled
                if self.wordpress_enabled:
                    wp_post_id = self._publish_to_wordpress(topic_data, blog_content, meta_description)
                    if wp_post_id:
                        published_count += 1
                        print_success(f"🚀 WordPress ID: {wp_post_id}")
                    else:
                        print_error("❌ WordPress publishing failed")

                print("-" * 50)

            except Exception as e:
                print_error(f"❌ Failed to generate {topic_data['title']}: {e}")

        print_success(f"🎉 BEAST MODE COMPLETE!")
        print_success(f"📝 Generated: {generated_count}/{len(self.sheet_data)} markdown files")
        if self.wordpress_enabled:
            print_success(f"🚀 Published: {published_count}/{len(self.sheet_data)} WordPress posts")

    def generate_custom_blog_post(self, topic: str):
        """Generate a custom blog post for any topic"""
        print_info(f"🎨 Generating custom blog post for: {topic}")

        # Create custom topic data
        custom_data = {
            'row_number': 'custom',
            'primary_keywords': topic,
            'auxiliary_keywords': '',
            'title': topic
        }

        # Generate the blog content
        ai_content = self._generate_ai_content(custom_data)

        # Extract meta description and clean content
        meta_description, blog_content = self._extract_meta_description(ai_content)

        # Save to markdown file
        filename = self._save_blog_post(custom_data, blog_content, meta_description)
        print_success(f"📝 Custom markdown saved: {filename}")

        # Publish to WordPress if enabled
        if self.wordpress_enabled:
            wp_post_id = self._publish_to_wordpress(custom_data, blog_content, meta_description)
            if wp_post_id:
                print_success(f"🚀 Published to WordPress! Post ID: {wp_post_id}")
            else:
                print_error("❌ WordPress publishing failed")

    def _generate_ai_content(self, topic_data: Dict) -> str:
        """Generate blog content using AI"""

        # Create the prompt
        prompt = f"""
Write an engaging, comprehensive blog post about "{topic_data['title']}".

Primary keywords to focus on: {topic_data['primary_keywords']}
Auxiliary keywords to include: {topic_data['auxiliary_keywords']}

Requirements:
- FIRST: Write a compelling meta description (150-160 characters) that includes primary keywords
- Format the meta description as: META_DESCRIPTION: [your description here]
- Then write the blog post in markdown format
- Include a compelling title with # header
- Add an engaging introduction
- Create 3-5 main sections with ## headers
- Include practical tips, examples, or insights
- Add a strong conclusion
- Use bullet points and numbered lists where appropriate
- Make it SEO-friendly but natural and engaging
- Aim for 800-1200 words
- Include relevant emojis to make it more engaging

IMPORTANT: Start your response with the meta description line, then add a blank line, then write the blog post.

Example format:
META_DESCRIPTION: Learn how digital marketing transforms businesses with proven strategies that boost sales, increase brand awareness, and drive customer engagement in 2025.

# Your Blog Post Title Here
...rest of the blog content...

Write a high-quality blog post that would rank well and provide real value to readers.
"""

        try:
            completion = self.ai_client.chat.completions.create(
                model=self.ai_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"AI generation failed: {e}")

    def _extract_meta_description(self, content: str) -> tuple[str, str]:
        """Extract meta description from AI content and return (meta_description, clean_content)"""
        if content.startswith('META_DESCRIPTION:'):
            lines = content.split('\n', 2)
            if len(lines) >= 2:
                meta_description = lines[0].replace('META_DESCRIPTION:', '').strip()
                # Remove the meta description line and any following empty lines
                clean_content = '\n'.join(lines[1:]).strip()
                return meta_description, clean_content

        # Fallback: generate a basic meta description from the first paragraph
        lines = content.split('\n')
        first_paragraph = ""
        for line in lines:
            if line.strip() and not line.startswith('#'):
                first_paragraph = line.strip()
                break

        # Create a meta description from first paragraph (limit to 160 chars)
        meta_description = first_paragraph[:157] + "..." if len(first_paragraph) > 157 else first_paragraph

        return meta_description, content

    def _save_blog_post(self, topic_data: Dict, content: str, meta_description: str) -> str:
        """Save blog post to markdown file"""

        # Create filename from title
        title = topic_data['title']
        filename = re.sub(r'[^a-zA-Z0-9\\s-]', '', title)  # Remove special chars
        filename = re.sub(r'\\s+', '-', filename.strip())   # Replace spaces with hyphens
        filename = filename.lower()[:50]                    # Lowercase and limit length

        # Add timestamp for uniqueness
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}.md"

        # Full file path
        filepath = self.output_dir / filename

        # Add metadata to the content
        metadata = f"""---
title: "{topic_data['title']}"
meta_description: "{meta_description}"
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
primary_keywords: "{topic_data['primary_keywords']}"
auxiliary_keywords: "{topic_data['auxiliary_keywords']}"
row_number: {topic_data['row_number']}
generated_by: "Blog Writing Agent v2.0"
wordpress_enabled: {self.wordpress_enabled}
---

"""

        full_content = metadata + content

        # Write to file
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            return str(filepath)

        except Exception as e:
            raise Exception(f"Failed to save markdown file: {e}")

    def _publish_to_wordpress(self, topic_data: Dict, content: str, meta_description: str) -> Optional[int]:
        """Publish blog post to WordPress"""
        if not self.wordpress_enabled or not hasattr(self, 'wp_client'):
            return None

        try:
            # Convert markdown to HTML (simple conversion)
            html_content = self._markdown_to_html(content)

            # Create the post
            post_id = self.wp_client.create_post(
                title=topic_data['title'],
                content=html_content,
                meta_description=meta_description,
                status=self.wp_status
            )

            return post_id

        except Exception as e:
            print_error(f"WordPress publishing error: {e}")
            return None

    def _markdown_to_html(self, markdown_content: str) -> str:
        """Convert markdown to HTML using proper markdown library"""
        try:
            # Remove YAML frontmatter if present
            if markdown_content.startswith('---'):
                parts = markdown_content.split('---', 2)
                if len(parts) >= 3:
                    markdown_content = parts[2].strip()

            # Convert markdown to HTML using the markdown library
            html_content = markdown.markdown(
                markdown_content,
                extensions=['extra', 'codehilite']
            )

            # Clean up any remaining issues
            html_content = html_content.strip()

            print_info(f"🔄 Converted {len(markdown_content)} chars of markdown to {len(html_content)} chars of HTML")

            return html_content

        except Exception as e:
            print_error(f"Markdown conversion failed: {e}")
            # Fallback to simple conversion
            return self._simple_markdown_to_html(markdown_content)

    def _simple_markdown_to_html(self, markdown_content: str) -> str:
        """Simple fallback markdown to HTML conversion"""
        # Remove YAML frontmatter if present
        if markdown_content.startswith('---'):
            parts = markdown_content.split('---', 2)
            if len(parts) >= 3:
                markdown_content = parts[2].strip()

        html_content = markdown_content

        # Convert headers
        html_content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)

        # Convert bold and italic
        html_content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html_content)
        html_content = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html_content)

        # Convert to paragraphs
        paragraphs = html_content.split('\n\n')
        html_paragraphs = []

        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('<'):
                para = f'<p>{para}</p>'
            elif para:
                html_paragraphs.append(para)

        return '\n'.join(html_paragraphs)
