try:
    import unittest2 as unittest  # flake8: noqa
except ImportError:
    import unittest  # flake8: noqa


class SpyMixin:
    def __init__(self):
        self._spy_calls = {}
        self._key = 0

    def create_spy(self):
        key = self._key
        self._key += 1

        def spy(*args, **kwargs):
            if not key in self._spy_calls:
                self._spy_calls[key] = []
            self._spy_calls[key].append((args, kwargs))

        spy.key = key
        return spy

    def assertCalled(self, spy):
        self.assertIn(spy.key, self._spy_calls)

    def assertCalledWith(self, spy, *args, **kwargs):
        self.assertCalled(spy)
        self.assertIn((args, kwargs), self._spy_calls[spy.key])
