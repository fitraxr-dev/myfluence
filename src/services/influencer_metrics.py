"""
Module untuk menghitung metrics influencer
"""
import json
from pathlib import Path
from typing import Dict, List, Optional


def calculate_engagement_rate(stats: Dict, videos: List[Dict]) -> float:
    """
    Menghitung engagement rate influencer secara keseluruhan
    
    Formula: (Total Engagement / Total Views) * 100
    Total Engagement = Total Likes + Total Comments + Total Shares dari semua video
    
    Args:
        stats (Dict): Data statistik user dengan key 'followers_count'
        videos (List[Dict]): List video dengan stats masing-masing
    
    Returns:
        float: Engagement rate dalam persentase (0-100)
    """
    if not videos:
        return 0.0
    
    total_views = 0
    total_engagement = 0
    
    for video in videos:
        video_stats = video.get('stats', {})
        views = video_stats.get('viewCount', 0)
        likes = video_stats.get('likeCount', 0)
        comments = video_stats.get('commentCount', 0)
        shares = video_stats.get('shareCount', 0)
        
        total_views += views
        total_engagement += (likes + comments + shares)
    
    # Hindari division by zero
    if total_views == 0:
        return 0.0
    
    engagement_rate = (total_engagement / total_views) * 100
    return round(engagement_rate, 2)


def calculate_avg_engagement_rate_per_post(videos: List[Dict]) -> float:
    """
    Menghitung rata-rata engagement rate per post
    
    Formula: Average((Likes + Comments + Shares) / Views * 100) untuk setiap video
    
    Args:
        videos (List[Dict]): List video dengan stats masing-masing
    
    Returns:
        float: Rata-rata engagement rate per post dalam persentase (0-100)
    """
    if not videos:
        return 0.0
    
    engagement_rates = []
    
    for video in videos:
        video_stats = video.get('stats', {})
        views = video_stats.get('viewCount', 0)
        likes = video_stats.get('likeCount', 0)
        comments = video_stats.get('commentCount', 0)
        shares = video_stats.get('shareCount', 0)
        
        # Skip video tanpa views
        if views == 0:
            continue
        
        engagement = likes + comments + shares
        video_engagement_rate = (engagement / views) * 100
        engagement_rates.append(video_engagement_rate)
    
    # Hindari division by zero
    if not engagement_rates:
        return 0.0
    
    avg_engagement_rate = sum(engagement_rates) / len(engagement_rates)
    return round(avg_engagement_rate, 2)


def get_influencer_metrics(username: str) -> Optional[Dict]:
    """
    Mengambil dan menghitung metrics lengkap untuk influencer
    
    Args:
        username (str): Username influencer
    
    Returns:
        Dict: Metrics influencer dengan struktur:
            - username: Username
            - nickname: Display name
            - followers_count: Jumlah followers
            - total_likes: Total likes
            - total_videos: Jumlah video yang dianalisis
            - engagement_rate: Overall engagement rate
            - avg_engagement_per_post: Rata-rata engagement per post
            - videos: Detail video dengan stats
    """
    # Path ke data files
    data_dir = Path(__file__).parent.parent / "data"
    stats_file = data_dir / "stats" / f"{username}.stats.json"
    info_file = data_dir / "info" / f"{username}.info.json"
    videos_file = data_dir / "videos" / f"{username}.video.json"
    
    # Cek apakah file ada
    if not stats_file.exists() or not videos_file.exists():
        return None
    
    try:
        # Load data stats
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats_data = json.load(f)
        
        # Load data info (untuk nickname)
        nickname = username
        if info_file.exists():
            with open(info_file, 'r', encoding='utf-8') as f:
                info_data = json.load(f)
                nickname = info_data.get('nickname', username)
        
        # Load data videos
        with open(videos_file, 'r', encoding='utf-8') as f:
            videos_data = json.load(f)
        
        videos = videos_data.get('videos', [])
        
        # Hitung metrics
        engagement_rate = calculate_engagement_rate(stats_data, videos)
        avg_engagement_per_post = calculate_avg_engagement_rate_per_post(videos)
        
        return {
            'username': username,
            'nickname': nickname,
            'followers_count': stats_data.get('followers_count', 0),
            'total_likes': stats_data.get('total_likes', 0),
            'total_videos': len(videos),
            'engagement_rate': engagement_rate,
            'avg_engagement_per_post': avg_engagement_per_post,
            'videos': videos
        }
        
    except Exception as e:
        print(f"Error loading data for {username}: {e}")
        return None


def get_all_influencers_metrics(usernames: List[str]) -> List[Dict]:
    """
    Mengambil metrics untuk semua influencer dalam list
    
    Args:
        usernames (List[str]): List username influencer
    
    Returns:
        List[Dict]: List metrics untuk setiap influencer
    """
    metrics_list = []
    
    for username in usernames:
        metrics = get_influencer_metrics(username)
        if metrics:
            metrics_list.append(metrics)
    
    return metrics_list
