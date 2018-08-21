from django.test.runner import DiscoverRunner

# If it touches the database, it's not a /unit/ test, so provider a
# running that skips those bits.
class UnitTestDiscoverRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, *args, **kwargs):
        pass
