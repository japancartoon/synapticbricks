"""
BrickLang Core Library - Day 1: File I/O & HTTP Bricks

Building the first 20 essential bricks with full tests.
"""

import sys
import json
import csv
import os
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs

sys.path.insert(0, str(Path(__file__).parent))

from core import brick, BrickEngine, Pipeline

print("=" * 80)
print("BrickLang EPIC 1: Building First 20 Core Bricks")
print("=" * 80)

engine = BrickEngine(project_dir="core_library")

# ===== FILE I/O BRICKS (10) =====
print("\n[1/2] Building File I/O Bricks (10)...")

@brick("read_text_file", description="Read text file to string")
def read_text_file(filepath: str, encoding: str = "utf-8") -> str:
    """Read entire text file."""
    with open(filepath, 'r', encoding=encoding) as f:
        return f.read()

read_text_file.add_test(
    inputs={"filepath": __file__},  # Test with this file
    expected_output={
        lambda x: isinstance(x, str),
        lambda x: len(x) > 0,
        lambda x: "brick" in x  # This file contains "brick"
    },
    label="read_self_test"
)
engine.register(read_text_file)

@brick("write_text_file", description="Write string to file")
def write_text_file(filepath: str, content: str, encoding: str = "utf-8") -> bool:
    """Write text to file, returns True on success."""
    try:
        # Atomic write
        temp_path = Path(filepath).with_suffix('.tmp')
        with open(temp_path, 'w', encoding=encoding) as f:
            f.write(content)
        temp_path.replace(filepath)
        return True
    except Exception as e:
        return False

write_text_file.add_test(
    inputs={"filepath": "test_write.txt", "content": "Hello BrickLang!"},
    expected_output=True,
    label="write_test"
)
engine.register(write_text_file)

@brick("read_json", description="Parse JSON file to dict")
def read_json(filepath: str, encoding: str = "utf-8") -> Dict:
    """Read and parse JSON file."""
    with open(filepath, 'r', encoding=encoding) as f:
        return json.load(f)

read_json.add_test(
    inputs={"filepath": "bricklang/core_library/test.json"},
    expected_output=lambda x: isinstance(x, (dict, list)),
    label="read_json_test"
)
engine.register(read_json)

