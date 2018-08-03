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


class Promise(object):
    def __init__(self):
        self._children = []
        self._status = OPEN
        self._value = None

    def resolve(self, value):
        if self._status == OPEN:
            self._status = RESOLVED
            self._value = value
            for d, callback, errback in self._children:
                callback(value).then(d.resolve, d.reject)

    def reject(self, value, silent=False):
        if self._status == OPEN:
            self._status = REJECTED
            self._value = value
            for d, callback, errback in self._children:
                errback(value).then(d.resolve, d.reject)

    def then(self, callback, errback=None):
        _callback = wrap(callback, default=when)
        _errback = wrap(errback, default=reject)

        if self._status == RESOLVED:
            return _callback(self._value)
        elif self._status == REJECTED:
            return _errback(self._value)
        else:  # OPEN
            promise = Promise()
            self._children.append((promise, _callback, _errback))
            return promise

    def catch(self, errback):
        return self.then(None, errback)


def when(value=None):
    if isinstance(value, Promise):
        return value
    else:
        promise = Promise()
        promise.resolve(value)
        return promise


def reject(value=None):
    if isinstance(value, Promise):
        return value
    else:
        promise = Promise()
        promise.reject(value)
        return promise


def wrap(fn, default=None):
    def wrapped(*args, **kwargs):
        try:
            value = fn(*args, **kwargs)
        except Exception as err:
            return reject(err)
        return when(value)

    if fn is None:
        return default
    else:
        return wrapped


def all(promises):
    result = Promise()
    data = {
        'count': len(promises),
        'results': [None] * len(promises),
    }

    def success_factory(i):
        def success(value):
            data['results'][i] = value
            data['count'] -= 1

            if data['count'] == 0:
                result.resolve(data['results'])

        return success

    for i, promise in enumerate(promises):
        promise.then(success_factory(i), result.reject)

    return result
