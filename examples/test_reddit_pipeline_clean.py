"""
Real-World Test: Reddit API  Obsidian Notes Pipeline

This pipeline:
1. Fetches trending posts from Reddit
2. Parses the JSON data
3. Validates post structure
4. Formats as Obsidian markdown
5. Saves to vault with tags

Tests:
- Network operations (Reddit API)
- JSON parsing
- Data validation
- Markdown formatting
- File I/O
- Obsidian canvas visualization
- Auto-healing when things break
"""

import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from core import (
    brick, Brick,
    BrickEngine,
    Pipeline,
    BrickTester,
    BrickHealer
)
from core.visualizer import BrickVisualizer, AutoHealer

# Initialize
VAULT_PATH = "C:/Users/MedoRadi/Desktop/Esi world/Esi"
PROJECT_NAME = "BrickLang_Reddit"

engine = BrickEngine(project_dir=f"test_{PROJECT_NAME}")
visualizer = BrickVisualizer(vault_path=VAULT_PATH, project_name=PROJECT_NAME)
healer = AutoHealer(visualizer)

print("Reddit -> Obsidian Pipeline Test")
print("=" * 60)

# ===== BRICK 1: Fetch Reddit Posts =====
@brick("fetch_reddit", description="Fetch trending posts from Reddit API")
def fetch_reddit(subreddit: str, limit: int = 10) -> Dict[str, Any]:
    """
    Fetch trending posts from a subreddit.
    (Mock data for testing - real version would use requests)
    """
    # Mock Reddit API response
    mock_response = {
        "data": {
            "children": [
                {
                    "data": {
                        "title": "Amazing Python Trick",
                        "selftext": "Here's how to speed up your code...",
                        "author": "pythonista",
                        "score": 1234,
                        "created_utc": 1709284800,
                        "subreddit": subreddit,
                        "url": "https://reddit.com/r/python/comments/abc123"
                    }
                },
                {
                    "data": {
                        "title": "TIL about Python decorators",
                        "selftext": "Decorators are amazing for...",
                        "author": "coder42",
                        "score": 856,
                        "created_utc": 1709281200,
                        "subreddit": subreddit,
                        "url": "https://reddit.com/r/python/comments/def456"
                    }
                }
            ]
        },
        "fetched_at": datetime.now().isoformat(),
        "subreddit": subreddit,
        "limit": limit
    }
    
    return mock_response

fetch_reddit.add_test(
    inputs={"subreddit": "python", "limit": 5},
    expected_output={
        "data": lambda x: isinstance(x, dict) and "children" in x,
        "fetched_at": lambda x: isinstance(x, str),
        "subreddit": "python",
        "limit": 5
    },
    label="fetch_basic"
)

