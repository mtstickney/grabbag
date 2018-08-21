from django.urls import path

from grabbag.settings import *

ROOT_URLCONF = 'link_save.unit_tests.urls'

# These are unit tests, so use a unit-testing runner.
TEST_RUNNER = 'link_save.unit_test_runner.UnitTestDiscoverRunner'

LINKSAVE_MASTER_API_TOKEN = 'ghjiklmnabcdef'
