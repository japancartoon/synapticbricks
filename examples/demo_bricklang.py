"""
BRICKLANG VERSION

Reddit Data Pipeline - Using BrickLang
Fetch posts, filter, transform, save
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Import all our brick libraries
import core_library_day1
import epic3_phase1
from core import Pipeline

print("=" * 80)
print("BRICKLANG: Reddit Data Pipeline")
print("=" * 80)

start_time = time.perf_counter()

# Combine both engines
core_engine = core_library_day1.engine
epic3_engine = epic3_phase1.engine

# Register Epic 3 bricks into core engine
for brick_id, brick in epic3_engine.bricks.items():
    core_engine.bricks[brick_id] = brick

print(f"\nTotal bricks available: {len(core_engine.bricks)}")

# Build the pipeline
pipeline = Pipeline("reddit_pipeline", core_engine)

# Step 1: Fetch data from Reddit
pipeline.add_step(
    "http_get",
    input_map={
        "url": "url",
        "headers": "headers"
    },
    output_key="response"
)

# Step 2: Parse JSON response
pipeline.add_step(
    "parse_json_response",
    input_map={"response": "response"},
    output_key="parsed"
)

# Step 3: Extract posts from nested structure
from core import brick

@brick("extract_posts", "Extract posts from Reddit response")
def extract_posts(parsed: dict) -> list:
    """Extract post data from Reddit API response."""
    if not parsed.get("success"):
        return []
    data = parsed.get("data", {})
    children = data.get("children", [])
    
    posts = []
    for item in children:
        post = item.get("data", {})
        posts.append({
            "title": post.get("title", ""),
            "score": post.get("score", 0),
            "num_comments": post.get("num_comments", 0),
            "author": post.get("author", ""),
            "subreddit": post.get("subreddit", ""),
            "url": post.get("url", ""),
            "created_utc": post.get("created_utc", 0)
        })
    return posts

core_engine.register(extract_posts)

pipeline.add_step(
    "extract_posts",
    input_map={"parsed": "parsed"},
    output_key="posts"
)

# Step 4: Filter high-quality posts (score > 100)
@brick("filter_high_score", "Filter posts with score > 100")
def filter_high_score(posts: list) -> list:
    """Filter posts with score greater than 100."""
    return [p for p in posts if p.get("score", 0) > 100]

core_engine.register(filter_high_score)

pipeline.add_step(
    "filter_high_score",
    input_map={"posts": "posts"},
    output_key="filtered_posts"
)

# Step 5: Group by subreddit
@brick("group_by_subreddit", "Group posts by subreddit")
def group_by_subreddit(posts: list) -> dict:
    """Group posts by their subreddit field."""
    from collections import defaultdict
    groups = defaultdict(list)
    for post in posts:
        groups[post.get("subreddit")].append(post)
    return dict(groups)

core_engine.register(group_by_subreddit)

pipeline.add_step(
    "group_by_subreddit",
    input_map={"posts": "filtered_posts"},
    output_key="grouped"
)

# Step 6: Build output structure
@brick("build_output", "Build final output structure")
def build_output(posts: list, filtered: list, grouped: dict) -> dict:
    """Build the final output dictionary."""
    return {
        "total_posts": len(posts),
        "filtered_posts": len(filtered),
        "subreddits": len(grouped),
        "data": grouped
    }

core_engine.register(build_output)

pipeline.add_step(
    "build_output",
    input_map={
        "posts": "posts",
        "filtered": "filtered_posts",
        "grouped": "grouped"
    },
    output_key="output"
)

# Step 7: Save to JSON
pipeline.add_step(
    "write_json",
    input_map={
        "filepath": "output_file",
        "data": "output"
    },
    output_key="save_result"
)

# Visualize the pipeline
print("\nPipeline Structure:")
print(pipeline.visualize())

# Run the pipeline!
print("\n" + "=" * 80)
print("Running BrickLang Pipeline...")
print("=" * 80)

result = pipeline.run({
    "url": "https://www.reddit.com/r/python/top.json?limit=50",
    "headers": {"User-Agent": "BrickLang Test 1.0"},
    "output_file": "reddit_synapticbricks.json"
})

total_time = (time.perf_counter() - start_time) * 1000

# Results
if result["success"]:
    print("\n✅ PIPELINE SUCCESS!")
    print(f"\nExecution Time: {result['total_duration_ms']:.2f}ms")
    print(f"Total Time (with setup): {total_time:.2f}ms")
    
    print(f"\nStep Breakdown:")
    for i, step in enumerate(result['execution_log'], 1):
        status = "✅" if step['success'] else "❌"
        print(f"  {status} Step {i}: {step['brick_id']} ({step['duration_ms']:.2f}ms)")
    
    # Show results
    output_data = result['data'].get('output', {})
    print(f"\nResults:")
    print(f"  Total posts: {output_data.get('total_posts', 0)}")
    print(f"  Filtered posts: {output_data.get('filtered_posts', 0)}")
    print(f"  Subreddits: {output_data.get('subreddits', 0)}")
    
else:
    print(f"\n❌ PIPELINE FAILED!")
    print(f"Failed at: {result['failed_brick']}")
    print(f"Error: {result['error']}")

print("\n" + "=" * 80)
print("BRICKLANG - COMPLETE!")
print("=" * 80)
print(f"\nLines of Code: ~25 (excluding brick definitions)")
print(f"Bricks Used: 7")
print(f"Custom Code: 2 small helper bricks")
print("=" * 80)
