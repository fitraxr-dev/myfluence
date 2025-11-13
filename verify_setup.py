#!/usr/bin/env python3
"""Verification script to check MyFluence setup.

This script verifies that:
1. All required directories exist
2. Configuration is loaded correctly
3. Required dependencies are installed
4. Data files are present
5. MongoDB connection works (if configured)
"""
import sys
from pathlib import Path

def check_imports():
    """Check if all required imports are available."""
    print("🔍 Checking required dependencies...")
    
    missing = []
    
    try:
        import pymongo
        print("  ✓ pymongo")
    except ImportError:
        print("  ✗ pymongo (required for MongoDB insertion)")
        missing.append("pymongo")
    
    try:
        import dotenv
        print("  ✓ python-dotenv")
    except ImportError:
        print("  ✗ python-dotenv (required for configuration)")
        missing.append("python-dotenv")
    
    if missing:
        print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
        print("  Install with: pip install " + " ".join(missing))
        return False
    
    print("  ✓ All dependencies installed")
    return True


def check_directories():
    """Check if all required directories exist."""
    print("\n🔍 Checking directory structure...")
    
    base_dir = Path(__file__).parent
    required_dirs = [
        "src/data",
        "src/data/videos",
        "src/data/metrics",
        "src/data/sentiment",
        "src/data/info",
        "src/data/stats",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = base_dir / dir_path
        if full_path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} (missing)")
            all_exist = False
    
    if not all_exist:
        print("\n⚠ Some directories are missing")
        return False
    
    print("  ✓ All directories exist")
    return True


def check_config():
    """Check if configuration is properly set up."""
    print("\n🔍 Checking configuration...")
    
    env_file = Path(__file__).parent / "src" / ".env"
    
    if not env_file.exists():
        print("  ✗ src/.env file not found")
        print("  ℹ Copy src/.env.example to src/.env and configure it")
        return False
    
    print("  ✓ src/.env file exists")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from config import (
            MONGODB_URI, MONGODB_DATABASE, DEFAULT_COUNTRY,
            DATA_DIR, VIDEOS_DIR, METRICS_DIR
        )
        
        print(f"  ✓ MongoDB URI: {MONGODB_URI}")
        print(f"  ✓ Database: {MONGODB_DATABASE}")
        print(f"  ✓ Default Country: {DEFAULT_COUNTRY}")
        print(f"  ✓ Data Directory: {DATA_DIR}")
        return True
        
    except ImportError as e:
        print(f"  ✗ Failed to load config: {e}")
        return False


def check_data_files():
    """Check if data files are present."""
    print("\n🔍 Checking data files...")
    
    base_dir = Path(__file__).parent
    data_dir = base_dir / "src" / "data"
    
    video_files = list((data_dir / "videos").glob("*.video.json"))
    metrics_files = list((data_dir / "metrics").glob("*.er_metrics.json"))
    sentiment_files = list((data_dir / "sentiment").glob("*_sentiment.json"))
    info_files = list((data_dir / "info").glob("*.info.json"))
    
    print(f"  ✓ Video files: {len(video_files)}")
    print(f"  ✓ Metrics files: {len(metrics_files)}")
    print(f"  ✓ Sentiment files: {len(sentiment_files)}")
    print(f"  ✓ Info files: {len(info_files)}")
    
    if len(video_files) == 0 or len(metrics_files) == 0:
        print("\n  ⚠ No data files found - required files (videos, metrics) are missing")
        print("  ℹ Make sure to scrape data first or add data files to src/data/")
        return False
    
    # Check if we have matching files
    video_usernames = {f.stem.replace('.video', '') for f in video_files}
    metrics_usernames = {f.stem.replace('.er_metrics', '') for f in metrics_files}
    matching = video_usernames & metrics_usernames
    
    print(f"  ✓ Matching creators: {len(matching)}")
    if matching:
        print(f"    Usernames: {', '.join(sorted(matching))}")
    
    return len(matching) > 0


def check_mongodb():
    """Check MongoDB connection."""
    print("\n🔍 Checking MongoDB connection...")
    
    try:
        from pymongo import MongoClient
        sys.path.insert(0, str(Path(__file__).parent / "src"))
        from config import MONGODB_URI, MONGODB_DATABASE
        
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        
        print(f"  ✓ Connected to MongoDB")
        print(f"  ✓ Database: {MONGODB_DATABASE}")
        
        # List collections
        db = client[MONGODB_DATABASE]
        collections = db.list_collection_names()
        if collections:
            print(f"  ✓ Existing collections: {', '.join(collections)}")
        else:
            print(f"  ℹ No collections yet (will be created on first insert)")
        
        client.close()
        return True
        
    except ImportError:
        print("  ⚠ pymongo not installed (required for MongoDB features)")
        return False
    except Exception as e:
        print(f"  ✗ MongoDB connection failed: {e}")
        print("  ℹ Make sure MongoDB is running and connection details are correct")
        return False


def main():
    """Run all verification checks."""
    print("="*50)
    print("MyFluence Setup Verification")
    print("="*50)
    
    checks = [
        ("Dependencies", check_imports),
        ("Directories", check_directories),
        ("Configuration", check_config),
        ("Data Files", check_data_files),
        ("MongoDB", check_mongodb),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n✗ {name} check failed with error: {e}")
            results[name] = False
    
    print("\n" + "="*50)
    print("Summary")
    print("="*50)
    
    for name, result in results.items():
        status = "✓" if result else "✗"
        print(f"{status} {name}: {'OK' if result else 'FAILED'}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ All checks passed! You're ready to use MyFluence.")
        print("\nNext steps:")
        print("  1. Run transformation: ./run_transform.sh")
        print("  2. Insert to MongoDB: ./run_transform.sh --insert")
    else:
        print("⚠ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Create .env file: cp src/.env.example src/.env")
        print("  - Start MongoDB: systemctl start mongodb")
    print("="*50)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
