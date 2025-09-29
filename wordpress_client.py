"""
WordPress Client - WordPress Integration Module
Created: 24 Sept 2025
Author: mstf

Handles WordPress XML-RPC connection and post creation
"""

# Fix for Python 3.9+ collections.Iterable issue
import collections.abc
import collections
collections.Iterable = collections.abc.Iterable

from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods import posts
from wordpress_xmlrpc import WordPressPost
from dotenv import load_dotenv
import os
from typing import Optional

class WordPressClient:
    """WordPress client for publishing blog posts"""

    def __init__(self):
        """Initialize WordPress client"""
        # Load environment variables
        load_dotenv()

        self.wp_url = os.getenv("WORDPRESS_URL")
        self.wp_username = os.getenv("WORDPRESS_USERNAME")
        self.wp_password = os.getenv("WORDPRESS_PASSWORD")

        self.client = None
        self._create_client()

    def _create_client(self):
        """Create WordPress XML-RPC client"""
        try:
            if not all([self.wp_url, self.wp_username, self.wp_password]):
                raise ValueError("Missing WordPress credentials in .env file")

            self.client = Client(self.wp_url, self.wp_username, self.wp_password)

        except Exception as e:
            raise Exception(f"Failed to create WordPress client: {e}")

    def test_connection(self) -> bool:
        """Test WordPress connection"""
        try:
            if not self.client:
                return False

            # Try to get one post to test connection
            test_posts = self.client.call(GetPosts({'number': 1}))
            return True

        except Exception as e:
            print(f"WordPress connection test failed: {e}")
            return False

    def get_posts(self, count: int = 5):
        """Get recent posts from WordPress"""
        try:
            if not self.client:
                return []

            recent_posts = self.client.call(GetPosts({'number': count}))
            return recent_posts

        except Exception as e:
            print(f"Error fetching WordPress posts: {e}")
            return []

    def create_post(self, title: str, content: str, status: str = 'draft', meta_description: str = None) -> Optional[int]:
        """Create a new WordPress post with meta description"""
        try:
            if not self.client:
                raise Exception("WordPress client not initialized")

            post = WordPressPost()
            post.title = title
            post.content = content
            post.post_status = status  # draft, publish, private

            # Set excerpt (meta description)
            if meta_description:
                post.excerpt = meta_description
            else:
                # Fallback to first 200 chars of content
                post.excerpt = content[:200] + "..." if len(content) > 200 else content

            # Add custom fields for SEO (if your theme supports it)
            post.custom_fields = []

            if meta_description:
                # Add meta description as custom field for SEO plugins
                post.custom_fields.append({
                    'key': '_yoast_wpseo_metadesc',  # Yoast SEO
                    'value': meta_description
                })
                post.custom_fields.append({
                    'key': '_aioseop_description',  # All in One SEO
                    'value': meta_description
                })
                post.custom_fields.append({
                    'key': 'meta_description',  # Generic meta description
                    'value': meta_description
                })

            post_id = self.client.call(NewPost(post))
            return post_id

        except Exception as e:
            raise Exception(f"Failed to create WordPress post: {e}")

    def get_connection_info(self) -> dict:
        """Get connection information for debugging"""
        return {
            'url': self.wp_url,
            'username': self.wp_username,
            'password_set': bool(self.wp_password),
            'client_ready': bool(self.client)
        }
