"""
Real-world BrickLang Test: Web Scraper + Data Pipeline
Project: Scrape GitHub trending repos and save to JSON

This tests:
1. Network operations (fetch URL)
2. HTML parsing (extract data)
3. Data validation (check fields)
4. Data transformation (clean/format)
5. File I/O (save results)
6. Self-healing (when things break)
"""

from synapticbricks.core import (
    brick, Brick,
    BrickEngine,
    Pipeline,
    BrickTester,
    BrickHealer,
    LabelRegistry
)
import json
from typing import Dict, List, Any
from datetime import datetime

# Initialize engine
engine = BrickEngine(project_dir="test_github_scraper")

# ===== BRICK 1: Fetch URL =====
@brick("fetch_html", description="Fetch HTML content from URL")
def fetch_html(url: str) -> Dict[str, Any]:
    """
    Simulate fetching HTML (in real version, use requests)
    """
    # Mock data for testing
    mock_html = """
    <article class="repo">
        <h2>awesome-python</h2>
        <p class="description">A curated list of awesome Python frameworks</p>
        <span class="stars">45,678</span>
    </article>
    <article class="repo">
        <h2>FastAPI</h2>
        <p class="description">Modern Python web framework</p>
        <span class="stars">62,341</span>
    </article>
    """
    return {
        "url": url,
        "html": mock_html,
        "status": 200,
        "timestamp": datetime.now().isoformat()
    }

fetch_html.add_test(
    inputs={"url": "https://github.com/trending"},
    expected_output={
        "url": "https://github.com/trending",
        "html": lambda x: isinstance(x, str) and len(x) > 0,
        "status": 200,
        "timestamp": lambda x: isinstance(x, str)
    },
    label="basic_fetch"
)

# ===== BRICK 2: Parse HTML =====
@brick("parse_repos", description="Extract repo data from HTML")
def parse_repos(html: str) -> List[Dict[str, str]]:
    """
    Simple parser - extract repo name, description, stars
    """
    repos = []
    
    # Simple string parsing (real version would use BeautifulSoup)
    sections = html.split('<article class="repo">')
    
    for section in sections[1:]:  # Skip first empty split
        repo = {}
        
        # Extract name
        if '<h2>' in section:
            start = section.find('<h2>') + 4
            end = section.find('</h2>')
            repo['name'] = section[start:end].strip()
        
        # Extract description
        if '<p class="description">' in section:
            start = section.find('<p class="description">') + 23
            end = section.find('</p>')
            repo['description'] = section[start:end].strip()
        
        # Extract stars
        if '<span class="stars">' in section:
            start = section.find('<span class="stars">') + 20
            end = section.find('</span>')
            repo['stars'] = section[start:end].strip()
        
        if repo.get('name'):
            repos.append(repo)
    
    return repos

parse_repos.add_test(
    inputs={
        "html": '<article class="repo"><h2>test-repo</h2><p class="description">Test desc</p><span class="stars">100</span></article>'
    },
    expected_output=[{
        "name": "test-repo",
        "description": "Test desc",
        "stars": "100"
    }],
    label="parse_single"
)

