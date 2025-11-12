"""
Test script untuk fungsi calculate_avg_posts_like, calculate_avg_posts_comment, calculate_avg_posts_shares
"""
import sys
from pathlib import Path

# Setup path
sys.path.append(str(Path(__file__).parent.parent))

from services.influencer_metrics import (
    calculate_avg_posts_like,
    calculate_avg_posts_comment,
    calculate_avg_posts_shares,
    get_influencer_metrics
)
import json


def test_avg_functions():
    """Test fungsi rata-rata likes, comments, shares"""
    
    # Sample video data
    videos = [
        {
            'videoId': '123',
            'stats': {
                'viewCount': 1000000,
                'likeCount': 50000,
                'commentCount': 500,
                'shareCount': 200
            }
        },
        {
            'videoId': '456',
            'stats': {
                'viewCount': 2000000,
                'likeCount': 100000,
                'commentCount': 1000,
                'shareCount': 400
            }
        },
        {
            'videoId': '789',
            'stats': {
                'viewCount': 1500000,
                'likeCount': 75000,
                'commentCount': 750,
                'shareCount': 300
            }
        }
    ]
    
    print("\n" + "="*60)
    print("Testing Average Posts Metrics Functions")
    print("="*60 + "\n")
    
    print("📹 Sample Data (3 videos):")
    for idx, video in enumerate(videos, 1):
        stats = video['stats']
        print(f"\n  Video {idx}:")
        print(f"    Likes: {stats['likeCount']:,}")
        print(f"    Comments: {stats['commentCount']:,}")
        print(f"    Shares: {stats['shareCount']:,}")
    
    # Calculate averages
    avg_likes = calculate_avg_posts_like(videos)
    avg_comments = calculate_avg_posts_comment(videos)
    avg_shares = calculate_avg_posts_shares(videos)
    
    print("\n" + "-"*60)
    print("📊 Calculated Averages:")
    print("-"*60)
    print(f"  Average Likes/Post: {avg_likes:,.2f}")
    print(f"  Average Comments/Post: {avg_comments:,.2f}")
    print(f"  Average Shares/Post: {avg_shares:,.2f}")
    
    # Manual verification
    print("\n" + "-"*60)
    print("✅ Manual Verification:")
    print("-"*60)
    total_likes = sum(v['stats']['likeCount'] for v in videos)
    total_comments = sum(v['stats']['commentCount'] for v in videos)
    total_shares = sum(v['stats']['shareCount'] for v in videos)
    
    print(f"  Total Likes: {total_likes:,} / 3 = {total_likes/3:,.2f}")
    print(f"  Total Comments: {total_comments:,} / 3 = {total_comments/3:,.2f}")
    print(f"  Total Shares: {total_shares:,} / 3 = {total_shares/3:,.2f}")
    
    print("\n" + "="*60 + "\n")


def test_with_real_data():
    """Test dengan data real dari file"""
    username = "dillaprb"
    
    print("\n" + "="*60)
    print(f"Testing with Real Data: @{username}")
    print("="*60 + "\n")
    
    # Load video data
    video_file = Path(__file__).parent.parent / "data" / "videos" / f"{username}.video.json"
    
    if not video_file.exists():
        print(f"❌ Video file not found: {video_file}")
        return
    
    with open(video_file, 'r', encoding='utf-8') as f:
        video_data = json.load(f)
    
    videos = video_data.get('videos', [])
    
    if not videos:
        print("❌ No videos found in data")
        return
    
    # Calculate metrics
    avg_likes = calculate_avg_posts_like(videos)
    avg_comments = calculate_avg_posts_comment(videos)
    avg_shares = calculate_avg_posts_shares(videos)
    
    print(f"Username: @{video_data.get('username', '')}")
    print(f"Nickname: {video_data.get('nickname', '')}")
    print(f"Total Videos Analyzed: {len(videos)}")
    
    print("\n📊 Average Per Post Metrics:")
    print("-"*60)
    print(f"  Average Likes/Post: {avg_likes:,.2f}")
    print(f"  Average Comments/Post: {avg_comments:,.2f}")
    print(f"  Average Shares/Post: {avg_shares:,.2f}")
    
    print("\n📹 Individual Video Stats:")
    print("-"*60)
    for idx, video in enumerate(videos, 1):
        stats = video['stats']
        print(f"\n  Video {idx} (ID: {video['videoId']}):")
        print(f"    Likes: {stats['likeCount']:,}")
        print(f"    Comments: {stats['commentCount']:,}")
        print(f"    Shares: {stats['shareCount']:,}")
    
    print("\n" + "="*60 + "\n")


def main():
    """Main test function"""
    # Test dengan sample data
    test_avg_functions()
    
    # Test dengan real data
    test_with_real_data()


if __name__ == "__main__":
    main()
