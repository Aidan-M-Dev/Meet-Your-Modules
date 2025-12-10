"""
Configuration classes for different environments (development, production).

Usage:
    Set FLASK_ENV environment variable to 'development' or 'production'
    to automatically load the appropriate configuration.
"""

import os


class Config:
    """Base configuration with common settings."""

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')

    # Database Connection Pool
    DB_POOL_MIN = int(os.getenv('DB_POOL_MIN', 2))
    DB_POOL_MAX = int(os.getenv('DB_POOL_MAX', 10))

    # Frontend/Backend
    FRONTEND_ADDRESS = os.getenv('FRONTEND_ADDRESS', 'localhost')
    FRONTEND_PORT = os.getenv('FRONTEND_PORT', '5173')
    BACKEND_ADDRESS = os.getenv('BACKEND_ADDRESS', 'localhost')
    BACKEND_PORT = int(os.getenv('BACKEND_PORT', 5000))

    # Google AI
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JSON_SORT_KEYS = False  # Preserve JSON key order


class DevelopmentConfig(Config):
    """Development environment configuration."""

    DEBUG = True
    TESTING = False

    # CORS - Allow localhost and common development addresses
    CORS_ORIGINS = [
        f"http://{Config.FRONTEND_ADDRESS}:{Config.FRONTEND_PORT}",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # Alternative frontend dev server
    ]

    # Logging - Verbose in development
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')

    # Database - Warn if using production DB
    @property
    def DATABASE_URL(self):
        db_url = os.getenv('DATABASE_URL')
        if db_url and 'production' in db_url.lower():
            import logging
            logger = logging.getLogger(__name__)
            logger.warning("⚠️  Using production database in development mode!")
        return db_url


class ProductionConfig(Config):
    """Production environment configuration."""

    DEBUG = False
    TESTING = False

    # CORS - Strict, only allow configured frontend
    CORS_ORIGINS = [
        f"http://{Config.FRONTEND_ADDRESS}:{Config.FRONTEND_PORT}",
    ]

    # Allow HTTPS origins in production
    if os.getenv('FRONTEND_HTTPS', 'false').lower() == 'true':
        CORS_ORIGINS.append(
            f"https://{Config.FRONTEND_ADDRESS}:{Config.FRONTEND_PORT}"
        )

    # Logging - Less verbose in production
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Security - Require secret key in production
    SECRET_KEY = os.getenv('SECRET_KEY')

    @classmethod
    def validate(cls):
        """Validate production configuration. Called when config is actually used."""
        if not cls.SECRET_KEY or cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            raise ValueError(
                "SECRET_KEY must be set in production! "
                "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )

        # Require Google API key in production
        if not cls.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY must be set in production!")


class TestingConfig(Config):
    """Testing environment configuration."""

    DEBUG = False
    TESTING = True

    # Use test database
    DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'postgresql://test:test@localhost:5432/test_db')

    # CORS - Allow all origins for testing
    CORS_ORIGINS = ['*']

    # Logging - Minimal in tests
    LOG_LEVEL = 'ERROR'

    # Don't require API keys in testing
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'test-key')


# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """
    Get configuration based on FLASK_ENV environment variable.

    Returns:
        Config class: DevelopmentConfig, ProductionConfig, or TestingConfig

    Defaults to DevelopmentConfig if FLASK_ENV is not set.
    """
    env = os.getenv('FLASK_ENV', 'development').lower()
    config = config_by_name.get(env, config_by_name['default'])

    # Validate production config when it's actually used
    if env == 'production' and hasattr(config, 'validate'):
        config.validate()

    return config
