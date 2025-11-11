"""
Test script untuk debugging get_user_info
"""
import asyncio
import sys
from pathlib import Path

# Tambahkan src ke Python path
sys.path.append(str(Path(__file__).parent))

from services.influencer_data import get_user_info
from utils.save_data import save_user_data

async def main():
    # Test dengan satu user
    username = "dillaprb"
    
    print(f"Testing get_user_info for @{username}...")
    print("=" * 60)
    
    try:
        user_info = await get_user_info(username)
        
        print("\n[RESULT] User Info:")
        print("-" * 60)
        for key, value in user_info.items():
            print(f"{key:20s}: {value}")
        
        # Check jika data kosong
        if not user_info.get('id') and not user_info.get('nickname'):
            print("\n⚠️  WARNING: Data kosong!")
            print("Kemungkinan penyebab:")
            print("1. MS_TOKEN sudah expired")
            print("2. Username tidak ditemukan")
            print("3. TikTok mendeteksi bot (butuh proxy)")
            print("4. Response format berubah")
        else:
            print("\n✓ Data berhasil diambil!")
            
            # Save data
            saved_files = save_user_data(user_info, username)
            print(f"\n✓ Data saved to:")
            print(f"  - {saved_files['info_file']}")
            print(f"  - {saved_files['stats_file']}")
            
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}")
        print(f"   {e}")

if __name__ == "__main__":
    asyncio.run(main())
