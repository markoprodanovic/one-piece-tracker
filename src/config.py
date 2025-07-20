import os
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

load_dotenv()


class AppConfig(BaseModel):

    supabase_url: str = Field(description="Supabase project URL")
    supabase_key: str = Field(description="Supabase anon/public key")

    one_piece_api_base_url: str = Field(
        default="https://api.api-onepiece.com/v2",
        description="Base URL for the One Piece API"
    )

    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    @field_validator('supabase_url')
    @classmethod
    def validate_supabase_url(cls, v):
        if not v.startswith('https://') or '.supabase.co' not in v:
            raise ValueError(
                'Supabase URL must be a valid Supabase project URL')
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR'}
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}')
        return v.upper()

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


def get_config() -> AppConfig:

    supabase_url = os.getenv('SUPABASE_URL')
    if not supabase_url:
        raise ValueError("SUPABASE_URL environment variable is not set.")

    supabase_key = os.getenv('SUPABASE_KEY')
    if not supabase_key:
        raise ValueError("SUPABASE_KEY environment variable is not set.")

    try:
        return AppConfig(
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            one_piece_api_base_url=os.getenv(
                'ONE_PIECE_API_BASE_URL', 'https://api.api-onepiece.com/v2'),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
    except Exception as e:
        print(f"Configuration error: {e}")
        print('Please check your .env file is properly set up')
        raise


config = get_config()
