"""
Test script untuk menguji fitur engagement metrics di app.py
dengan satu influencer saja
"""
import asyncio
import time
import json
from pathlib import Path
import sys

# Setup path
sys.path.append(str(Path(__file__).parent.parent))

from services.influencer_data import get_user_info, get_user_videos
from services.influencer_metrics import calculate_engagement_rate, calculate_avg_engagement_rate_per_post
from utils.save_data import save_user_data


async def test_single_influencer():
    """Test untuk satu influencer"""
    username = "dillaprb"
    
    print(f"\n{'='*60}")
    print(f"Testing Engagement Metrics Feature")
    print(f"{'='*60}\n")
    print(f"Testing with @{username}\n")
    
    # 1. Ambil dan simpan data user info
    print(f"[1/3] Fetching user info...")
    user_info = await get_user_info(username)
    
    if user_info.get('success'):
        save_user_data(user_info, username)
        print(f"  ✓ User info saved")
    
    # 2. Ambil dan simpan data 5 video terbaru
    print(f"\n[2/3] Fetching videos...")
    video_data = await get_user_videos(username, count=5)
    
    if video_data.get('success'):
        # Simpan ke file videos
        video_dir = Path(__file__).parent.parent / "data" / "videos"
        video_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = video_dir / f"{username}.video.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✓ {len(video_data['videos'])} videos saved")
        
        # 3. Hitung engagement rate metrics
        print(f"\n[3/3] Calculating engagement metrics...")
        
        # Load stats data
        stats_file = Path(__file__).parent.parent / "data" / "stats" / f"{username}.stats.json"
        stats_data = {}
        if stats_file.exists():
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats_data = json.load(f)
        
        videos = video_data.get('videos', [])
        
        # Hitung metrics
        engagement_rate = calculate_engagement_rate(stats_data, videos)
        avg_engagement_per_post = calculate_avg_engagement_rate_per_post(videos)
        
        # Simpan metrics ke file
        metrics_dir = Path(__file__).parent.parent / "data" / "metrics"
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
        
        print(f"  ✓ Metrics calculated and saved to {metrics_file.name}")
        print(f"\n{'='*60}")
        print(f"📊 Engagement Metrics Results:")
        print(f"{'='*60}")
        print(f"Username: @{metrics_data['username']}")
        print(f"Nickname: {metrics_data['nickname']}")
        print(f"Followers: {metrics_data['followers_count']:,}")
        print(f"Videos Analyzed: {metrics_data['total_videos_analyzed']}")
        print(f"\n🎯 Metrics:")
        print(f"  - Engagement Rate: {metrics_data['engagement_rate']}%")
        print(f"  - Avg Engagement/Post: {metrics_data['avg_engagement_per_post']}%")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(test_single_influencer())
