"""
Test script untuk save_user_data
"""
import sys
from pathlib import Path

# Tambahkan src ke Python path
sys.path.append(str(Path(__file__).parent))

from utils.save_data import save_user_data, load_user_info, load_user_stats, load_user_data

# Contoh data user dari get_user_info
sample_user_info = {
    'id': '7123456789',
    'username': 'testuser',
    'nickname': 'Test User',
    'signature': 'This is a test bio',
    'followers_count': 150000,
    'total_likes': 2500000,
    'timestamp': '2025-11-11T10:30:45.123456'
}

print("Testing save_user_data...")
print("-" * 60)

# Test 1: Save data
print("\n1. Saving user data...")
saved_files = save_user_data(sample_user_info, 'testuser')
print(f"   ✓ Info saved to: {saved_files['info_file']}")
print(f"   ✓ Stats saved to: {saved_files['stats_file']}")

# Test 2: Load info
print("\n2. Loading info data...")
info_data = load_user_info('testuser')
print(f"   Info data: {info_data}")

# Test 3: Load stats
print("\n3. Loading stats data...")
stats_data = load_user_stats('testuser')
print(f"   Stats data: {stats_data}")

# Test 4: Load combined data
print("\n4. Loading combined data...")
combined_data = load_user_data('testuser')
print(f"   Combined data: {combined_data}")

print("\n" + "=" * 60)
print("Test completed! ✓")
print("\nFile structure:")
print("  src/data/info/testuser.info.json")
print("  src/data/stats/testuser.stats.json")