@brick("write_json", description="Save dict as JSON")
def write_json(filepath: str, data: Any, indent: int = 2) -> bool:
    """Write data as JSON file."""
    try:
        temp_path = Path(filepath).with_suffix('.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        temp_path.replace(filepath)
        return True
    except:
        return False

write_json.add_test(
    inputs={"filepath": "test_output.json", "data": {"test": "value"}},
    expected_output=True,
    label="write_json_test"
)
engine.register(write_json)

@brick("read_csv", description="Parse CSV file to list of dicts")
def read_csv(filepath: str, encoding: str = "utf-8") -> List[Dict]:
    """Read CSV file as list of dictionaries."""
    with open(filepath, 'r', encoding=encoding, newline='') as f:
        reader = csv.DictReader(f)
        return list(reader)

read_csv.add_test(
    inputs={"filepath": "bricklang/core_library/test.csv"},
    expected_output=lambda x: isinstance(x, list),
    label="read_csv_test"
)
engine.register(read_csv)

@brick("write_csv", description="Save list of dicts as CSV")
def write_csv(filepath: str, data: List[Dict], fieldnames: Optional[List[str]] = None) -> bool:
    """Write list of dicts to CSV."""
    try:
        if not data:
            return False
        
        fields = fieldnames or list(data[0].keys())
        temp_path = Path(filepath).with_suffix('.tmp')
        
        with open(temp_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
        
        temp_path.replace(filepath)
        return True
    except:
        return False

write_csv.add_test(
    inputs={"filepath": "test_output.csv", "data": [{"name": "test", "value": 1}]},
    expected_output=True,
    label="write_csv_test"
)
engine.register(write_csv)

@brick("list_files", description="List directory contents")
def list_files(directory: str, pattern: str = "*") -> List[str]:
    """List files in directory matching pattern."""
    path = Path(directory)
    if not path.exists():
        return []
    return [str(f) for f in path.glob(pattern)]

list_files.add_test(
    inputs={"directory": ".", "pattern": "*.py"},
    expected_output=lambda x: isinstance(x, list),
    label="list_files_test"
)
engine.register(list_files)

@brick("file_exists", description="Check if file exists")
def file_exists(filepath: str) -> bool:
    """Check if file or directory exists."""
    return Path(filepath).exists()

file_exists.add_test(
    inputs={"filepath": __file__},
    expected_output=True,
    label="file_exists_test"
)
engine.register(file_exists)

@brick("create_directory", description="Create directory")
def create_directory(dirpath: str, parents: bool = True) -> bool:
    """Create directory, optionally creating parents."""
    try:
        Path(dirpath).mkdir(parents=parents, exist_ok=True)
        return True
    except:
        return False

create_directory.add_test(
    inputs={"dirpath": "test_dir"},
    expected_output=True,
    label="create_dir_test"
)
engine.register(create_directory)

@brick("append_to_file", description="Append text to file")
def append_to_file(filepath: str, content: str, encoding: str = "utf-8") -> bool:
    """Append content to file."""
    try:
        with open(filepath, 'a', encoding=encoding) as f:
            f.write(content)
        return True
    except:
        return False

append_to_file.add_test(
    inputs={"filepath": "test_append.txt", "content": "New line\n"},
    expected_output=True,
    label="append_test"
)
engine.register(append_to_file)

print(f"  ✅ File I/O: 10/10 bricks registered")

# ===== HTTP BRICKS (10) =====
print("\n[2/2] Building HTTP Bricks (10)...")

@brick("http_get", description="HTTP GET request")
def http_get(url: str, headers: Optional[Dict] = None, timeout: int = 30) -> Dict:
    """Perform HTTP GET request."""
    try:
        response = requests.get(url, headers=headers or {}, timeout=timeout)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text,
            "success": response.ok
        }
    except Exception as e:
        return {
            "status_code": 0,
            "headers": {},
            "content": "",
            "success": False,
            "error": str(e)
        }

http_get.add_test(
    inputs={"url": "https://httpbin.org/get"},
    expected_output={
        "status_code": lambda x: x == 200,
        "success": True
    },
    label="http_get_test"
)
engine.register(http_get)

@brick("http_post", description="HTTP POST request with JSON")
def http_post(url: str, data: Dict, headers: Optional[Dict] = None, timeout: int = 30) -> Dict:
    """Perform HTTP POST request with JSON data."""
    try:
        headers = headers or {}
        headers['Content-Type'] = 'application/json'
        response = requests.post(url, json=data, headers=headers, timeout=timeout)
        return {
            "status_code": response.status_code,
            "content": response.text,
            "success": response.ok
        }
    except Exception as e:
        return {
            "status_code": 0,
            "content": "",
            "success": False,
            "error": str(e)
        }

http_post.add_test(
    inputs={"url": "https://httpbin.org/post", "data": {"test": "value"}},
    expected_output={
        "status_code": lambda x: x == 200,
        "success": True
    },
    label="http_post_test"
)
engine.register(http_post)

@brick("http_download", description="Download file from URL")
def http_download(url: str, filepath: str, chunk_size: int = 8192) -> bool:
    """Download file from URL."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        temp_path = Path(filepath).with_suffix('.tmp')
        with open(temp_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                f.write(chunk)
        
        temp_path.replace(filepath)
        return True
    except:
        return False

http_download.add_test(
    inputs={"url": "https://httpbin.org/robots.txt", "filepath": "test_download.txt"},
    expected_output=True,
    label="download_test"
)
engine.register(http_download)

@brick("parse_url", description="Parse URL into components")
def parse_url(url: str) -> Dict:
    """Parse URL into scheme, netloc, path, params, query, fragment."""
    parsed = urlparse(url)
    return {
        "scheme": parsed.scheme,
        "netloc": parsed.netloc,
        "path": parsed.path,
        "params": parsed.params,
        "query": dict(parse_qs(parsed.query)),
        "fragment": parsed.fragment,
        "hostname": parsed.hostname,
        "port": parsed.port
    }

parse_url.add_test(
    inputs={"url": "https://example.com:8080/path?key=value#anchor"},
    expected_output={
        "scheme": "https",
        "hostname": "example.com",
        "port": 8080
    },
    label="parse_url_test"
)
engine.register(parse_url)

@brick("build_url", description="Construct URL from components")
def build_url(scheme: str, netloc: str, path: str = "", query: Optional[Dict] = None) -> str:
    """Build URL from components."""
    query_string = urlencode(query or {})
    return urlunparse((scheme, netloc, path, "", query_string, ""))

build_url.add_test(
    inputs={"scheme": "https", "netloc": "example.com", "path": "/api", "query": {"key": "value"}},
    expected_output=lambda x: "https://example.com/api" in x and "key=value" in x,
    label="build_url_test"
)
engine.register(build_url)

@brick("add_auth_header", description="Add authorization header")
def add_auth_header(headers: Dict, token: str, auth_type: str = "Bearer") -> Dict:
    """Add authorization header to headers dict."""
    headers = headers.copy()
    headers['Authorization'] = f"{auth_type} {token}"
    return headers

add_auth_header.add_test(
    inputs={"headers": {}, "token": "abc123"},
    expected_output={"Authorization": "Bearer abc123"},
    label="auth_header_test"
)
engine.register(add_auth_header)

@brick("retry_request", description="Retry HTTP request with backoff")
def retry_request(url: str, max_retries: int = 3, backoff: float = 1.0) -> Dict:
    """Retry GET request with exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                return {
                    "status_code": response.status_code,
                    "content": response.text,
                    "success": True,
                    "attempts": attempt + 1
                }
        except:
            pass
        
        if attempt < max_retries - 1:
            time.sleep(backoff * (2 ** attempt))
    
    return {
        "status_code": 0,
        "content": "",
        "success": False,
        "attempts": max_retries,
        "error": "Max retries exceeded"
    }

retry_request.add_test(
    inputs={"url": "https://httpbin.org/get", "max_retries": 2},
    expected_output={
        "success": True,
        "attempts": lambda x: x >= 1
    },
    label="retry_test"
)
engine.register(retry_request)

@brick("check_status", description="Validate HTTP status code")
def check_status(status_code: int) -> Dict:
    """Check if status code is successful."""
    return {
        "code": status_code,
        "success": 200 <= status_code < 300,
        "client_error": 400 <= status_code < 500,
        "server_error": 500 <= status_code < 600,
        "message": {
            200: "OK",
            201: "Created",
            400: "Bad Request",
            401: "Unauthorized",
            404: "Not Found",
            500: "Internal Server Error"
        }.get(status_code, "Unknown")
    }

check_status.add_test(
    inputs={"status_code": 200},
    expected_output={"success": True, "message": "OK"},
    label="check_status_test"
)
engine.register(check_status)

@brick("parse_json_response", description="Parse JSON from HTTP response")
def parse_json_response(response: Dict) -> Dict:
    """Parse JSON content from HTTP response."""
    try:
        content = response.get("content", "")
        return {
            "data": json.loads(content),
            "success": True
        }
    except:
        return {
            "data": None,
            "success": False,
            "error": "Failed to parse JSON"
        }

parse_json_response.add_test(
    inputs={"response": {"content": '{"key": "value"}'}},
    expected_output={"data": {"key": "value"}, "success": True},
    label="parse_json_resp_test"
)
engine.register(parse_json_response)

@brick("handle_http_error", description="Handle HTTP errors gracefully")
def handle_http_error(response: Dict, retry_on_error: bool = False) -> Dict:
    """Handle HTTP response errors."""
    if response.get("success"):
        return {"handled": True, "error": None, "should_retry": False}
    
    status = response.get("status_code", 0)
    should_retry = retry_on_error and (status >= 500 or status == 0)
    
    return {
        "handled": True,
        "error": response.get("error", "Unknown error"),
        "status_code": status,
        "should_retry": should_retry,
        "error_type": "network" if status == 0 else "server" if status >= 500 else "client"
    }

handle_http_error.add_test(
    inputs={"response": {"success": False, "status_code": 500}, "retry_on_error": True},
    expected_output={"should_retry": True, "error_type": "server"},
    label="error_handler_test"
)
engine.register(handle_http_error)

print(f"  ✅ HTTP: 10/10 bricks registered")

# ===== SUMMARY =====
print("\n" + "=" * 80)
print("EPIC 1 - Day 1 COMPLETE!")
print("=" * 80)
print(f"\n✅ Total bricks: {len(engine.bricks)}")
print(f"✅ File I/O: 10 bricks")
print(f"✅ HTTP: 10 bricks")
print(f"\nAll bricks registered and ready to test!")
print("\nNext: Run demo pipeline (arXiv fetch → save)")
print("=" * 80)
