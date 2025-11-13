#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TikTok KOL Data Transformer and MongoDB Importer.

This module provides tools to transform TikTok Key Opinion Leader (KOL) data
from multiple JSON sources into a structured MongoDB schema. It automatically
discovers, matches, and processes creator data files from organized directories.

The transformation pipeline:
    1. Discovers creator files across multiple directories
    2. Matches files by username with fuzzy matching support
    3. Transforms raw JSON into MongoDB-compatible document structures
    4. Generates JSONL files for inspection or manual import
    5. Optionally performs direct MongoDB insertion with reference resolution

Directory Structure:
    src/data/
        videos/         - *.video.json (video statistics per creator)
        metrics/        - *.er_metrics.json (engagement metrics)
        sentiment/      - *_sentiment.json (sentiment analysis results)
        info/           - *.info.json (creator profile information)
        stats/          - *.stats.json (additional statistics)

Output Collections:
    - content_creators: Creator profile information
    - accounts: Platform-specific account data with historical snapshots
    - posts: Individual post/video data with engagement metrics
    - account_metrics_daily: Time series data for account metrics
    - sentiment_summaries: Aggregated sentiment analysis results

MongoDB Schema:
    Follows standardized schema with ObjectId references between collections.
    See inline documentation for detailed schema specifications.

Usage:
    # Generate JSONL files only
    $ python transform_kol_data.py

    # Generate JSONL and insert into MongoDB
    $ python transform_kol_data.py --insert

    # Custom data directory
    $ python transform_kol_data.py --data-dir /path/to/data

    # Custom output directory
    $ python transform_kol_data.py --outdir /path/to/output

Dependencies:
    - Python 3.10+
    - pymongo (required for --insert functionality)
    - python-dotenv (for environment variable management)

Configuration:
    Set environment variables in src/.env file:
    - MONGODB_HOST: MongoDB host (default: localhost)
    - MONGODB_PORT: MongoDB port (default: 27017)
    - MONGODB_DATABASE: Database name (default: myfluence)
    - MONGODB_USERNAME: MongoDB username (optional)
    - MONGODB_PASSWORD: MongoDB password (optional)
    - DEFAULT_COUNTRY: Default country code (default: ID)
