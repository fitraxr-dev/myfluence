import asyncio
import time
import json
from pathlib import Path
from services.influencer_data import get_user_info, get_user_videos
from services.influencer_metrics import calculate_engagement_rate, calculate_avg_engagement_rate_per_post
from utils.save_data import save_user_data

# Daftar influencer yang akan di-scrape
INFLUENCERS = [
    "dillaprb",
    "kevindikmanto",
    "tasyafarasya",
    "tasyiiathasyia",
    "maharajasp8",
    "doctor.incognito_99",
    "fadiljaidi"
]

DELAY_BETWEEN_REQUESTS = 5  # detik

async def main():
    """Process semua influencer"""
    total = len(INFLUENCERS)
    success_info = 0
    success_videos = 0
    success_metrics = 0
    
    print(f"Processing {total} influencers...")
    print("=" * 60)
    
    for idx, username in enumerate(INFLUENCERS, 1):
        print(f"\n[{idx}/{total}] @{username}")
        
        # 1. Ambil dan simpan data user info
        user_info = await get_user_info(username)
        
        if user_info.get('success'):
            save_user_data(user_info, username)
            success_info += 1
        
        # 2. Ambil dan simpan data 5 video terbaru
        print(f"\n  📹 Fetching videos...")
        video_data = await get_user_videos(username, count=5)
        
        if video_data.get('success'):
            # Simpan ke file videos
            video_dir = Path(__file__).parent / "data" / "videos"
            video_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = video_dir / f"{username}.video.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(video_data, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ {len(video_data['videos'])} videos saved to {output_file.name}")
            success_videos += 1
            
            # 3. Hitung engagement rate metrics
            print(f"\n  📊 Calculating engagement metrics...")
            
            # Load stats data untuk mendapatkan followers count
            stats_file = Path(__file__).parent / "data" / "stats" / f"{username}.stats.json"
            stats_data = {}
            if stats_file.exists():
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats_data = json.load(f)
            
            videos = video_data.get('videos', [])
            
            # Hitung metrics
            engagement_rate = calculate_engagement_rate(stats_data, videos)
            avg_engagement_per_post = calculate_avg_engagement_rate_per_post(videos)
            
            # Simpan metrics ke file
            metrics_dir = Path(__file__).parent / "data" / "metrics"
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
            
            print(f"  ✓ Metrics calculated and saved:")
            print(f"    - Engagement Rate: {engagement_rate}%")
            print(f"    - Avg Engagement/Post: {avg_engagement_per_post}%")
            success_metrics += 1
        
        # Delay antar request (kecuali yang terakhir)
        if idx < total:
            print(f"  ⏳ Waiting {DELAY_BETWEEN_REQUESTS}s...")
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Completed:")
    print(f"  - User Info: {success_info}/{total} success")
    print(f"  - Videos: {success_videos}/{total} success")
    print(f"  - Metrics: {success_metrics}/{total} success")

if __name__ == "__main__":
    asyncio.run(main())