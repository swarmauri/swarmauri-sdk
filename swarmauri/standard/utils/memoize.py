def memoize(func):
    cache = {}
    def memoized_func(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return memoized_func
    
class MemoizingMeta(type):
    def __new__(cls, name, bases, dct):
        for key, value in dct.items():
            if callable(value) and not key.startswith('__'):
                dct[key] = memoize(value)
        return super().__new__(cls, name, bases, dct)
