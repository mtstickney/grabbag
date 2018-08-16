from django.urls import path

from .settings import *

ROOT_URLCONF = 'grabbag.unit_tests.urls'

# These are unit tests, so use a unit-testing runner.
TEST_RUNNER = 'grabbag.unit_test_runner.UnitTestDiscoverRunner'
