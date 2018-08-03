import unittest

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from laneya import promise as q


class TestPromise(unittest.TestCase):
    def assert_never_called(self, *args, **kwargs):
        assert False

    def raise_rejected(self, promise):
        if (promise._status == q.REJECTED and
                isinstance(promise._value, Exception)):
            raise promise._value

    def test_promise_resolve(self):
        mock = Mock()

        promise = q.Promise()
        promise.resolve('foo')
        promise.then(mock, self.assert_never_called)

        mock.assert_called_with('foo')

    def test_promise_resolve_inverted(self):
        mock = Mock()

        promise = q.Promise()
        promise.then(mock, self.assert_never_called)
        promise.resolve('foo')

        mock.assert_called_with('foo')

    def test_promise_resolve_twice(self):
        mock = Mock()

        promise = q.Promise()
        promise.resolve('foo')
        promise.resolve('bar')
        promise.then(mock, self.assert_never_called)

        mock.assert_called_with('foo')

    def test_promise_reject(self):
        mock = Mock()

        promise = q.Promise()
        promise.reject('foo')
        promise.then(self.assert_never_called, mock)

        mock.assert_called_with('foo')

    def test_promise_reject_inverted(self):
        mock = Mock()

        promise = q.Promise()
        promise.then(self.assert_never_called, mock)
        promise.reject('foo')

        mock.assert_called_with('foo')

    def test_promise_reject_twice(self):
        mock = Mock()

        promise = q.Promise()
        promise.reject('foo')
        promise.reject('bar')
        promise.then(self.assert_never_called, mock)

        mock.assert_called_with('foo')

    def test_success_propagation(self):
        mock = Mock()

        promise = q.Promise()
        promise.resolve('foo')
        promise\
            .then(None, self.assert_never_called)\
            .then(mock, self.assert_never_called)

        mock.assert_called_with('foo')

    def test_error_propagation(self):
        mock = Mock()

        promise = q.Promise()
        promise.reject('foo')
        promise\
            .then(self.assert_never_called)\
            .catch(mock)

        mock.assert_called_with('foo')

    def test_success_chaining(self):
        mock = Mock()

        def fn(x):
            return x + 'bar'

        promise = q.Promise()
        promise.resolve('foo')
        promise\
            .then(fn, self.assert_never_called)\
            .then(mock, self.assert_never_called)

        mock.assert_called_with('foobar')

    def test_error_chaining(self):
        mock = Mock()

        def fn(x):
            return x + 'bar'

        promise = q.Promise()
        promise.reject('foo')
        promise\
            .then(self.assert_never_called, fn)\
            .then(mock, self.assert_never_called)

        mock.assert_called_with('foobar')

    def test_when_with_value(self):
        mock = Mock()

        promise = q.when('foo')
        promise.then(mock, self.assert_never_called)

        mock.assert_called_with('foo')

    def test_when_with_promise(self):
        p1 = q.Promise()
        p2 = q.when(p1)

        self.assertEqual(p1, p2)

    def test_reject_with_value(self):
        mock = Mock()

        promise = q.reject('foo')
        promise.then(self.assert_never_called, mock)

        mock.assert_called_with('foo')

    def test_reject_with_promise(self):
        p1 = q.Promise()
        p2 = q.reject(p1)

        self.assertEqual(p1, p2)

    def test_wrap_return(self):
        mock = Mock()

        @q.wrap
        def fn(x):
            return 'foo'

        promise = fn('bar')
        promise.then(mock, self.assert_never_called)

        mock.assert_called_with('foo')

    def test_wrap_raise(self):
        mock = Mock()
        err = Exception('foo')

        @q.wrap
        def fn(x):
            raise err

        promise = fn('bar')
        promise.then(self.assert_never_called, mock)

        mock.assert_called_with(err)

    def test_all_success(self):
        mock = Mock()

        p1 = q.Promise()
        p2 = q.Promise()
        p3 = q.Promise()

        p1.resolve('foo')
        p3.resolve('baz')
        p2.resolve('bar')

        q.all([p1, p2, p3]).then(mock, self.assert_never_called)

        mock.assert_called_with(['foo', 'bar', 'baz'])

    def test_all_error(self):
        mock = Mock()

        p1 = q.Promise()
        p2 = q.Promise()
        p3 = q.Promise()

        p2.resolve('bar')
        p3.reject('baz')

        q.all([p1, p2, p3]).then(self.assert_never_called, mock)

        mock.assert_called_with('baz')
