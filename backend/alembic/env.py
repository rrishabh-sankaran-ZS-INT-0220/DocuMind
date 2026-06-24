import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ----------------------------------------------------------------------
# Ensure project root is on sys.path so `backend` is importable
# ----------------------------------------------------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))          # .../backend/alembic
backend_dir = os.path.dirname(current_dir)                        # .../backend
project_root = os.path.dirname(backend_dir)                       # .../DocuMind

if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.config import settings
from backend.app.db.base import Base
from backend.app.db.models import *  # noqa: F401,F403

config = context.config

# Use sync DB URL from settings (built from env vars)
config.set_main_option("sqlalchemy.url", settings.sync_db_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section)
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()