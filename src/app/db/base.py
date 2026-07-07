"""
Registry module for database models.

This module is critical for Alembic migrations. By importing all models here,
Alembic's env.py can detect changes to the metadata and automatically generate
the necessary migration scripts.
"""

from src.app.db.session import Base

# Importing all models so they register with the Base.metadata
from src.app.models.user import User
from src.app.models.source import Source
from src.app.models.search_profile import SearchProfile
from src.app.models.job import Job
from src.app.models.job_match import JobMatch
from src.app.models.search_run import SearchRun
from src.app.models.schedule import Schedule
from src.app.models.notification import Notification
from src.app.models.user_preference import UserPreferences
