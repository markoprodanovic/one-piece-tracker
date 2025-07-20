# One Piece Episode Tracker

A Python application that automatically syncs One Piece episode data from a public API to a Supabase database.

## Features

- 🏴‍☠️ Fetches all One Piece episodes with metadata (title, release date, arc, saga)
- 🔄 Smart sync - only processes new episodes for efficient daily updates
- 📊 Handles missing data gracefully with placeholder values
- 🚀 Production ready with health checks and error handling

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Setup

Create a Supabase project and run this SQL:

```sql
CREATE TABLE episodes (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    release_date DATE,
    arc_title TEXT,
    saga_title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_episodes_release_date ON episodes(release_date);
```

### 3. Environment Variables

Copy `.env.example` to `.env` and fill in your Supabase credentials:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

## Usage

```bash
# Run the sync
python -m src.main

# Test everything works
python test_main.py
```

## How It Works

1. Fetches all episodes from the One Piece API (~1138 episodes)
2. Compares with existing database episodes
3. Inserts only new episodes using upsert logic
4. Generates sync statistics

**Sample output:**

```
Episodes fetched from API: 1138
New episodes found: 2
Episodes inserted: 2
Sync duration: 4.48 seconds
```

## Project Structure

```
src/
├── main.py           # Main application
├── config.py         # Configuration
├── models.py         # Data models
├── api_client.py     # API client
└── database.py       # Database operations
```
