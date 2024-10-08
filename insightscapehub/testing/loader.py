import unittest
from pathlib import Path
from setuptools import find_packages
from insightscapehub.utils.enums import AppsEnum
from insightscapehub.testing.helpers import drop_test_db, prepare_run_tests


class CustomTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, test):
        # Actions to perform before running tests
        prepare_run_tests()
        # Perform your custom actions here

        # Run the tests
        result = super().run(test)

        # Actions to perform after running tests
        # Perform your custom actions here

        drop_test_db()

        return result


def load_tests():
    from insightscapehub.utils import settings

    current_dir = settings.APP_HOME

    packages = set([(package.split(".")[0])
                   for package in find_packages(current_dir)])

    test_suite = unittest.TestSuite([])

    for package in packages:
        tests = unittest.defaultTestLoader.discover(
            package, top_level_dir=current_dir)
        test_suite.addTests(tests)
    # Create and run the custom test runner
    runner = CustomTestRunner()
    runner.run(test_suite)


def setup(app_name: AppsEnum, app_home: Path):
    from insightscapehub import envs

    envs.load_env_files(app_home)

    from insightscapehub.utils import settings

    settings.APP_HOME = app_home
    settings.APP_NAME = app_name

    load_tests()
