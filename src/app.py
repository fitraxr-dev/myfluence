import asyncio
import time
import json
from pathlib import Path
from services.influencer_data import get_user_info, get_user_videos
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
        
        # Delay antar request (kecuali yang terakhir)
        if idx < total:
            print(f"  ⏳ Waiting {DELAY_BETWEEN_REQUESTS}s...")
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Completed:")
    print(f"  - User Info: {success_info}/{total} success")
    print(f"  - Videos: {success_videos}/{total} success")

if __name__ == "__main__":
    asyncio.run(main())