"""
Simpler Reddit Pipeline Test - Clean version without encoding issues
"""

import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import brick, BrickEngine, Pipeline, BrickTester
from core.visualizer import BrickVisualizer

# Config
VAULT_PATH = "C:/Users/MedoRadi/Desktop/Esi world/Esi"
PROJECT_NAME = "BrickLang_Reddit"

print("=" * 60)
print("Reddit to Obsidian Pipeline Test")
print("=" * 60)

# Initialize
engine = BrickEngine(project_dir=f"test_{PROJECT_NAME}")
visualizer = BrickVisualizer(vault_path=VAULT_PATH, project_name=PROJECT_NAME)

# ===== ALL BRICKS DEFINED FIRST =====

@brick("fetch_reddit", description="Fetch trending posts from Reddit API")
def fetch_reddit(subreddit: str, limit: int = 10) -> Dict[str, Any]:
    """Fetch trending posts (mock data)"""
    return {
        "data": {
            "children": [
                {"data": {
                    "title": "Amazing Python Trick",
                    "selftext": "Speed up your code...",
                    "author": "pythonista",
                    "score": 1234,
                    "created_utc": 1709284800,
                    "subreddit": subreddit,
                    "url": "https://reddit.com/r/python/1"
                }},
                {"data": {
                    "title": "TIL about decorators",
                    "selftext": "Decorators are amazing...",
                    "author": "coder42",
                    "score": 856,
                    "created_utc": 1709281200,
                    "subreddit": subreddit,
                    "url": "https://reddit.com/r/python/2"
                }}
            ]
        },
        "fetched_at": datetime.now().isoformat(),
        "subreddit": subreddit
    }

@brick("parse_posts", description="Extract post data from Reddit JSON")
def parse_posts(reddit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse Reddit API response"""
    posts = []
    for child in reddit_data["data"]["children"]:
        post_data = child["data"]
        posts.append({
            "title": post_data["title"],
            "content": post_data.get("selftext", ""),
            "author": post_data["author"],
            "score": post_data["score"],
            "created": datetime.fromtimestamp(post_data["created_utc"]).isoformat(),
            "subreddit": post_data["subreddit"],
            "url": post_data["url"]
        })
    return posts

@brick("format_notes", description="Format posts as Obsidian markdown")
def format_notes(posts: List[Dict[str, Any]]) -> List[str]:
    """Format all posts as markdown"""
    notes = []
    for post in posts:
        frontmatter = f'''---
title: "{post['title']}"
author: {post['author']}
score: {post['score']}
subreddit: {post['subreddit']}
source: reddit
---

'''
        content = f'''# {post['title']}

**Author:** u/{post['author']}  
**Score:** {post['score']} upvotes  
**Subreddit:** r/{post['subreddit']}  

{post.get('content', '')}

---
*Imported {datetime.now().isoformat()}*
'''
        notes.append(frontmatter + content)
    return notes

@brick("save_notes", description="Save notes to Obsidian vault")
def save_notes(notes: List[str], vault_path: str, folder: str = "Reddit") -> Dict[str, Any]:
    """Save notes to vault"""
    vault = Path(vault_path)
    output_dir = vault / folder
    output_dir.mkdir(exist_ok=True)
    
    saved = []
    for i, note in enumerate(notes):
        try:
            title = note.split('title: "')[1].split('"')[0] if 'title: "' in note else f"post_{i}"
            filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:100]
            filepath = output_dir / f"{filename}_{int(time.time())}.md"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(note)
            saved.append(str(filepath))
        except Exception as e:
            print(f"  Error saving note {i}: {e}")
    
    return {
        "saved_count": len(saved),
        "files": saved,
        "output_dir": str(output_dir)
    }

# ===== REGISTER =====
print("\nRegistering bricks...")
engine.register(fetch_reddit)
engine.register(parse_posts)
engine.register(format_notes)
engine.register(save_notes)

brick_list = []
for brick_id, b in engine.bricks.items():
    label = b.label.full if b.label else "no-label"
    print(f"  {label} -> {brick_id}")
    
    import inspect
    source = inspect.getsource(b.func)
    
    visualizer.create_brick_note(
        brick_id=brick_id,
        name=b.meta.name,
        label=label,
        description=b.meta.description or "",
        source_code=source,
        tests=b.tests,
        status="healthy"
    )
    
    brick_list.append({
        "id": brick_id,
        "name": b.meta.name,
        "label": label,
        "status": "healthy",
        "error": None
    })

# ===== BUILD PIPELINE =====
print("\nBuilding pipeline...")
pipeline = Pipeline("reddit_to_obsidian", engine)
pipeline.add_step("fetch_reddit", input_map={"subreddit": "subreddit"}, output_key="reddit_data")
pipeline.add_step("parse_posts", input_map={"reddit_data": "reddit_data"}, output_key="posts")
pipeline.add_step("format_notes", input_map={"posts": "posts"}, output_key="notes")
pipeline.add_step("save_notes", input_map={"notes": "notes", "vault_path": "vault_path", "folder": "folder"}, output_key="result")

connections = [
    ("fetch_reddit", "parse_posts"),
    ("parse_posts", "format_notes"),
    ("format_notes", "save_notes")
]

# ===== CREATE CANVAS =====
print("\nCreating Obsidian canvas...")
canvas_path = visualizer.create_pipeline_canvas("reddit_to_obsidian", brick_list, connections)
print(f"  Canvas: {canvas_path}")

index_path = visualizer.create_index_note("reddit_to_obsidian", canvas_path)
print(f"  Index: {index_path}")

# ===== RUN PIPELINE =====
print("\nRunning pipeline...")
result = pipeline.run({
    "subreddit": "python",
    "vault_path": VAULT_PATH,
    "folder": "Reddit_Imports"
})

if result["success"]:
    print("  SUCCESS!")
    save_result = result["data"]["result"]
    print(f"  Saved {save_result['saved_count']} notes")
    print(f"  Location: {save_result['output_dir']}")
else:
    print(f"  FAILED at: {result['failed_brick']}")
    print(f"  Error: {result['error']}")

# ===== FINAL REPORT =====
print("\n" + "=" * 60)
print("COMPLETE")
print("=" * 60)
print(f"Bricks: {len(engine.bricks)}")
print(f"Canvas: {canvas_path}")
print(f"\nOpen in Obsidian:")
print(f"  {VAULT_PATH}/{PROJECT_NAME}/reddit_to_obsidian_index.md")
print("=" * 60)
