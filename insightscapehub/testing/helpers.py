import os

import psycopg2
import psycopg2.sql

import alembic.command
import alembic.config
from insightscapehub.utils import db as _db
from insightscapehub.utils import settings


def is_running_in_docker():
    return bool(
        os.environ.get("DOCKER_CONTAINER_ID") or os.environ.get(
            "DOCKER_CONTAINER_NAME")
    )


def configure(testing=True):
    if settings.IS_TESTING and testing:
        return

    settings.IS_TESTING = testing == True
    settings.DB_NAME = "test_" + settings.DB_NAME if testing else settings.DB_NAME
    settings.DB_URL = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

    # UPDATE SESSION DETAILS
    _db.SQLALCHEMY_DATABASE_URL = settings.DB_URL
    _db.engine = _db.create_engine(settings.DB_URL)
    _db.SessionLocal = _db.sessionmaker(
        bind=_db.engine, autocommit=False, autoflush=False
    )


def get_raw_conn():
    conn = psycopg2.connect(
        user=settings.DB_USER,
        host=settings.DB_HOST,
        password=settings.DB_PASSWORD,
        port=settings.DB_PORT,
    )
    conn.autocommit = True

    return conn


# CREATE TEST DB
def create_test_db():
    print("Creating test database...")
    conn = get_raw_conn()
    cursor = conn.cursor()
    dbname = psycopg2.sql.Identifier(settings.DB_NAME)
    drop_cmd = psycopg2.sql.SQL("DROP DATABASE  IF EXISTS {}").format(dbname)
    create_cmd = psycopg2.sql.SQL("CREATE DATABASE {}").format(dbname)

    cursor.execute(drop_cmd)
    cursor.execute(create_cmd)
    cursor.close()
    conn.close()


def drop_test_db():
    try:
        print("Destroying test database...")
        conn = get_raw_conn()
        cursor = conn.cursor()

        dbname = psycopg2.sql.Identifier(settings.DB_NAME)

        drop_cmd = psycopg2.sql.SQL("DROP DATABASE  IF EXISTS {} WITH (FORCE)").format(
            dbname
        )
        cursor.execute(drop_cmd)
        cursor.close()
        conn.close()
    except Exception as e:
        print(e, "Failed to destroy db. OK", sep="\n")
    finally:
        pass


def prepare_run_tests():
    configure()
    create_test_db()
    cfg_path = settings.APP_HOME / "alembic.ini"
    print("CFG", cfg_path)

    alembic_cfg = alembic.config.Config(cfg_path)

    alembic_cfg.set_main_option("sqlalchemy.url", settings.DB_URL)

    try:
        alembic.command.revision(alembic_cfg, autogenerate=True)
        alembic.command.upgrade(alembic_cfg, "head")

    except Exception as e:
        print(e)
