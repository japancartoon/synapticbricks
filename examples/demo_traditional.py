"""
TRADITIONAL PYTHON VERSION

Reddit Data Pipeline - Pure Python
Fetch posts, filter, transform, save
"""

import requests
import json
import time
from typing import List, Dict
from collections import defaultdict

print("=" * 80)
print("TRADITIONAL PYTHON: Reddit Data Pipeline")
print("=" * 80)

start_time = time.perf_counter()

# Step 1: Fetch data from Reddit
print("\n[1/5] Fetching data from Reddit API...")
step1_start = time.perf_counter()

url = "https://www.reddit.com/r/python/top.json?limit=50"
headers = {"User-Agent": "BrickLang Test 1.0"}
response = requests.get(url, headers=headers)
data = response.json()

posts_raw = data["data"]["children"]
step1_time = (time.perf_counter() - step1_start) * 1000
print(f"  ✅ Fetched {len(posts_raw)} posts ({step1_time:.2f}ms)")

# Step 2: Extract key fields
print("\n[2/5] Extracting key fields...")
step2_start = time.perf_counter()

posts = []
for item in posts_raw:
    post = item["data"]
    posts.append({
        "title": post.get("title", ""),
        "score": post.get("score", 0),
        "num_comments": post.get("num_comments", 0),
        "author": post.get("author", ""),
        "subreddit": post.get("subreddit", ""),
        "url": post.get("url", ""),
        "created_utc": post.get("created_utc", 0)
    })

step2_time = (time.perf_counter() - step2_start) * 1000
print(f"  ✅ Extracted {len(posts)} posts ({step2_time:.2f}ms)")

# Step 3: Filter high-quality posts
print("\n[3/5] Filtering posts (score > 100)...")
step3_start = time.perf_counter()

filtered_posts = [p for p in posts if p["score"] > 100]

step3_time = (time.perf_counter() - step3_start) * 1000
print(f"  ✅ Filtered to {len(filtered_posts)} posts ({step3_time:.2f}ms)")

# Step 4: Group by subreddit
print("\n[4/5] Grouping by subreddit...")
step4_start = time.perf_counter()

grouped = defaultdict(list)
for post in filtered_posts:
    grouped[post["subreddit"]].append(post)

grouped_dict = dict(grouped)
step4_time = (time.perf_counter() - step4_start) * 1000
print(f"  ✅ Grouped into {len(grouped_dict)} subreddits ({step4_time:.2f}ms)")

# Step 5: Save to JSON
print("\n[5/5] Saving to JSON...")
step5_start = time.perf_counter()

output = {
    "total_posts": len(posts),
    "filtered_posts": len(filtered_posts),
    "subreddits": len(grouped_dict),
    "data": grouped_dict
}

with open("reddit_traditional.json", "w") as f:
    json.dump(output, f, indent=2)

step5_time = (time.perf_counter() - step5_start) * 1000
print(f"  ✅ Saved to reddit_traditional.json ({step5_time:.2f}ms)")

# Summary
total_time = (time.perf_counter() - start_time) * 1000

print("\n" + "=" * 80)
print("TRADITIONAL PYTHON - COMPLETE!")
print("=" * 80)
print(f"\nStep Times:")
print(f"  1. Fetch:    {step1_time:7.2f}ms")
print(f"  2. Extract:  {step2_time:7.2f}ms")
print(f"  3. Filter:   {step3_time:7.2f}ms")
print(f"  4. Group:    {step4_time:7.2f}ms")
print(f"  5. Save:     {step5_time:7.2f}ms")
print(f"\nTotal Time:  {total_time:7.2f}ms")
print(f"\nLines of Code: ~60")
print("=" * 80)
