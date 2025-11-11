from TikTokApi import TikTokApi
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import os
import json

# Load environment variables dari file .env
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Ambil konfigurasi dari .env
ms_token = os.getenv('MS_TOKEN')
browser = os.getenv('TIKTOK_BROWSER', 'chromium')

async def get_user_info(username):
    """
    Mengambil informasi user dari TikTok dengan skema terstruktur
    
    Args:
        username (str): Username TikTok
    
    Returns:
        dict: Data user dengan skema:
            - id: User ID
            - username: uniqueId
            - nickname: Display name
            - signature: Bio/signature
            - followers_count: Jumlah followers
            - total_likes: Total likes (heart_count)
            - timestamp: Waktu pengambilan data
            - success: Boolean untuk status berhasil/gagal
            - error: Pesan error jika gagal
    """
    try:
        print(f"  📡 Connecting to TikTok API...")
        
        async with TikTokApi() as api:
            # Buat session dengan timeout lebih panjang
            await api.create_sessions(
                ms_tokens=[ms_token], 
                num_sessions=1, 
                sleep_after=3,
                browser=browser,
                headless=True  # Run browser tanpa GUI untuk lebih cepat
            )
            
            print(f"  🔍 Fetching data for @{username}...")
            user = api.user(username=username)
            raw_user_info = await user.info()
            
            # Ekstrak data dari struktur: userInfo -> user & statsV2
            user_data = raw_user_info.get('userInfo', {}).get('user', {})
            stats_data = raw_user_info.get('userInfo', {}).get('statsV2', {})
            
            # Validasi data
            if not user_data.get('id'):
                raise ValueError(f"User @{username} not found or data incomplete")
            
            structured_info = {
                'id': user_data.get('id', ''),
                'username': user_data.get('uniqueId', ''),
                'nickname': user_data.get('nickname', ''),
                'signature': user_data.get('signature', ''),
                'followers_count': int(stats_data.get('followerCount', 0)),
                'total_likes': int(stats_data.get('heartCount', 0)),
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'error': None
            }
            
            print(f"  ✓ Data fetched successfully!")
            return structured_info
            
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        print(f"  ❌ Error: {error_type}")
        print(f"     {error_msg[:150]}")
        
        # Return data dengan error flag
        return {
            'id': '',
            'username': username,
            'nickname': '',
            'signature': '',
            'followers_count': 0,
            'total_likes': 0,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': f"{error_type}: {error_msg[:100]}"
        }

async def get_user_videos(username, count=5):
    """
    Mengambil video terbaru dari user TikTok (return raw data apa adanya)
    
    Args:
        username (str): Username TikTok
        count (int): Jumlah video yang diambil (default: 5)
    
    Returns:
        dict: Data videos dengan skema:
            - username: Username
            - total_videos: Jumlah video yang diambil
            - videos: List raw video data dari TikTok API
            - timestamp: Waktu pengambilan data
            - success: Boolean untuk status berhasil/gagal
            - error: Pesan error jika gagal
    """
    print(f"  📡 Connecting to TikTok API...")
    
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token], 
            num_sessions=1, 
            sleep_after=3,
            browser=browser,
            headless=True
        )
        
        print(f"  🎬 Fetching {count} videos from @{username}...")
        user = api.user(username=username)
        
        videos_data = []
        video_count = 0
        
        async for video in user.videos(count=count):
            # Batasi secara manual untuk memastikan hanya mengambil sejumlah count
            if video_count >= count:
                break
                
            video_count += 1
            
            # Ambil data video apa adanya dari TikTok API
            video_raw_data = video.as_dict
            
            videos_data.append(video_raw_data)
            print(f"    [{video_count}/{count}] Video ID: {video.id}")
        
        # Return data tanpa menyimpan ke file
        result = {
            'username': username,
            'total_videos': len(videos_data),
            'videos': videos_data,
            'timestamp': datetime.now().isoformat(),
            'success': True,
            'error': None
        }
        
        print(f"  ✓ {len(videos_data)} videos fetched successfully!")
        return result