# ===== BRICK 2: Parse Posts =====
@brick("parse_reddit_posts", description="Extract post data from Reddit JSON")
def parse_reddit_posts(reddit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse Reddit API response into clean post data.
    """
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

parse_reddit_posts.add_test(
    inputs={
        "reddit_data": {
            "data": {
                "children": [
                    {
                        "data": {
                            "title": "Test Post",
                            "selftext": "Test content",
                            "author": "testuser",
                            "score": 100,
                            "created_utc": 1709284800,
                            "subreddit": "test",
                            "url": "https://reddit.com/test"
                        }
                    }
                ]
            }
        }
    },
    expected_output=[{
        "title": "Test Post",
        "content": "Test content",
        "author": "testuser",
        "score": 100,
        "created": lambda x: isinstance(x, str),
        "subreddit": "test",
        "url": "https://reddit.com/test"
    }],
    label="parse_single"
)

# ===== BRICK 3: Validate Posts =====
@brick("validate_posts", description="Validate post data structure")
def validate_posts(posts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate that all posts have required fields.
    """
    valid = []
    invalid = []
    
    required_fields = ["title", "author", "score", "url"]
    
    for post in posts:
        missing = [f for f in required_fields if not post.get(f)]
        
        if missing:
            invalid.append({
                "post": post.get("title", "unknown"),
                "missing": missing
            })
        else:
            valid.append(post)
    
    return {
        "valid": valid,
        "invalid": invalid,
        "total": len(posts),
        "valid_count": len(valid),
        "invalid_count": len(invalid)
    }

validate_posts.add_test(
    inputs={
        "posts": [
            {"title": "Good Post", "author": "user1", "score": 100, "url": "http://test.com"},
            {"title": "Bad Post", "score": 50}  # Missing author and url
        ]
    },
    expected_output={
        "valid": lambda x: len(x) == 1,
        "invalid": lambda x: len(x) == 1,
        "total": 2,
        "valid_count": 1,
        "invalid_count": 1
    },
    label="validation_mixed"
)

# ===== BRICK 4: Format as Markdown =====
@brick("format_obsidian_note", description="Format post as Obsidian markdown note")
def format_obsidian_note(post: Dict[str, Any]) -> str:
    """
    Format a Reddit post as Obsidian markdown with frontmatter.
    """
    # Create frontmatter
    frontmatter = f'''---
title: "{post['title']}"
author: {post['author']}
score: {post['score']}
subreddit: {post['subreddit']}
created: {post['created']}
source: reddit
tags:
  - reddit
  - {post['subreddit']}
---

'''
    
    # Create content
    content = f'''# {post['title']}

**Author:** u/{post['author']}  
**Score:** {post['score']} upvotes  
**Subreddit:** r/{post['subreddit']}  
**Posted:** {post['created']}  
**Link:** [{post['url']}]({post['url']})

---

{post.get('content', '*No content*')}

---

*Imported from Reddit on {datetime.now().isoformat()}*
'''
    
    return frontmatter + content

format_obsidian_note.add_test(
    inputs={
        "post": {
            "title": "Test Title",
            "author": "testuser",
            "score": 100,
            "subreddit": "test",
            "created": "2026-03-01T12:00:00",
            "url": "https://reddit.com/test",
            "content": "Test content"
        }
    },
    expected_output=lambda x: (
        isinstance(x, str) and
        "---" in x and
        "# Test Title" in x and
        "u/testuser" in x
    ),
    label="format_basic"
)

# ===== BRICK 5: Save to Obsidian =====
@brick("save_to_obsidian", description="Save markdown notes to Obsidian vault")
def save_to_obsidian(
    notes: List[str],
    vault_path: str,
    folder: str = "Reddit_Imports"
) -> Dict[str, Any]:
    """
    Save formatted notes to Obsidian vault.
    """
    from pathlib import Path
    
    vault = Path(vault_path)
    output_dir = vault / folder
    output_dir.mkdir(exist_ok=True)
    
    saved_files = []
    errors = []
    
    for i, note in enumerate(notes):
        try:
            # Extract title from frontmatter
            title = note.split('title: "')[1].split('"')[0] if 'title: "' in note else f"post_{i}"
            
            # Sanitize filename
            filename = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
            filename = filename[:100]  # Limit length
            filepath = output_dir / f"{filename}_{int(time.time())}.md"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(note)
            
            saved_files.append(str(filepath))
        except Exception as e:
            errors.append({
                "note_index": i,
                "error": str(e)
            })
    
    return {
        "saved_count": len(saved_files),
        "error_count": len(errors),
        "files": saved_files,
        "errors": errors,
        "output_dir": str(output_dir)
    }

save_to_obsidian.add_test(
    inputs={
        "notes": ['---\ntitle: "Test"\n---\n# Test'],
        "vault_path": "C:/Users/MedoRadi/Desktop/Esi world/Esi",
        "folder": "Test_Reddit"
    },
    expected_output={
        "saved_count": 1,
        "error_count": 0,
        "files": lambda x: len(x) == 1,
        "errors": [],
        "output_dir": lambda x: "Test_Reddit" in x
    },
    label="save_single"
)

# ===== REGISTER ALL BRICKS =====
print("\n Registering bricks...")
engine.register(fetch_reddit)
engine.register(parse_reddit_posts)
engine.register(validate_posts)
engine.register(format_obsidian_note)
engine.register(save_to_obsidian)

brick_list = []
for brick_id, brick in engine.bricks.items():
    label = brick.label.full if brick.label else "no-label"
    print(f"   {label} -> {brick_id}")
    
    # Create Obsidian note for brick
    import inspect
    source = inspect.getsource(brick.func)
    
    visualizer.create_brick_note(
        brick_id=brick_id,
        name=brick.meta.name,
        label=label,
        description=brick.meta.description or "",
        source_code=source,
        tests=brick.tests,
        status="healthy"
    )
    
    brick_list.append({
        "id": brick_id,
        "name": brick.meta.name,
        "label": label,
        "status": "healthy",
        "error": None
    })

# Map valid posts through formatter (this requires looping)
# For simplicity, we'll create a helper brick BEFORE building pipeline
@brick("format_all_posts", description="Format all posts as markdown")
def format_all_posts(posts: List[Dict[str, Any]]) -> List[str]:
    """Format all posts."""
    notes = []
    for post in posts:
        # Call the actual function, not the Brick wrapper
        frontmatter = f'''---
title: "{post['title']}"
author: {post['author']}
score: {post['score']}
subreddit: {post['subreddit']}
created: {post['created']}
source: reddit
tags:
  - reddit
  - {post['subreddit']}
---

'''
        content = f'''# {post['title']}

**Author:** u/{post['author']}  
**Score:** {post['score']} upvotes  
**Subreddit:** r/{post['subreddit']}  
**Posted:** {post['created']}  
**Link:** [{post['url']}]({post['url']})

---

{post.get('content', '*No content*')}

---

*Imported from Reddit on {datetime.now().isoformat()}*
'''
        notes.append(frontmatter + content)
    return notes

engine.register(format_all_posts)

# ===== BUILD PIPELINE =====
print("\n Building pipeline...")
pipeline = Pipeline("reddit_to_obsidian", engine)

pipeline.add_step(
    "fetch_reddit",
    input_map={"subreddit": "subreddit", "limit": "limit"},
    output_key="reddit_data"
)

pipeline.add_step(
    "parse_reddit_posts",
    input_map={"reddit_data": "reddit_data"},
    output_key="posts"
)

pipeline.add_step(
    "validate_posts",
    input_map={"posts": "posts"},
    output_key="validation"
)

pipeline.add_step(
    "format_all_posts",
    input_map={"posts": "validation.valid"},
    output_key="notes"
)

pipeline.add_step(
    "save_to_obsidian",
    input_map={
        "notes": "notes",
        "vault_path": "vault_path",
        "folder": "folder"
    },
    output_key="save_result"
)

# Create connections for canvas
connections = [
    ("fetch_reddit", "parse_reddit_posts"),
    ("parse_reddit_posts", "validate_posts"),
    ("validate_posts", "format_all_posts"),
    ("format_all_posts", "save_to_obsidian")
]

# ===== TEST ALL BRICKS =====
print("\n Testing all bricks...")
tester = BrickTester(engine)
report = tester.test_all()

print(f"  Results: {report['status']}")
print(f"  Passed: {report['passed']}/{report['total_tests']}")

# Update brick statuses based on test results
for brick_id, result in report["results"].items():
    if result["failed"] > 0:
        brick_status = "broken"
        error_msg = f"{result['failed']} tests failed"
        
        # Find brick in list and update
        for brick_info in brick_list:
            if brick_info["id"] == brick_id:
                brick_info["status"] = brick_status
                brick_info["error"] = error_msg
        
        # Update Obsidian note
        visualizer.update_brick_status(brick_id, brick_status, error_msg)
        print(f"   {brick_id}: {error_msg}")

# ===== CREATE CANVAS =====
print("\n Creating Obsidian canvas...")
canvas_path = visualizer.create_pipeline_canvas(
    "reddit_to_obsidian",
    brick_list,
    connections
)
print(f"  Canvas: {canvas_path}")

# ===== CREATE INDEX =====
index_path = visualizer.create_index_note("reddit_to_obsidian", canvas_path)
print(f"  Index: {index_path}")

# ===== RUN PIPELINE =====
print("\n  Running pipeline...")
try:
    result = pipeline.run({
        "subreddit": "python",
        "limit": 10,
        "vault_path": VAULT_PATH,
        "folder": "Reddit_Imports"
    })
    
    if result["success"]:
        print("   Pipeline completed successfully!")
        save_result = result["data"]["save_result"]
        print(f"  Saved {save_result['saved_count']} notes to:")
        print(f"  {save_result['output_dir']}")
    else:
        print(f"   Pipeline failed at: {result['failed_brick']}")
        print(f"  Error: {result['error']}")
        
        # Update failed brick in canvas
        for brick_info in brick_list:
            if brick_info["id"] == result["failed_brick"]:
                brick_info["status"] = "broken"
                brick_info["error"] = result["error"]
        
        visualizer.update_brick_status(
            result["failed_brick"],
            "broken",
            result["error"]
        )
        
        # Recreate canvas with updated statuses
        visualizer.create_pipeline_canvas(
            "reddit_to_obsidian",
            brick_list,
            connections
        )

except Exception as e:
    print(f"   Exception: {e}")

# ===== FINAL REPORT =====
print("\n" + "=" * 60)
print(" Reddit  Obsidian Pipeline Test Complete")
print("=" * 60)
print(f"Bricks: {len(engine.bricks)}")
print(f"Tests passed: {report['passed']}/{report['total_tests']}")
print(f"Canvas: {canvas_path}")
print(f"Index: {index_path}")
print(f"")
print(" Open in Obsidian:")
print(f"  {VAULT_PATH}/{PROJECT_NAME}/reddit_to_obsidian_index.md")
print("=" * 60)

