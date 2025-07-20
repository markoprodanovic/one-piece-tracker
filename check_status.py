#!/usr/bin/env python3
"""
Status check script for monitoring.
Shows database state and recent activity.
"""

import asyncio
from datetime import datetime
from src.database import EpisodeDatabase
from src.main import get_health_status


async def main():
    print("One Piece Episode Tracker - Status Check")
    print("=" * 50)

    try:
        print("🔍 System Health Check...")
        health = await get_health_status()

        if health['overall_healthy']:
            print("✅ System Status: HEALTHY")
        else:
            print("❌ System Status: UNHEALTHY")
            print(f"   API: {'✅' if health['api_healthy'] else '❌'}")
            print(f"   Database: {'✅' if health['database_healthy'] else '❌'}")
            return False

        print("\n📊 Database Statistics...")
        with EpisodeDatabase() as db:
            stats = db.get_database_stats()

            print(f"   Total Episodes: {stats['total_episodes']}")
            print(f"   Episode Range: {stats['earliest_episode']} to {stats['latest_episode']}")
            print(f"   Latest Release: {stats['latest_release_date']}")
            print(f"   Unique Sagas: {stats['unique_sagas']}")
            print(f"   Unique Arcs: {stats['unique_arcs']}")

        print("\n🆕 Recent Episodes...")
        with EpisodeDatabase() as db:
            client = db._ensure_connected()
            recent = client.table(db.table_name).select(
                "id, title, release_date").order("id", desc=True).limit(3).execute()

            for episode in recent.data:
                print(f"   Episode {episode['id']}: {episode['title'][:50]}...")

        print(f"\n✅ Status check completed at {datetime.utcnow().isoformat()}Z")
        return True

    except Exception as e:
        print(f"\n❌ Status check failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
