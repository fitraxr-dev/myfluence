"""
Test script untuk menghitung metrics dari data yang sudah ada
"""
import json
from pathlib import Path
import sys

# Setup path
sys.path.append(str(Path(__file__).parent.parent))

from services.influencer_metrics import calculate_engagement_rate, calculate_avg_engagement_rate_per_post


def calculate_and_save_metrics(username):
    """Hitung dan simpan metrics untuk influencer yang sudah punya data"""
    
    print(f"\n{'='*60}")
    print(f"Calculating Metrics for @{username}")
    print(f"{'='*60}\n")
    
    # Path ke data files
    data_dir = Path(__file__).parent.parent / "data"
    stats_file = data_dir / "stats" / f"{username}.stats.json"
    videos_file = data_dir / "videos" / f"{username}.video.json"
    
    # Cek file ada
    if not stats_file.exists():
        print(f"❌ Stats file not found: {stats_file}")
        return
    
    if not videos_file.exists():
        print(f"❌ Videos file not found: {videos_file}")
        return
    
    # Load data
    with open(stats_file, 'r', encoding='utf-8') as f:
        stats_data = json.load(f)
    
    with open(videos_file, 'r', encoding='utf-8') as f:
        video_data = json.load(f)
    
    videos = video_data.get('videos', [])
    
    # Hitung metrics
    engagement_rate = calculate_engagement_rate(stats_data, videos)
    avg_engagement_per_post = calculate_avg_engagement_rate_per_post(videos)
    
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
        'timestamp': video_data.get('timestamp', '')
    }
    
    metrics_file = metrics_dir / f"{username}.er_metrics.json"
    with open(metrics_file, 'w', encoding='utf-8') as f:
        json.dump(metrics_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Metrics saved to: {metrics_file.name}\n")
    print(f"📊 Results:")
    print(f"  Username: @{metrics_data['username']}")
    print(f"  Nickname: {metrics_data['nickname']}")
    print(f"  Followers: {metrics_data['followers_count']:,}")
    print(f"  Videos Analyzed: {metrics_data['total_videos_analyzed']}")
    print(f"\n🎯 Engagement Metrics:")
    print(f"  - Engagement Rate: {metrics_data['engagement_rate']}%")
    print(f"  - Avg Engagement/Post: {metrics_data['avg_engagement_per_post']}%")
    print(f"\n{'='*60}\n")


def main():
    """Test untuk semua influencer yang ada datanya"""
    influencers = [
        "dillaprb",
        "kevindikmanto",
        "tasyafarasya",
        "tasyiiathasyia",
        "maharajasp8",
        "doctor.incognito_99",
        "fadiljaidi"
    ]
    
    for username in influencers:
        calculate_and_save_metrics(username)


if __name__ == "__main__":
    main()
