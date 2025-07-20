"""
Data models for the One Piece episode tracker.

These Pydantic models define the structure of data we receive from the API
and what we store in our database. They provide type safety and automatic
validation of the data.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Saga(BaseModel):
    """
    Represents a One Piece saga.

    A saga is a large story arc that contains multiple smaller arcs.
    """
    id: int
    title: str
    saga_number: str
    saga_chapitre: str  # Chapter range (keeping original French field name)
    saga_volume: str    # Volume range
    saga_episode: str   # Episode range


class Arc(BaseModel):
    """
    Represents a One Piece story arc.

    An arc is a story segment within a saga.
    """
    id: int
    title: str
    description: str
    saga: Saga  # Nested saga information


class EpisodeFromAPI(BaseModel):
    """
    Represents an episode as received from the One Piece API.

    This model matches the exact structure returned by the API,
    including all nested objects and optional fields.
    Arc and saga are optional to handle incomplete API data.
    """
    id: int
    title: str
    description: str
    number: str = Field(description="Episode number in format 'n°X'")
    chapter: str = Field(description="Chapter reference in format 'Chap X'")
    release_date: str = Field(description="Release date in YYYY-MM-DD format")
    arc: Optional[Arc] = None  # Made optional to handle missing data
    saga: Optional[Saga] = None  # Made optional to handle missing data

    @field_validator('release_date')
    @classmethod
    def validate_release_date(cls, v):
        """
        Validate that release_date is in the correct format.

        The API returns dates as strings in YYYY-MM-DD format.
        We validate the format but keep it as a string for now.
        """
        if not v:
            raise ValueError('Release date cannot be empty')

        # Try to parse the date to validate format
        try:
            from datetime import datetime
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError(f'Release date must be in YYYY-MM-DD format, got: {v}')

        return v


class EpisodeForDB(BaseModel):
    """
    Represents an episode as we want to store it in our database.

    This is a simplified version containing only the fields we care about:
    - id, title, release_date, arc_title, saga_title
    """
    id: int
    title: str
    release_date: date  # Converted to actual date object
    arc_title: str
    saga_title: str

    @classmethod
    def from_api_episode(cls, api_episode: EpisodeFromAPI) -> 'EpisodeForDB':
        """
        Convert an API episode to a database episode.

        This class method takes an EpisodeFromAPI object and extracts
        only the fields we want to store in our database. Uses placeholder
        values for missing arc/saga data.

        Args:
            api_episode: Episode data from the API

        Returns:
            EpisodeForDB: Simplified episode for database storage
        """
        from datetime import datetime

        # Convert string date to date object
        release_date_obj = datetime.strptime(api_episode.release_date, '%Y-%m-%d').date()

        # Handle missing arc/saga data with placeholders
        arc_title = api_episode.arc.title if api_episode.arc else "Unknown Arc"
        saga_title = api_episode.saga.title if api_episode.saga else "Unknown Saga"

        return cls(
            id=api_episode.id,
            title=api_episode.title,
            release_date=release_date_obj,
            arc_title=arc_title,
            saga_title=saga_title
        )

    def to_dict(self) -> dict:
        """
        Convert the episode to a dictionary for database insertion.

        Supabase expects dictionaries when inserting data.
        We convert the date to ISO format string for JSON serialization.

        Returns:
            dict: Episode data ready for database insertion
        """
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date.isoformat(),
            'arc_title': self.arc_title,
            'saga_title': self.saga_title
        }


class EpisodeFromDB(BaseModel):
    """
    Represents an episode as retrieved from our database.

    This includes the database-specific fields like created_at and updated_at
    that we added in our table schema.
    """
    id: int
    title: str
    release_date: date
    arc_title: str
    saga_title: str
    created_at: Optional[str] = None  # Database timestamp
    updated_at: Optional[str] = None  # Database timestamp

    @field_validator('release_date', mode='before')
    @classmethod
    def parse_release_date(cls, v):
        """
        Parse release_date from database.

        The database might return this as a string, so we convert it to a date object.
        """
        if isinstance(v, str):
            from datetime import datetime
            return datetime.fromisoformat(v.replace('Z', '+00:00')).date()
        return v


# Type aliases for clarity
APIEpisodeList = list[EpisodeFromAPI]
DBEpisodeList = list[EpisodeForDB]
