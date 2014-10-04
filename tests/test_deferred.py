import shared
from shared import unittest

from laneya import deferred as q


class TestDeferred(unittest.TestCase, shared.SpyMixin):
    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        shared.SpyMixin.__init__(self)

    def assertNeverCalled(self, *args, **kwargs):
        assert False

    def test_deferred_resolve(self):
        spy = self.create_spy()

        d = q.Deferred()
        d.resolve('foo')
        d.promise.then(spy, self.assertNeverCalled)._raise()

        self.assertCalledWith(spy, 'foo')

    def test_deferred_resolve_inverted(self):
        spy = self.create_spy()

        d = q.Deferred()
        d.promise.then(spy, self.assertNeverCalled)._raise()
        d.resolve('foo')

        self.assertCalledWith(spy, 'foo')

    def test_deferred_resolve_done(self):
        spy = self.create_spy()

        d = q.Deferred()
        d.promise.then(spy, self.assertNeverCalled)._raise()
        d.resolve('foo')

        with self.assertRaises(q.AlreadyDoneError):
            d.resolve('bar')

        with self.assertRaises(q.AlreadyDoneError):
            d.reject('bar')

        self.assertCalledWith(spy, 'foo')

    def test_deferred_reject(self):
        spy = self.create_spy()

        d = q.Deferred()
        d.reject('foo')
        d.promise.then(self.assertNeverCalled, spy)._raise()

        self.assertCalledWith(spy, 'foo')

    def test_deferred_reject_inverted(self):
        spy = self.create_spy()

        d = q.Deferred()
        d.promise.then(self.assertNeverCalled, spy)._raise()
        d.reject('foo')

        self.assertCalledWith(spy, 'foo')

    def test_deferred_reject_done(self):
        spy = self.create_spy()

        d = q.Deferred()
        d.promise.then(self.assertNeverCalled, spy)._raise()
        d.reject('foo')

        with self.assertRaises(q.AlreadyDoneError):
            d.resolve('bar')

        with self.assertRaises(q.AlreadyDoneError):
            d.reject('bar')

        self.assertCalledWith(spy, 'foo')

    def test_success_propagation(self):
        spy = self.create_spy()

        d = q.Deferred()
        d.resolve('foo')
        d.promise\
            .then(None, self.assertNeverCalled)\
            .then(spy, self.assertNeverCalled)\
            ._raise()

        self.assertCalledWith(spy, 'foo')

    def test_error_propagation(self):
        spy = self.create_spy()

        d = q.Deferred()
        d.reject('foo')
        d.promise\
            .then(self.assertNeverCalled)\
            .then(self.assertNeverCalled, spy)\
            ._raise()

        self.assertCalledWith(spy, 'foo')

    def test_success_chaining(self):
        spy = self.create_spy()
        fn = lambda x: x + 'bar'

        d = q.Deferred()
        d.resolve('foo')
        d.promise\
            .then(fn, self.assertNeverCalled)\
            .then(spy, self.assertNeverCalled)\
            ._raise()

        self.assertCalledWith(spy, 'foobar')

    def test_error_chaining(self):
        spy = self.create_spy()
        fn = lambda x: x + 'bar'

        d = q.Deferred()
        d.reject('foo')
        d.promise\
            .then(self.assertNeverCalled, fn)\
            .then(spy, self.assertNeverCalled)\
            ._raise()

        self.assertCalledWith(spy, 'foobar')

    def test_when_with_value(self):
        spy = self.create_spy()

        p = q.when('foo')
        p.then(spy, self.assertNeverCalled)._raise()

        self.assertCalledWith(spy, 'foo')

    def test_when_with_promise(self):
        p1 = q.Promise()
        p2 = q.when(p1)

        self.assertEqual(p1, p2)

    def test_reject(self):
        spy = self.create_spy()

        p = q.reject('foo')
        p.then(self.assertNeverCalled, spy)._raise()

        self.assertCalledWith(spy, 'foo')

    def test_wrap_return(self):
        spy = self.create_spy()
        fn = lambda x: 'foo'

        p = q.wrap(fn)('bar')
        p.then(spy, self.assertNeverCalled)._raise()

        self.assertCalledWith(spy, 'foo')

    def test_wrap_raise(self):
        spy = self.create_spy()
        err = Exception('foo')

        def fn(x):
            raise err

        p = q.wrap(fn)('bar')
        p.then(self.assertNeverCalled, spy)._raise()

        self.assertCalledWith(spy, err)

    def test_raise(self):
        with self.assertRaises(AssertionError):
            q.when('foo').then(self.assertNeverCalled)._raise()

    def test_all_success(self):
        spy = self.create_spy()

        d1 = q.Deferred()
        d2 = q.Deferred()
        d3 = q.Deferred()

        d1.resolve('foo')
        d3.resolve('baz')
        d2.resolve('bar')

        q.all(d1.promise, d2.promise, d3.promise)\
            .then(spy, self.assertNeverCalled)\
            ._raise()

        self.assertCalledWith(spy, ['foo', 'bar', 'baz'])

    def test_all_error(self):
        spy = self.create_spy()

        d1 = q.Deferred()
        d2 = q.Deferred()
        d3 = q.Deferred()

        d2.resolve('bar')
        d3.reject('baz')

        q.all(d1.promise, d2.promise, d3.promise)\
            .then(self.assertNeverCalled, spy)\
            ._raise()

        self.assertCalledWith(spy, 'baz')
