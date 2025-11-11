import asyncio
import time
from services.influencer_data import get_user_info
from utils.save_data import save_user_data

# Daftar influencer yang akan di-scrape
INFLUENCERS = [
    "dillaprb",
    "kevindikmanto",
    "tasyafarasya",
    "tasyiiathasyia",
    "maharajasp8",
    "doctor.incognito_99"
]

DELAY_BETWEEN_REQUESTS = 5  # detik

async def main():
    """Process semua influencer"""
    total = len(INFLUENCERS)
    success = 0
    
    print(f"Processing {total} influencers...")
    print("=" * 60)
    
    for idx, username in enumerate(INFLUENCERS, 1):
        print(f"\n[{idx}/{total}] @{username}")
        
        # Ambil dan simpan data (get_user_info adalah async, butuh await)
        user_info = await get_user_info(username)
        
        if user_info.get('success'):
            save_user_data(user_info, username)
            success += 1
        
        # Delay antar request (kecuali yang terakhir)
        if idx < total:
            print(f"  ⏳ Waiting {DELAY_BETWEEN_REQUESTS}s...")
            time.sleep(DELAY_BETWEEN_REQUESTS)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Completed: {success}/{total} success")

if __name__ == "__main__":
    asyncio.run(main())