"""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

try:
    from pymongo import MongoClient
    from pymongo.errors import BulkWriteError
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False
    MongoClient = None
    BulkWriteError = None

# Import configuration
try:
    from config import (
        MONGODB_URI, MONGODB_DATABASE, DEFAULT_COUNTRY,
        DATA_DIR, VIDEOS_DIR, METRICS_DIR, SENTIMENT_DIR, 
        INFO_DIR, OUTPUT_DIR
    )
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    # Fallback defaults if config not available
    MONGODB_URI = "mongodb://localhost:27017/"
    MONGODB_DATABASE = "myfluence"
    DEFAULT_COUNTRY = "ID"
    DATA_DIR = Path(__file__).parent / "data"
    VIDEOS_DIR = DATA_DIR / "videos"
    METRICS_DIR = DATA_DIR / "metrics"
    SENTIMENT_DIR = DATA_DIR / "sentiment"
    INFO_DIR = DATA_DIR / "info"
    OUTPUT_DIR = Path(__file__).parent.parent / "output"


def to_int(x: Any, default: Optional[int] = None) -> Optional[int]:
    """Converts a value to integer with fallback handling.
    
    Attempts to convert the input to an integer. If direct conversion fails,
    tries converting through float first. Returns default if all conversions fail.
    
    Args:
        x: The value to convert. Can be None, numeric string, float, or int.
        default: Value to return if conversion fails. Defaults to None.
    
    Returns:
        The converted integer value, or the default if conversion fails.
    """
    try:
        if x is None:
            return default
        return int(x)
    except Exception:
        try:
            return int(float(x))
        except Exception:
            return default


def iso_from_epoch(sec: Any) -> Optional[str]:
    """Converts Unix epoch timestamp to ISO 8601 format string.
    
    Args:
        sec: Unix epoch timestamp in seconds. Can be int, float, or string.
    
    Returns:
        ISO 8601 formatted datetime string in UTC timezone, or None if conversion fails.
    """
    sec_i = to_int(sec)
    if sec_i is None:
        return None
    return datetime.fromtimestamp(sec_i, tz=timezone.utc).isoformat()


def read_json(path: Path) -> Dict[str, Any]:
    """Reads and parses a JSON file.
    
    Args:
        path: Path object pointing to the JSON file to read.
    
    Returns:
        Dictionary containing the parsed JSON data.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_jsonl(path: Path, docs: List[Dict[str, Any]]) -> None:
    """Writes a list of documents to a JSON Lines (.jsonl) file.
    
    Args:
        path: Path object specifying where to write the JSONL file.
        docs: List of dictionaries to write, one per line.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")


def extract_username_from_filename(filename: str) -> Optional[str]:
    """Extracts username from standardized filename patterns.
    
    Supports multiple filename patterns:
    - {username}.video.json (video data files)
    - {username}.er_metrics.json (engagement metrics files)
    - {username}_sentiment.json (sentiment analysis files)
    - {username}.info.json (creator info files)
    - {username}.stats.json (statistics files)
    
    Args:
        filename: The filename string to parse.
    
    Returns:
        The extracted username, or None if pattern doesn't match.
    """
    if filename.endswith('.video.json'):
        return filename.replace('.video.json', '')
    elif filename.endswith('.er_metrics.json'):
        return filename.replace('.er_metrics.json', '')
    elif filename.endswith('_sentiment.json'):
        return filename.replace('_sentiment.json', '')
    elif filename.endswith('.info.json'):
        return filename.replace('.info.json', '')
    elif filename.endswith('.stats.json'):
        return filename.replace('.stats.json', '')
    return None


def discover_creators(videos_dir: Path, metrics_dir: Path, sentiment_dir: Path, 
                     info_dir: Path) -> Dict[str, Dict[str, Optional[Path]]]:
    """Discovers and matches creator data files across multiple directories.
    
    Args:
        videos_dir: Path to directory containing video JSON files.
        metrics_dir: Path to directory containing engagement metrics files.
        sentiment_dir: Path to directory containing sentiment analysis files.
        info_dir: Path to directory containing creator info files.
    
    Returns:
        Dictionary mapping username to file paths.
    """
    creator_files: Dict[str, Dict[str, Optional[Path]]] = {}
    
    # Scan videos directory
    if videos_dir.exists():
        for file in videos_dir.glob('*.video.json'):
            username = extract_username_from_filename(file.name)
            if username:
                if username not in creator_files:
                    creator_files[username] = {
                        'video': None, 'metrics': None, 
                        'sentiment': None, 'info': None
                    }
                creator_files[username]['video'] = file
    
    # Scan metrics directory
    if metrics_dir.exists():
        for file in metrics_dir.glob('*.er_metrics.json'):
            username = extract_username_from_filename(file.name)
            if username:
                if username not in creator_files:
                    creator_files[username] = {
                        'video': None, 'metrics': None, 
                        'sentiment': None, 'info': None
                    }
                creator_files[username]['metrics'] = file
    
    # Scan sentiment directory
    if sentiment_dir.exists():
        for file in sentiment_dir.glob('*_sentiment.json'):
            username = extract_username_from_filename(file.name)
            if username:
                if username not in creator_files:
                    creator_files[username] = {
                        'video': None, 'metrics': None, 
                        'sentiment': None, 'info': None
                    }
                creator_files[username]['sentiment'] = file
    
    # Scan info directory
    if info_dir.exists():
        for file in info_dir.glob('*.info.json'):
            username = extract_username_from_filename(file.name)
            if username:
                if username not in creator_files:
                    creator_files[username] = {
                        'video': None, 'metrics': None, 
                        'sentiment': None, 'info': None
                    }
                creator_files[username]['info'] = file
    
    return creator_files


def parse_iso_timestamp(ts_str: Optional[str]) -> Optional[int]:
    """Parses ISO 8601 timestamp string to Unix epoch seconds.
    
    Args:
        ts_str: ISO 8601 formatted timestamp string.
    
    Returns:
        Unix epoch timestamp in seconds (integer), or None if parsing fails.
    """
    if not ts_str:
        return None
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return int(dt.timestamp())
    except Exception:
        return None


def transform_tiktok_data(video_data: Dict[str, Any], metrics_data: Dict[str, Any],
                          info_data: Optional[Dict[str, Any]], username: str, 
                          country: Optional[str] = "ID") -> Tuple[List, List, List, List]:
    """Transforms TikTok creator data into MongoDB-compatible document structures.
    
    Args:
        video_data: Dictionary containing video information.
        metrics_data: Dictionary containing account metrics.
        info_data: Dictionary containing creator info (optional).
        username: The username/handle of the creator.
        country: ISO country code (default: "ID" for Indonesia).
    
    Returns:
        Tuple containing four lists: creators, accounts, posts, account_ts
    """
    # Generate creator_id
    nickname = video_data.get("nickname") or metrics_data.get("nickname")
    creator_id = f"kol_{username}"
    
    # Get additional info from info_data
    signature = None
    platform_user_id = username
    if info_data:
        signature = info_data.get("signature")
        platform_user_id = info_data.get("id", username)
    
    # Collection: content_creators
    creators = [{
        "creator_id": creator_id,
        "name": nickname,
        "handle_primary": username,
        "categories": [],
        "bio": signature,
        "country": country,
        "tags": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }]

    # Collection: accounts
    snap_ts_str = metrics_data.get("timestamp")
    snap_ts_int = parse_iso_timestamp(snap_ts_str)
    followers_count = to_int(metrics_data.get("followers_count"))
    total_videos = to_int(metrics_data.get("total_videos_analyzed"))
    engagement_rate = metrics_data.get("engagement_rate")
    
    # Calculate total likes from videos
    total_likes = 0
    if video_data.get("videos"):
        for v in video_data["videos"]:
            if isinstance(v.get("stats"), dict):
                like_count = to_int(v["stats"].get("likeCount"), 0)
                if like_count is not None:
                    total_likes += like_count
    
    snap_ts_any = snap_ts_int
    
    accounts = [{
        "creator_id": creator_id,
        "platform": "tiktok",
        "platform_user_id": platform_user_id,
        "username": username,
        "nickname": nickname,
        "verified": None,
        "profile_signature": signature,
        "avatar_url": None,
        "meta": {
            "engagement_rate": engagement_rate
        },
        "current_counters": {
            "followers": followers_count,
            "hearts_total": total_likes,
            "videos_total": total_videos
        },
        "snapshots": [
            {
                "ts": iso_from_epoch(snap_ts_any) or datetime.now(timezone.utc).isoformat(),
                "followers": followers_count,
                "hearts_total": total_likes,
                "videos_total": total_videos
            }
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }]

    # Collection: posts
    posts: List[Dict[str, Any]] = []
    for v in video_data.get("videos", []):
        video_id = v.get("videoId")
        if not video_id:
            continue
        
        video_url = v.get("videoUrl")
        stats_obj = v.get("stats", {}) or {}
        
        views = to_int(stats_obj.get("viewCount"))
        likes = to_int(stats_obj.get("likeCount"))
        comments = to_int(stats_obj.get("commentCount"))
        shares = to_int(stats_obj.get("shareCount"))
        bookmarks = None
        
        engagement_total = (likes or 0) + (comments or 0) + (shares or 0)
        
        view_to_engagement_ratio_pct = None
        if views and views > 0 and engagement_total > 0:
            view_to_engagement_ratio_pct = round((engagement_total / views) * 100, 2)
        
        er_pct = None

        posts.append({
            "account_id_ref": username,
            "platform": "tiktok",
            "post_id": video_id,
            "post_url": video_url,
            "created_at_platform": None,
            "caption": None,
            "language": None,
            "hashtags": [],
            "media": {
                "duration_sec": None,
                "video_height": None,
                "video_width": None,
                "cover": None,
                "music_title": None,
                "music_author": None
            },
            "stats": {
                "views": views,
                "likes": likes,
                "comments": comments,
                "shares": shares,
                "bookmarks": bookmarks
            },
            "engagement": {
                "total": engagement_total,
                "view_to_engagement_ratio_pct": view_to_engagement_ratio_pct,
                "er_pct": er_pct
            },
            "pin_flags": {},
            "labels": [],
            "created_at_ingest": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        })

    # Collection: account_metrics_daily
    account_ts: List[Dict[str, Any]] = []
    if snap_ts_any is not None:
        dt = datetime.fromtimestamp(snap_ts_any, tz=timezone.utc)
        dt_floor = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)
        account_ts.append({
            "account_id_ref": username,
            "date": dt_floor.isoformat(),
            "followers": followers_count,
            "hearts_total": total_likes,
            "videos_total": total_videos
        })
    
    return creators, accounts, posts, account_ts


def load_sentiment(sent_path: Path) -> Dict[str, Any]:
    """Loads sentiment data from a JSON file with error handling.
    
    Args:
        sent_path: Path to the sentiment JSON file.
    
    Returns:
        Dictionary containing sentiment data, or empty dict if loading fails.
    """
    try:
        with open(sent_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def build_sentiment_summary(sent: Dict[str, Any], username: str) -> List[Dict[str, Any]]:
    """Builds sentiment summary document following MongoDB schema.
    
    Args:
        sent: Dictionary containing sentiment analysis results.
        username: Username for account reference.
    
    Returns:
        List containing a single sentiment summary document, or empty list if invalid.
    """
    if not isinstance(sent, dict) or not sent:
        return []

    pos = to_int(sent.get("positive"))
    neu = to_int(sent.get("neutral"))
    neg = to_int(sent.get("negative"))
    total = to_int(sent.get("total"))
    
    # Calculate SS = (Np - Nn) / Ntotal * 100
    net_sentiment_score_pct = None
    if total and total > 0 and pos is not None and neg is not None:
        net_sentiment_score_pct = round(((pos - neg) / total) * 100, 2)
    else:
        try:
            score_val = sent.get("sentiment_score")
            if score_val is not None:
                net_sentiment_score_pct = float(score_val)
        except Exception:
            pass

    doc = {
        "account_id_ref": username,
        "post_id": None,
        "window": {
            "type": "sample",
            "size": total if total else None
        },
        "counts": {
            "positive": pos,
            "negative": neg,
            "neutral": neu,
            "total": total
        },
        "net_sentiment_score_pct": net_sentiment_score_pct,
        "engagement_reference": {
            "followers_at_calc": None,
            "er_pct": None,
            "fsi": None
        },
        "computed_at": datetime.now(timezone.utc).isoformat()
    }

    return [doc]


def process_sentiment(sentiment_path: Optional[Path], username: str) -> List[Dict[str, Any]]:
    """Processes sentiment file and generates sentiment summary documents.
    
    Args:
        sentiment_path: Path to sentiment JSON file, or None if not available.
        username: Username for account reference.
    
    Returns:
        List containing sentiment summary documents, or empty list if unavailable.
    """
    if sentiment_path is None or not sentiment_path.exists():
        return []
    
    sent = load_sentiment(sentiment_path)
    if not sent:
        return []
    
    return build_sentiment_summary(sent, username)


def insert_to_mongodb(
    creators: List[Dict[str, Any]],
    accounts: List[Dict[str, Any]],
    posts: List[Dict[str, Any]],
    account_ts: List[Dict[str, Any]],
    sentiments: List[Dict[str, Any]],
    mongo_uri: str,
    db_name: str
) -> Dict[str, Any]:
    """Inserts transformed data into MongoDB with reference resolution.
    
    Args:
        creators: List of content_creators documents to insert.
        accounts: List of accounts documents to insert.
        posts: List of posts documents with temporary "account_id_ref" fields.
        account_ts: List of account_metrics_daily documents.
        sentiments: List of sentiment_summaries documents.
        mongo_uri: MongoDB connection URI.
        db_name: Name of the database to insert into.
    
    Returns:
        Dictionary containing insertion statistics for each collection.
    """
    if not PYMONGO_AVAILABLE or MongoClient is None or BulkWriteError is None:
        raise ImportError("pymongo is not available. Install it with: pip install pymongo")
    
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    results = {
        "content_creators": {"inserted": 0, "errors": 0},
        "accounts": {"inserted": 0, "errors": 0},
        "posts": {"inserted": 0, "errors": 0},
        "account_metrics_daily": {"inserted": 0, "errors": 0},
        "sentiment_summaries": {"inserted": 0, "errors": 0}
    }
    
    account_id_map: Dict[str, Any] = {}
    
    # 1. Insert content_creators
    if creators:
        try:
            result = db.content_creators.insert_many(creators, ordered=False)
            results["content_creators"]["inserted"] = len(result.inserted_ids)
        except BulkWriteError as e:
            results["content_creators"]["inserted"] = e.details.get("nInserted", 0)
            results["content_creators"]["errors"] = len(e.details.get("writeErrors", []))
        except Exception as e:
            print(f"Error inserting content_creators: {e}")
    
    # 2. Insert accounts and build account_id_map
    if accounts:
        try:
            result = db.accounts.insert_many(accounts, ordered=False)
            results["accounts"]["inserted"] = len(result.inserted_ids)
            # Build mapping: username -> account ObjectId
            for idx, account in enumerate(accounts):
                if idx < len(result.inserted_ids):
                    account_id_map[account['username']] = result.inserted_ids[idx]
        except BulkWriteError as e:
            results["accounts"]["inserted"] = e.details.get("nInserted", 0)
            results["accounts"]["errors"] = len(e.details.get("writeErrors", []))
        except Exception as e:
            print(f"Error inserting accounts: {e}")
    
    # 3. Insert posts - resolve account_id references
    if posts and account_id_map:
        posts_to_insert = []
        for post in posts:
            account_ref = post.pop("account_id_ref", None)
            if account_ref and account_ref in account_id_map:
                post["account_id"] = account_id_map[account_ref]
                posts_to_insert.append(post)
        
        if posts_to_insert:
            try:
                result = db.posts.insert_many(posts_to_insert, ordered=False)
                results["posts"]["inserted"] = len(result.inserted_ids)
            except BulkWriteError as e:
                results["posts"]["inserted"] = e.details.get("nInserted", 0)
                results["posts"]["errors"] = len(e.details.get("writeErrors", []))
            except Exception as e:
                print(f"Error inserting posts: {e}")
    
    # 4. Insert account_metrics_daily - resolve account_id references
    if account_ts and account_id_map:
        metrics_to_insert = []
        for metric in account_ts:
            account_ref = metric.pop("account_id_ref", None)
            if account_ref and account_ref in account_id_map:
                metric["account_id"] = account_id_map[account_ref]
                metrics_to_insert.append(metric)
        
        if metrics_to_insert:
            try:
                result = db.account_metrics_daily.insert_many(metrics_to_insert, ordered=False)
                results["account_metrics_daily"]["inserted"] = len(result.inserted_ids)
            except BulkWriteError as e:
                results["account_metrics_daily"]["inserted"] = e.details.get("nInserted", 0)
                results["account_metrics_daily"]["errors"] = len(e.details.get("writeErrors", []))
            except Exception as e:
                print(f"Error inserting account_metrics_daily: {e}")
    
    # 5. Insert sentiment_summaries - resolve account_id references
    if sentiments and account_id_map:
        sentiments_to_insert = []
        for sentiment in sentiments:
            account_ref = sentiment.pop("account_id_ref", None)
            if account_ref and account_ref in account_id_map:
                sentiment["account_id"] = account_id_map[account_ref]
                sentiments_to_insert.append(sentiment)
        
        if sentiments_to_insert:
            try:
                result = db.sentiment_summaries.insert_many(sentiments_to_insert, ordered=False)
                results["sentiment_summaries"]["inserted"] = len(result.inserted_ids)
            except BulkWriteError as e:
                results["sentiment_summaries"]["inserted"] = e.details.get("nInserted", 0)
                results["sentiment_summaries"]["errors"] = len(e.details.get("writeErrors", []))
            except Exception as e:
                print(f"Error inserting sentiment_summaries: {e}")
    
    client.close()
    return results


def main():
    """Main entry point for TikTok KOL data transformation and MongoDB insertion."""
    ap = argparse.ArgumentParser(
        description="Transform TikTok KOL JSON from data directories into MongoDB-ready JSONL and optionally insert into MongoDB."
    )
    ap.add_argument("--data-dir", type=Path, default=DATA_DIR,
                    help=f"Base data directory (default: {DATA_DIR})")
    ap.add_argument("--outdir", type=Path, default=OUTPUT_DIR,
                    help=f"Output directory for JSONL files (default: {OUTPUT_DIR})")
    ap.add_argument("--country", default=DEFAULT_COUNTRY,
                    help=f"Country code to store in creators (default: {DEFAULT_COUNTRY})")
    ap.add_argument("--mongo-uri", type=str, default=MONGODB_URI,
                    help=f"MongoDB connection URI (default: from config)")
    ap.add_argument("--db-name", type=str, default=MONGODB_DATABASE,
                    help=f"MongoDB database name (default: {MONGODB_DATABASE})")
    ap.add_argument("--insert", action="store_true",
                    help="Insert data directly into MongoDB after generating JSONL files")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    videos_dir = data_dir / "videos"
    metrics_dir = data_dir / "metrics"
    sentiment_dir = data_dir / "sentiment"
    info_dir = data_dir / "info"
    outdir = Path(args.outdir)
    
    # Discover all creator files
    print("Discovering creator files...")
    print(f"  Videos: {videos_dir}")
    print(f"  Metrics: {metrics_dir}")
    print(f"  Sentiment: {sentiment_dir}")
    print(f"  Info: {info_dir}")
    
    creator_files = discover_creators(videos_dir, metrics_dir, sentiment_dir, info_dir)
    
    if not creator_files:
        print("Error: No creator files found in the specified directories")
        return
    
    print(f"Found {len(creator_files)} creators to process")
    
    # Process all creators
    all_creators: List[Dict[str, Any]] = []
    all_accounts: List[Dict[str, Any]] = []
    all_posts: List[Dict[str, Any]] = []
    all_account_ts: List[Dict[str, Any]] = []
    all_sentiments: List[Dict[str, Any]] = []
    
    for username, paths in creator_files.items():
        print(f"\nProcessing: {username}")
        
        # Load video data (required)
        if not paths['video']:
            print(f"  ⚠ Skipping {username}: no video file found")
            continue
        
        video_data = read_json(paths['video'])
        
        # Load metrics data (required)
        if not paths['metrics']:
            print(f"  ⚠ Skipping {username}: no metrics file found")
            continue
        
        metrics_data = read_json(paths['metrics'])
        
        # Load info data (optional)
        info_data = None
        if paths['info']:
            info_data = read_json(paths['info'])
            print(f"  ✓ Loaded info data")
        
        # Transform data
        creators, accounts, posts, account_ts = transform_tiktok_data(
            video_data, metrics_data, info_data, username, country=args.country
        )
        
        all_creators.extend(creators)
        all_accounts.extend(accounts)
        all_posts.extend(posts)
        all_account_ts.extend(account_ts)
        
        print(f"  ✓ Transformed {len(posts)} posts")
        
        # Process sentiment if available
        if paths['sentiment']:
            sentiments = process_sentiment(paths['sentiment'], username)
            all_sentiments.extend(sentiments)
            print(f"  ✓ Processed sentiment data")
        else:
            print(f"  ℹ No sentiment data available")
    
    # Write all outputs
    print(f"\nWriting output files to {outdir}...")
    write_jsonl(outdir / "creators.jsonl", all_creators)
    write_jsonl(outdir / "accounts.jsonl", all_accounts)
    write_jsonl(outdir / "posts.jsonl", all_posts)
    write_jsonl(outdir / "account_metrics_daily.jsonl", all_account_ts)
    write_jsonl(outdir / "sentiment_summaries.jsonl", all_sentiments)
    
    result = {
        "counts": {
            "creators": len(all_creators),
            "accounts": len(all_accounts),
            "posts": len(all_posts),
            "account_metrics_daily": len(all_account_ts),
            "sentiment_summaries": len(all_sentiments)
        },
        "outdir": str(outdir)
    }
    
    print("✓ JSONL files written successfully")
    
    # MongoDB insertion (optional)
    if args.insert:
        if not PYMONGO_AVAILABLE:
            print("\n✗ Error: pymongo is not installed. Install it with: pip install pymongo")
            return
        
        print("\nInserting data into MongoDB...")
        print(f"  URI: {args.mongo_uri}")
        print(f"  Database: {args.db_name}")
        
        mongo_results = insert_to_mongodb(
            all_creators, all_accounts, all_posts, all_account_ts, all_sentiments,
            args.mongo_uri, args.db_name
        )
        
        result["mongodb_insertion"] = mongo_results
        print(f"\n✓ MongoDB insertion completed:")
        print(f"  - Database: {args.db_name}")
        print(f"  - content_creators: {mongo_results['content_creators']['inserted']} inserted, {mongo_results['content_creators']['errors']} errors")
        print(f"  - accounts: {mongo_results['accounts']['inserted']} inserted, {mongo_results['accounts']['errors']} errors")
        print(f"  - posts: {mongo_results['posts']['inserted']} inserted, {mongo_results['posts']['errors']} errors")
        print(f"  - account_metrics_daily: {mongo_results['account_metrics_daily']['inserted']} inserted, {mongo_results['account_metrics_daily']['errors']} errors")
        print(f"  - sentiment_summaries: {mongo_results['sentiment_summaries']['inserted']} inserted, {mongo_results['sentiment_summaries']['errors']} errors")
    
    print("\n" + "="*50)
    print("Summary:")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
