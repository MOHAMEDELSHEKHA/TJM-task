import requests
import json
import os

POSTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "posts.json")


def fetch_posts(limit=10):

    try:
        url = "https://jsonplaceholder.typicode.com/posts"
        response = requests.get(url, verify=False, timeout=10)
        response.raise_for_status()
        posts = response.json()
        print(f"✓ Fetched {len(posts)} posts from API")
        return posts[:limit]
    except Exception as e:
        print(f"API unavailable: {e}")

    try:
        with open(POSTS_FILE, "r", encoding="utf-8") as f:
            posts = json.load(f)
        print(f"✓ Loaded {len(posts)} posts from local file")
        return posts[:limit]
    except Exception as e:
        raise RuntimeError(f"Could not fetch posts from API or local file: {e}")


def format_post(post):
    return f"Title: {post['title']}\n\n{post['body']}"


def get_filename(post):
    return f"post_{post['id']}.txt"