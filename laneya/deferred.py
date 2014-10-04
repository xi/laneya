"""Promise/deferred implementation inspired by `Kris Kowal's Q`_.

If a function cannot return a value or throw an exception without blocking, it
can return a *promise* instead. A promise is an object that represents the
return value or the thrown exception that the function may eventually provide.

The async function will keep a *deferred* object that is connected to the
returned promise.  The deferred can be *resolved* or *rejected* any time in
which case all registered callbacks on the promise will be executed.

A deferred can only be resolved or rejected a single time. Any callbacks
registered after that will be executed immediately.


.. _Kris Kowal's Q: https://github.com/kriskowal/q

"""


OPEN = 0
RESOLVED = 1
REJECTED = 2


class AlreadyDoneError(Exception):
    """The deferred has already been resolved or rejected."""


class Deferred(object):
    def __init__(self):
        self.promise = Promise()

    def resolve(self, value, status=RESOLVED):
        """Resolve the deferred.

        All success callbacks that are registered on the promise will be
        executed with ``value``.

        All success callbacks that will be registered on the promise will be
        executed immediately.

        Throws :py:exc:`AlreadyDoneError` if already resolved/rejected.

        """
        if self.promise._status == OPEN:
            self.promise._status = status
            self.promise._value = value
            for d, callback, errback in self.promise._children:
                if status == RESOLVED:
                    callback(value).then(d.resolve, d.reject)
                else:  # rejected
                    errback(value).then(d.resolve, d.reject)
        else:
            raise AlreadyDoneError

    def reject(self, value):
        """Reject the deferred.

        Works execatly like :py:meth:`resolve`, only that it triggers the
        execution of error callbacks.

        """
        return self.resolve(value, status=REJECTED)


class Promise(object):
    def __init__(self):
        self._children = []
        self._status = OPEN
        self._value = None

    def then(self, callback, errback=None):
        """Register callbacks.

        The registered callbacks will be executes as soon as the associated
        deferred has either been resolved or rejected.  If it already has been,
        the corresponding callback is executed immediately.

        :py:meth:`then` always returns a promise which will be resolved with
        the result of the callback.  If the callback raises an exception, the
        promise is rejected.

        """
        _callback = wrap(callback, default=when)
        _errback = wrap(errback, default=reject)

        if self._status == RESOLVED:
            return _callback(self._value)
        elif self._status == REJECTED:
            return _errback(self._value)
        else:  # OPEN
            d = Deferred()
            self._children.append((d, _callback, _errback))
            return d.promise

    def _raise(self):
        if self._status == REJECTED and isinstance(self._value, Exception):
            raise self._value


def when(value=None):
    """Wrap value in a promise if it is not already one."""
    if isinstance(value, Promise):
        return value
    else:
        d = Deferred()
        d.resolve(value)
        return d.promise


def reject(value=None):
    """Shortcut for creating a rejecting promise."""
    d = Deferred()
    d.reject(value)
    return d.promise


def wrap(fun, default=None):
    """Wrap a function so that it always returns a promise."""
    def _fun(*args, **kwargs):
        try:
            result = fun(*args, **kwargs)
        except Exception as err:
            return reject(err)
        return when(result)

    if fun is None:
        return default
    else:
        return _fun


def all(*promises):
    """Convert a list of promises to a promise of a list."""
    d = Deferred()
    data = {
        'count': len(promises),
        'results': [None] * len(promises),
    }

    def success_factory(i):
        def success(value):
            data['results'][i] = value
            data['count'] -= 1

            if data['count'] == 0:
                d.resolve(data['results'])
        return success

    for i, promise in enumerate(promises):
        promise.then(success_factory(i), d.reject)

    return d.promise
