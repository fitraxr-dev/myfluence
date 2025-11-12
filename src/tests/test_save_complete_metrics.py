"""
Test script untuk memverifikasi penyimpanan metrics lengkap
dengan avg_likes, avg_comments, avg_shares
"""
import json
from pathlib import Path
import sys

# Setup path
sys.path.append(str(Path(__file__).parent.parent))

from services.influencer_metrics import (
    calculate_engagement_rate,
    calculate_avg_engagement_rate_per_post,
    calculate_avg_posts_like,
    calculate_avg_posts_comment,
    calculate_avg_posts_shares
)


def test_save_complete_metrics(username):
    """Test untuk menyimpan metrics lengkap"""
    
    print(f"\n{'='*60}")
    print(f"Testing Complete Metrics Save for @{username}")
    print(f"{'='*60}\n")
    
    # Path ke data files
    data_dir = Path(__file__).parent.parent / "data"
    stats_file = data_dir / "stats" / f"{username}.stats.json"
    videos_file = data_dir / "videos" / f"{username}.video.json"
    
    # Cek file ada
    if not stats_file.exists() or not videos_file.exists():
        print(f"❌ Required files not found")
        return
    
    # Load data
    with open(stats_file, 'r', encoding='utf-8') as f:
        stats_data = json.load(f)
    
    with open(videos_file, 'r', encoding='utf-8') as f:
        video_data = json.load(f)
    
    videos = video_data.get('videos', [])
    
    # Hitung semua metrics
    engagement_rate = calculate_engagement_rate(stats_data, videos)
    avg_engagement_per_post = calculate_avg_engagement_rate_per_post(videos)
    avg_likes = calculate_avg_posts_like(videos)
    avg_comments = calculate_avg_posts_comment(videos)
    avg_shares = calculate_avg_posts_shares(videos)
    
    # Simpan metrics
    metrics_dir = data_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    
    metrics_data = {
        'username': username,
        'nickname': video_data.get('nickname', ''),
        'followers_count': stats_data.get('followers_count', 0),
        'total_videos_analyzed': len(videos),
        'engagement_rate': engagement_rate,
        'avg_engagement_per_post': avg_engagement_per_post,
        'avg_likes': avg_likes,
        'avg_comments': avg_comments,
        'avg_shares': avg_shares,
        'timestamp': video_data.get('timestamp', '')
    }
    
    metrics_file = metrics_dir / f"{username}.metrics.json"
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Metrics saved to: {metrics_file.name}\n")
    
    # Display metrics
    print(f"📊 Complete Metrics for @{username}:")
    print("-"*60)
    print(f"Username: @{metrics_data['username']}")
    print(f"Nickname: {metrics_data['nickname']}")
    print(f"Followers: {metrics_data['followers_count']:,}")
    print(f"Videos Analyzed: {metrics_data['total_videos_analyzed']}")
    
    print(f"\n🎯 Engagement Metrics:")
    print(f"  - Engagement Rate: {metrics_data['engagement_rate']}%")
    print(f"  - Avg Engagement/Post: {metrics_data['avg_engagement_per_post']}%")
    
    print(f"\n📈 Average Per Post:")
    print(f"  - Avg Likes: {metrics_data['avg_likes']:,.2f}")
    print(f"  - Avg Comments: {metrics_data['avg_comments']:,.2f}")
    print(f"  - Avg Shares: {metrics_data['avg_shares']:,.2f}")
    
    print(f"\n{'='*60}\n")
    
    # Verify file content
    print(f"📄 File Content:")
    print("-"*60)
    print(json.dumps(metrics_data, indent=2, ensure_ascii=False))
    print(f"\n{'='*60}\n")


def main():
    """Test untuk beberapa influencer"""
    influencers = [
        "dillaprb",
        "kevindikmanto",
        "tasyafarasya",
    ]
    
    for username in influencers:
        test_save_complete_metrics(username)


if __name__ == "__main__":
    main()
