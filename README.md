# Bilal Bhai Badmaash Bot

The ultimate blog automation system that combines Google Sheets data, AI content generation, and WordPress publishing!

##  Features

-  **Google Sheets Integration** - Read blog topics from your spreadsheet
-  **AI Content Generation** - Create high-quality blog posts using OpenRouter API
-  **Markdown Export** - Save posts as beautifully formatted markdown files
-  **WordPress Publishing** - Automatically publish to your WordPress site
-  **Batch Processing** - Generate multiple posts in BEAST MODE
-  **Custom Topics** - Generate posts for any topic on demand

##  Setup

1. **Install Dependencies**
   ```bash
   pip install gspread google-auth openai python-wordpress-xmlrpc python-dotenv colorama
   ```

2. **Configure Credentials**
   - Copy your Google Sheets service account JSON file to this directory
   - Update `.env` file with your WordPress credentials:
     ```
     WORDPRESS_URL=https://your-site.com/xmlrpc.php
     WORDPRESS_USERNAME=your_username
     WORDPRESS_PASSWORD=your_password
     API_KEY+yourAPIKEY
     ```

## Usage

### List Available Topics
```bash
python blog_agent.py --list
```

### Generate Markdown Only
```bash
python blog_agent.py --generate 1
python blog_agent.py --custom "AI Trends 2025"
```

### Generate AND Publish to WordPress
```bash
python blog_agent.py --generate 1 --to-wordpress
python blog_agent.py --generate 1 --to-wordpress --wp-status publish
python blog_agent.py --generate-all --to-wordpress
```

### BEAST MODE (Generate All Posts)
```bash
python blog_agent.py --generate-all --to-wordpress
```

## File Structure

```
blog-automation/
├── blog_agent.py          # Main CLI interface
├── blog_engine.py         # Core blog generation logic
├── wordpress_client.py    # WordPress integration
├── utils.py              # Utility functions
├── .env                  # WordPress credentials
├── sheets-api-*.json     # Google Sheets credentials
└── blog_posts/           # Generated markdown files
```

##  Configuration Options

- `--model` - AI model to use (default: openai/gpt-4o-mini)
- `--output-dir` - Directory for markdown files
- `--wp-status` - WordPress post status (draft/publish/private)
- `--to-wordpress` - Enable WordPress publishing

##  Google Sheets Format

Your Google Sheets should have these columns:
- **Column A**: Primary Keywords
- **Column B**: Auxiliary Keywords
- **Column C**: Blog Post Title

##  Examples

```bash
# List all available topics
python blog_agent.py --list

# Generate post for row 1 as draft
python blog_agent.py --generate 1 --to-wordpress

# Generate and publish immediately
python blog_agent.py --generate 1 --to-wordpress --wp-status publish

# Generate custom post about AI
python blog_agent.py --custom "The Future of AI" --to-wordpress

# BILAL BEAST MODE: Generate and publish ALL posts
python blog_agent.py --generate-all --to-wordpress --wp-status publish
```

Created with ❤️ by mstf | September 2025
