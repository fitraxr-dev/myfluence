"""
Test script untuk menghitung metrics influencer
"""
import sys
from pathlib import Path

# Setup path agar bisa import dari src
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from services.influencer_metrics import (
    calculate_engagement_rate,
    calculate_avg_engagement_rate_per_post,
    get_influencer_metrics,
    get_all_influencers_metrics
)


def test_single_influencer(username):
    """
    Test metrics untuk satu influencer
    """
    print(f"\n{'='*60}")
    print(f"📊 Metrics for @{username}")
    print(f"{'='*60}\n")
    
    metrics = get_influencer_metrics(username)
    
    if metrics:
        print(f"Username: @{metrics['username']}")
        print(f"Nickname: {metrics['nickname']}")
        print(f"Followers: {metrics['followers_count']:,}")
        print(f"Total Likes: {metrics['total_likes']:,}")
        print(f"Total Videos Analyzed: {metrics['total_videos']}")
        print(f"\n📈 Engagement Metrics:")
        print(f"  - Overall Engagement Rate: {metrics['engagement_rate']}%")
        print(f"  - Avg Engagement per Post: {metrics['avg_engagement_per_post']}%")
        
        print(f"\n📹 Video Performance:")
        for idx, video in enumerate(metrics['videos'], 1):
            stats = video['stats']
            views = stats['viewCount']
            engagement = stats['likeCount'] + stats['commentCount'] + stats['shareCount']
            video_er = (engagement / views * 100) if views > 0 else 0
            
            print(f"\n  Video {idx} (ID: {video['videoId']}):")
            print(f"    Views: {views:,}")
            print(f"    Likes: {stats['likeCount']:,}")
            print(f"    Comments: {stats['commentCount']:,}")
            print(f"    Shares: {stats['shareCount']:,}")
            print(f"    Engagement Rate: {video_er:.2f}%")
    else:
        print(f"❌ Data not found for @{username}")
    
    print(f"\n{'='*60}\n")
    return metrics


def test_all_influencers():
    """
    Test metrics untuk semua influencer
    """
    usernames = [
        "dillaprb",
        "kevindikmanto",
        "tasyafarasya",
        "tasyiiathasyia",
        "maharajasp8",
        "doctor.incognito_99",
        "fadiljaidi"
    ]
    
    print(f"\n{'='*60}")
    print(f"📊 All Influencers Metrics Summary")
    print(f"{'='*60}\n")
    
    all_metrics = get_all_influencers_metrics(usernames)
    
    if all_metrics:
        # Sort by engagement rate
        sorted_metrics = sorted(all_metrics, key=lambda x: x['engagement_rate'], reverse=True)
        
        print(f"{'Rank':<6} {'Username':<20} {'Followers':<12} {'ER %':<10} {'Avg ER/Post %':<15}")
        print("-" * 65)
        
        for idx, metrics in enumerate(sorted_metrics, 1):
            print(f"{idx:<6} @{metrics['username']:<19} {metrics['followers_count']:<12,} "
                  f"{metrics['engagement_rate']:<10} {metrics['avg_engagement_per_post']:<15}")
        
        print(f"\n{'='*60}")
        print(f"Total influencers analyzed: {len(all_metrics)}")
        print(f"Average engagement rate: {sum(m['engagement_rate'] for m in all_metrics) / len(all_metrics):.2f}%")
        print(f"{'='*60}\n")
    else:
        print("❌ No metrics data found")


def main():
    """
    Main test function
    """
    # Test untuk satu influencer
    test_single_influencer("dillaprb")
    
    # Test untuk semua influencer
    test_all_influencers()


if __name__ == "__main__":
    main()
