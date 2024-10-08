import glob
from pathlib import Path

env_order = (".env")

# Sort the files based on the specified order
pattern = ".env*"


def load_env_files(path: Path):
    env_files = glob.glob(pattern, root_dir=path, recursive=True)

    sorted_env_files = sorted(
        env_files, key=lambda x: env_order.index(x) if x in env_order else 0
    )

    try:
        from dotenv import load_dotenv

        for env in sorted_env_files:
            load_dotenv(path.joinpath(env))

    except Exception as e:
        print("INFO:", "[insight_scape.env]", str(e))
