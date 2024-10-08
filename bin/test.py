from pathlib import Path
from insightscapehub.utils.enums import AppsEnum
from insightscapehub.testing.loader import setup

here = Path(__file__).parent.parent


setup(AppsEnum.BASE, here)
