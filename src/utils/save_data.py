import json
from pathlib import Path
from datetime import datetime

def save_user_data(user_info, username):
    """
    Menyimpan data user ke 2 file terpisah:
    1. username.info.json (id, username, nickname, signature) di src/data/info
    2. username.stats.json (username, nickname, followers_count, total_likes, timestamp) di src/data/stats
    
    Args:
        user_info (dict): Data user dari get_user_info()
        username (str): Username TikTok (tanpa @)
    
    Returns:
        dict: Path ke file-file yang disimpan
    """
    # Buat folder src/data/info dan src/data/stats jika belum ada
    info_dir = Path(__file__).parent.parent / "data" / "info"
    stats_dir = Path(__file__).parent.parent / "data" / "stats"
    info_dir.mkdir(parents=True, exist_ok=True)
    stats_dir.mkdir(parents=True, exist_ok=True)
    
    # Pisahkan data info dan stats
    info_data = {
        'id': user_info.get('id', ''),
        'username': user_info.get('username', ''),
        'nickname': user_info.get('nickname', ''),
        'signature': user_info.get('signature', '')
    }
    
    stats_data = {
        'username': user_info.get('username', ''),
        'nickname': user_info.get('nickname', ''),
        'followers_count': user_info.get('followers_count', 0),
        'total_likes': user_info.get('total_likes', 0),
        'timestamp': user_info.get('timestamp', datetime.now().isoformat())
    }
    
    # Simpan ke file info
    info_file = info_dir / f"{username}.info.json"
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(info_data, f, indent=2, ensure_ascii=False)
    
    # Simpan ke file stats
    stats_file = stats_dir / f"{username}.stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats_data, f, indent=2, ensure_ascii=False)
    
    return {
        'info_file': info_file,
        'stats_file': stats_file
    }

# Tetap pertahankan fungsi lama untuk backward compatibility
def save_user_info(user_info, username):
    """
    Menyimpan informasi user ke file JSON di folder src/data/info
    (Deprecated: Gunakan save_user_data untuk format baru)
    
    Args:
        user_info (dict): Data user dari get_user_info()
        username (str): Username TikTok (tanpa @)
    
    Returns:
        Path: Path ke file yang disimpan
    """
    # Buat folder src/data/info jika belum ada
    data_dir = Path(__file__).parent.parent / "data" / "info"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Buat nama file dengan format username.info.json
    output_file = data_dir / f"{username}.info.json"
    
    # Tambahkan timestamp ke data
    user_info['saved_at'] = datetime.now().isoformat()
    
    # Simpan ke file JSON dengan format rapi
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(user_info, f, indent=2, ensure_ascii=False)
    
    return output_file

def save_multiple_users_info(users_data, output_filename="users_info.json"):
    """
    Menyimpan informasi beberapa user sekaligus ke satu file JSON
    
    Args:
        users_data (dict): Dictionary berisi data beberapa user
        output_filename (str): Nama file output
    
    Returns:
        Path: Path ke file yang disimpan
    """
    # Buat folder src/data/info jika belum ada
    data_dir = Path(__file__).parent.parent / "data" / "info"
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Buat path file output
    output_file = data_dir / output_filename
    
    # Tambahkan timestamp
    data_to_save = {
        'saved_at': datetime.now().isoformat(),
        'total_users': len(users_data),
        'users': users_data
    }
    
    # Simpan ke file JSON dengan format rapi
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, indent=2, ensure_ascii=False)
    
    return output_file

def load_user_info(username):
    """
    Membaca informasi user dari file JSON
    
    Args:
        username (str): Username TikTok (tanpa @)
    
    Returns:
        dict: Data user atau None jika file tidak ditemukan
    """
    data_dir = Path(__file__).parent.parent / "data" / "info"
    input_file = data_dir / f"{username}.info.json"
    
    if not input_file.exists():
        return None
    
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_user_stats(username):
    """
    Membaca statistik user dari file JSON
    
    Args:
        username (str): Username TikTok (tanpa @)
    
    Returns:
        dict: Data stats atau None jika file tidak ditemukan
    """
    data_dir = Path(__file__).parent.parent / "data" / "stats"
    input_file = data_dir / f"{username}.stats.json"
    
    if not input_file.exists():
        return None
    
    with open(input_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_user_data(username):
    """
    Membaca semua data user (info + stats)
    
    Args:
        username (str): Username TikTok (tanpa @)
    
    Returns:
        dict: Data lengkap user (gabungan info dan stats) atau None jika tidak ada
    """
    info_data = load_user_info(username)
    stats_data = load_user_stats(username)
    
    if info_data is None and stats_data is None:
        return None
    
    # Gabungkan data
    combined_data = {}
    if info_data:
        combined_data.update(info_data)
    if stats_data:
        combined_data.update(stats_data)
    
    return combined_data
