from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

import asyncio
from sqlalchemy.ext.asyncio import async_engine_from_config
from app.core.config import get_settings
settings = get_settings()

from alembic import context

from app.core.database import Base
import app.models.expense  # noqa — ensures ExpenseDB is registered

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def run_migrations_online():
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.DATABASE_URL
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
    )

    async def do_run_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(
                lambda conn: context.configure(
                    connection=conn,
                    target_metadata=target_metadata
                )
            )
            async with connection.begin():
                await connection.run_sync(
                    lambda conn: context.run_migrations()
                )

    asyncio.run(do_run_migrations())


if context.is_offline_mode():
    run_migrations_online()
else:
    run_migrations_online()