# ===== BRICK 3: Validate Repos =====
@brick("validate_repos", description="Validate repo data structure")
def validate_repos(repos: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Check if all repos have required fields
    """
    valid = []
    invalid = []
    
    required_fields = ["name", "description", "stars"]
    
    for repo in repos:
        missing = [f for f in required_fields if f not in repo or not repo[f]]
        
        if missing:
            invalid.append({
                "repo": repo.get("name", "unknown"),
                "missing_fields": missing
            })
        else:
            valid.append(repo)
    
    return {
        "valid_count": len(valid),
        "invalid_count": len(invalid),
        "valid_repos": valid,
        "validation_errors": invalid
    }

validate_repos.add_test(
    inputs={
        "repos": [
            {"name": "repo1", "description": "desc1", "stars": "100"},
            {"name": "repo2", "description": "", "stars": "200"}  # Missing description
        ]
    },
    expected_output={
        "valid_count": 1,
        "invalid_count": 1,
        "valid_repos": [{"name": "repo1", "description": "desc1", "stars": "100"}],
        "validation_errors": lambda x: len(x) == 1
    },
    label="validation_check"
)

# ===== BRICK 4: Transform Data =====
@brick("transform_repos", description="Clean and format repo data")
def transform_repos(repos: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Transform raw data:
    - Convert stars from string to int
    - Add metadata
    - Clean descriptions
    """
    transformed = []
    
    for repo in repos:
        cleaned = {
            "name": repo["name"],
            "description": repo["description"].strip(),
            "stars": int(repo["stars"].replace(",", "")),
            "scraped_at": datetime.now().isoformat(),
            "source": "github_trending"
        }
        transformed.append(cleaned)
    
    return transformed

transform_repos.add_test(
    inputs={
        "repos": [{"name": "test", "description": "  desc  ", "stars": "1,234"}]
    },
    expected_output=[{
        "name": "test",
        "description": "desc",
        "stars": 1234,
        "scraped_at": lambda x: isinstance(x, str),
        "source": "github_trending"
    }],
    label="transform_basic"
)

# ===== BRICK 5: Save to JSON =====
@brick("save_json", description="Save data to JSON file")
def save_json(data: List[Dict[str, Any]], filepath: str) -> Dict[str, Any]:
    """
    Save data to JSON file
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return {
            "status": "success",
            "filepath": filepath,
            "records_saved": len(data)
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "filepath": filepath
        }

save_json.add_test(
    inputs={
        "data": [{"test": "data"}],
        "filepath": "test_output.json"
    },
    expected_output={
        "status": "success",
        "filepath": "test_output.json",
        "records_saved": 1
    },
    label="save_basic"
)

# ===== REGISTER ALL BRICKS =====
print("Registering bricks...")
engine.register(fetch_html)
engine.register(parse_repos)
engine.register(validate_repos)
engine.register(transform_repos)
engine.register(save_json)

print(f"\nRegistered {len(engine.bricks)} bricks")
for brick_id in engine.bricks.keys():
    brick_obj = engine.bricks[brick_id]
    print(f"  {brick_obj.label.full if brick_obj.label else 'no-label'} -> {brick_id}")

# ===== BUILD PIPELINE =====
print("\nBuilding pipeline...")
pipeline = Pipeline("github_scraper", engine)

# Step 1: Fetch HTML
pipeline.add_step(
    "fetch_html",
    input_map={"url": "url"},
    output_key="fetch_result"
)

# Step 2: Parse repos
pipeline.add_step(
    "parse_repos",
    input_map={"html": "fetch_result.html"},
    output_key="raw_repos"
)

# Step 3: Validate
pipeline.add_step(
    "validate_repos",
    input_map={"repos": "raw_repos"},
    output_key="validation"
)

# Step 4: Transform valid repos
pipeline.add_step(
    "transform_repos",
    input_map={"repos": "validation.valid_repos"},
    output_key="clean_repos"
)

# Step 5: Save to file
pipeline.add_step(
    "save_json",
    input_map={
        "data": "clean_repos",
        "filepath": "filepath"
    },
    output_key="save_result"
)

# ===== TEST ALL BRICKS =====
print("\nTesting all bricks...")
tester = BrickTester(engine)
report = tester.test_all()

print(f"\nTest Results: {report['status']}")
print(f"  Passed: {report['passed']}")
print(f"  Failed: {report['failed']}")
print(f"  Total: {report['total_tests']}")

if report["status"] != "all_passed":
    print("\nTest failures detected:")
    for brick_id, result in report["results"].items():
        if result["failed"] > 0:
            print(f"  X {brick_id}: {result['failed']} tests failed")

# ===== RUN PIPELINE =====
print("\nRunning pipeline...")
try:
    result = pipeline.run({
        "url": "https://github.com/trending",
        "filepath": "trending_repos.json"
    })
    
    print("\nPipeline execution successful!")
    print(f"  Success: {result['success']}")
    print(f"  Data keys: {list(result['data'].keys())}")
    print(f"  Final result: {result['result'][:200] if isinstance(result['result'], str) else result['result']}")
    
except Exception as e:
    print(f"\nX Pipeline failed: {e}")
    
    # Attempt self-healing
    print("\nAttempting self-healing...")
    healer = BrickHealer(engine, tester)
    diagnosis = healer.diagnose()
    
    if diagnosis["broken_bricks"]:
        print(f"\nFound {len(diagnosis['broken_bricks'])} broken bricks:")
        
        for broken in diagnosis["broken_bricks"]:
            print(f"\n  Brick: {broken['brick_id']}")
            print(f"  Tests failed: {broken['test_failures']}")
            
            # Create repair request
            repair = healer.create_repair_request(broken["brick_id"])
            print(f"\n  AI Repair Prompt:")
            print("  " + "="*60)
            print(repair.to_prompt().replace("\n", "\n  "))
            print("  " + "="*60)

# ===== FINAL REPORT =====
print("\n" + "="*70)
print("BrickLang Real-World Test Complete")
print("="*70)
print(f"Bricks created: {len(engine.bricks)}")
print(f"Pipeline steps: {len(pipeline.steps)}")
print(f"Tests passed: {report['passed']}/{report['total_tests']}")
print(f"Label system: {'Working' if all(engine.bricks[b].label for b in engine.bricks) else 'Failed'}")
print("="*70)
