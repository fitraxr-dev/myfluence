"""
Test script untuk mengambil video TikTok dari user tertentu
dan menyimpannya ke file JSON
"""
import asyncio
import json
import sys
from pathlib import Path

# Setup path agar bisa import dari src
project_root = Path(__file__).parent  # tests folder
src_root = project_root.parent  # src folder
sys.path.append(str(src_root))

from services.influencer_data import get_user_videos


async def test_get_video(username, count=5):
    """
    Test fungsi get_user_videos dan simpan hasilnya ke file
    
    Args:
        username (str): Username TikTok yang akan diambil videonya
        count (int): Jumlah video yang diambil (default: 5)
    """
    print(f"\n{'='*60}")
    print(f"🎬 Testing Video Fetch for @{username}")
    print(f"{'='*60}\n")
    
    # Ambil data video
    video_data = await get_user_videos(username, count=count)
    
    # Cek apakah berhasil
    if video_data['success']:
        print(f"\n✅ Successfully fetched {video_data['total_videos']} videos!")
        
        # Buat folder untuk menyimpan hasil test (di src/data/videos)
        output_dir = src_root / "data" / "videos"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Simpan ke file dengan format username.video.json
        output_file = output_dir / f"{username}.video.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Video data saved to: {output_file}")
        print(f"\n📊 Video Summary:")
        print(f"   - Username: {video_data['username']}")
        print(f"   - Total Videos: {video_data['total_videos']}")
        print(f"   - Timestamp: {video_data['timestamp']}")
        
        # Tampilkan detail setiap video
        print(f"\n📹 Video Details:")
        for idx, video in enumerate(video_data['videos'], 1):
            print(f"\n   Video {idx}:")
            print(f"   - ID: {video['id']}")
            print(f"   - Description: {video['desc'][:50]}..." if len(video['desc']) > 50 else f"   - Description: {video['desc']}")
            # print(f"   - Created: {video['create_time']}")
            # print(f"   - Stats: {video['stats']['play_count']:,} views, {video['stats']['like_count']:,} likes")
            # print(f"   - URL: {video['video_url']}")
    else:
        print(f"\n❌ Failed to fetch videos!")
        print(f"   Error: {video_data['error']}")
    
    print(f"\n{'='*60}\n")
    return video_data


async def main():
    """
    Main test function - test dengan beberapa username
    """
    # Daftar username untuk di-test
    test_usernames = [
        "dillaprb",
        # Tambahkan username lain jika ingin test lebih banyak
        # "kevindikmanto",
        # "tasyafarasya",
    ]
    
    results = []
    
    for username in test_usernames:
        result = await test_get_video(username, count=5)
        results.append(result)
        
        # Delay antar request
        if username != test_usernames[-1]:
            print("⏳ Waiting 5 seconds before next request...\n")
            await asyncio.sleep(5)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 Test Summary")
    print(f"{'='*60}")
    print(f"Total tests: {len(results)}")
    print(f"Successful: {sum(1 for r in results if r['success'])}")
    print(f"Failed: {sum(1 for r in results if not r['success'])}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
