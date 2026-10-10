import functools
import time


def memoize(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        try:
            hash(key)
        except TypeError:
            return func(*args, **kwargs)
        if key in cache:
            wrapper.hits += 1
            return cache[key]
        wrapper.misses += 1
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    def cache_clear():
        cache.clear()
        wrapper.hits = 0
        wrapper.misses = 0

    wrapper.hits = 0
    wrapper.misses = 0
    wrapper.cache_clear = cache_clear
    return wrapper


def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


if __name__ == '__main__':
    calls = []

    def slow_square(x, power=2):
        '''Возводит в степень.'''
        calls.append(x)
        return x ** power

    sq = memoize(slow_square)
    assert sq(3) == 9 and sq(3) == 9 and sq(3, power=3) == 27
    assert calls == [3, 3]
    assert (sq.hits, sq.misses) == (1, 2)
    assert sq.__name__ == 'slow_square' and sq.__doc__ == 'Возводит в степень.'
    total = memoize(sum)
    assert total([1, 2, 3]) == 6 and total([1, 2, 3]) == 6   # нехешируемый аргумент: вызов без кэша
    assert (total.hits, total.misses) == (0, 0)
    sq.cache_clear()
    assert (sq.hits, sq.misses) == (0, 0)
    sq(3)
    assert calls[-1] == 3

    def f(a, b=0):
        return a + b

    mf = memoize(f)
    assert mf(1, b=2) == 3 and mf(1, b=3) == 4
    assert mf(1, b=2) == 3
    assert (mf.hits, mf.misses) == (1, 2)
    assert mf(1, 2) == 3
    assert mf.misses == 3
    assert mf([1], b=[2]) == [1, 2]
    assert (mf.hits, mf.misses) == (1, 3)

    other = memoize(f)
    other(1)
    assert (other.hits, other.misses) == (0, 1) and mf.misses == 3

    fast_fib = memoize(fib)
    start = time.perf_counter()
    assert fast_fib(30) == 832040
    print(f'A: misses={fast_fib.misses}, {time.perf_counter() - start:.4f} сек')

    fib = memoize(fib)
    start = time.perf_counter()
    assert fib(30) == 832040
    print(f'B: misses={fib.misses}, {time.perf_counter() - start:.6f} сек')

# Вариант A почти не помогает: fast_fib(30) дает misses=1 и работает так же долго, как обычный fib.
# Внутри тела fib имя fib не локальное и не из объемлющей функции, поэтому по LEGB это глобальное имя,
# и его значение берется из глобальной области в момент каждого вызова. А там все еще лежит старая функция без кэша.
# Кэшируется только самый внешний вызов, все остальные идут мимо кэша.
# В варианте B мы переприсваиваем глобальное имя fib, поэтому когда тело функции ищет fib в глобальной
# области, оно находит уже обертку с кэшем. Каждое n считается один раз (misses=31), и вместо
# экспоненциального числа вызовов получается линейное, отсюда ускорение в тысячи раз.
