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
    Mengambil video terbaru dari user TikTok dengan struktur data terformat
    
    Args:
        username (str): Username TikTok
        count (int): Jumlah video yang diambil (default: 5)
    
    Returns:
        dict: Data videos dengan skema:
            - username: Username (uniqueId)
            - nickname: Display name
            - videos: List video dengan struktur:
                - videoId: ID video
                - videoUrl: URL video TikTok
                - stats: Statistik video (viewCount, likeCount, commentCount, shareCount)
            - timestamp: Waktu pengambilan data
            - success: Boolean untuk status berhasil/gagal
            - error: Pesan error jika gagal
    """
    try:
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
            
            # Ambil info user untuk mendapatkan nickname
            user_info = await user.info()
            user_data = user_info.get('userInfo', {}).get('user', {})
            nickname = user_data.get('nickname', '')
            
            videos_data = []
            video_count = 0
            
            async for video in user.videos(count=count):
                # Batasi secara manual untuk memastikan hanya mengambil sejumlah count
                if video_count >= count:
                    break
                    
                video_count += 1
                
                # Ekstrak data video dengan struktur yang diminta
                video_dict = video.as_dict
                stats = video_dict.get('stats', {})
                
                video_info = {
                    'videoId': video.id,
                    'videoUrl': f"https://www.tiktok.com/@{username}/video/{video.id}",
                    'stats': {
                        'viewCount': stats.get('playCount', 0),
                        'likeCount': stats.get('diggCount', 0),
                        'commentCount': stats.get('commentCount', 0),
                        'shareCount': stats.get('shareCount', 0)
                    }
                }
                
                videos_data.append(video_info)
                print(f"    [{video_count}/{count}] Video ID: {video.id}")
            
            # Return data dengan struktur yang diminta
            result = {
                'username': username,
                'nickname': nickname,
                'videos': videos_data,
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'error': None
            }
            
            print(f"  ✓ {len(videos_data)} videos fetched successfully!")
            return result
            
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        
        print(f"  ❌ Error: {error_type}")
        print(f"     {error_msg[:150]}")
        
        return {
            'username': username,
            'nickname': '',
            'videos': [],
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': f"{error_type}: {error_msg[:100]}"
        }