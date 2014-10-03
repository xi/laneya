OPEN = 0
RESOLVED = 1
REJECTED = 2


class AlreadyDoneError(Exception):
    pass


class Deferred(object):
    def __init__(self):
        self.promise = Promise()

    def resolve(self, value, status=RESOLVED):
        if self.promise._status == OPEN:
            self.promise._status = status
            self.promise._value = value
            for d, callback, errback in self.promise._children:
                if status == RESOLVED:
                    callback(value).then(d.resolve, d.reject)
                elif status == REJECTED:
                    errback(value).then(d.resolve, d.reject)
        else:
            raise AlreadyDoneError

    def reject(self, value):
        return self.resolve(value, status=REJECTED)


class Promise(object):
    def __init__(self):
        self._children = []
        self._status = OPEN
        self._value = None

    def then(self, callback, errback=None):
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
                try:
                    d.resolve(data['results'])
                except AlreadyDoneError:
                    pass
        return success

    for i, promise in enumerate(promises):
        promise.then(success_factory(i), d.reject)

    return d.promise


if __name__ == '__main__':
    def expect_factory(expected):
        def expect(actual):
            if actual == expected:
                print(actual)
            else:
                print("%s != %s" % (actual, expected))
        return expect

    def fail(error):
        raise Exception('fail')

    d = Deferred()
    d.resolve('huhu1')
    d.promise.then(expect_factory('huhu1'), fail)

    d = Deferred()
    d.promise.then(expect_factory('huhu2'), fail)
    d.resolve('huhu2')

    d = Deferred()
    d.reject('huhu3')
    d.promise.then(fail, expect_factory('huhu3'))

    d = Deferred()
    d.promise.then(fail, expect_factory('huhu4'))
    d.reject('huhu4')

    d = Deferred()
    d.reject('huhu5')
    d.promise.then(fail).then(fail, expect_factory('huhu5'))

    d = Deferred()
    d.reject('huhu6')
    d.promise.then(fail, when).then(expect_factory('huhu6'), fail)

    when('huhu7').then(expect_factory('huhu7'), fail)

    when(when('huhu8')).then(expect_factory('huhu8'), fail)

    reject('huhu9').then(fail, expect_factory('huhu9'))

    when(reject('huhu10')).then(fail, expect_factory('huhu10'))
