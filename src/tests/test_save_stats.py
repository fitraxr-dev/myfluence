"""
Test untuk melihat hasil save_user_data dengan username dan nickname di stats
"""
import json
import sys
from pathlib import Path

# Setup path
sys.path.append(str(Path(__file__).parent.parent))

from utils.save_data import save_user_data


def test_save_with_username_nickname():
    """Test save data dengan username dan nickname di stats"""
    
    # Sample data
    user_info = {
        'id': '7123456789',
        'username': 'dillaprb',
        'nickname': 'Dillah Probokusumo',
        'signature': 'Content Creator',
        'followers_count': 1968639,
        'total_likes': 143997693,
        'timestamp': '2025-11-11T20:00:00'
    }
    
    print("\n" + "="*60)
    print("Testing save_user_data with username & nickname in stats")
    print("="*60 + "\n")
    
    # Save data
    result = save_user_data(user_info, 'dillaprb')
    
    print(f"✓ Files saved:")
    print(f"  - Info: {result['info_file']}")
    print(f"  - Stats: {result['stats_file']}")
    
    # Read and display stats file
    with open(result['stats_file'], 'r', encoding='utf-8') as f:
        stats_data = json.load(f)
    
    print(f"\n📊 Stats file content:")
    print(json.dumps(stats_data, indent=2, ensure_ascii=False))
    
    # Verify
    print(f"\n✅ Verification:")
    print(f"  - Username in stats: {'✓' if 'username' in stats_data else '✗'}")
    print(f"  - Nickname in stats: {'✓' if 'nickname' in stats_data else '✗'}")
    print(f"  - Followers count: {'✓' if 'followers_count' in stats_data else '✗'}")
    print(f"  - Total likes: {'✓' if 'total_likes' in stats_data else '✗'}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    test_save_with_username_nickname()
