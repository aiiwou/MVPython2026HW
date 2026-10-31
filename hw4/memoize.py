from functools import wraps
from time import perf_counter

def memoize(func):
    """Кэширует результаты вызовов функции с хешируемыми аргументами."""
    cache = {}
    hits = 0
    misses = 0

    @wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal hits, misses

        try:
            key = (args, frozenset(kwargs.items()))
            hash(key)
        except TypeError:
            return func(*args, **kwargs)

        if key in cache:
            hits += 1
            wrapper.hits = hits
            return cache[key]

        misses += 1
        wrapper.misses = misses

        result = func(*args, **kwargs)
        cache[key] = result
        return result

    def cache_clear():
        nonlocal hits, misses

        cache.clear()
        hits = 0
        misses = 0
        wrapper.hits = 0
        wrapper.misses = 0

    wrapper.hits = 0
    wrapper.misses = 0
    wrapper.cache_clear = cache_clear

    return wrapper

def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

def experiment():
    global fib

    original_fib = fib

    fast_fib = memoize(original_fib)
    start = perf_counter()
    result_a = fast_fib(30)
    time_a = perf_counter() - start

    print('Вариант A - кэшируем только внешний вызов:')
    print('Результат:', result_a)
    print('Misses:', fast_fib.misses)
    print('Время:', time_a)

    fib = memoize(original_fib)
    start = perf_counter()
    result_b = fib(30)
    time_b = perf_counter() - start

    print('Вариант B - рекурсивные выховы тоже идут через кэш:')
    print('Результат:', result_b)
    print('Misses:', fib.misses)
    print('Время:', time_b)


if __name__ == '__main__':
    calls = []

    def slow_square(x, power=2):
        '''Возводит в степень.'''
        calls.append(x)
        return x ** power

    sq = memoize(slow_square)

    assert sq(3) == 9
    assert sq(3) == 9
    assert sq(3, power=3) == 27
    assert calls == [3, 3]
    assert (sq.hits, sq.misses) == (1, 2)
    assert sq.__name__ == 'slow_square'
    assert sq.__doc__ == 'Возводит в степень.'

    total = memoize(sum)
    assert total([1, 2, 3]) == 6
    assert total([1, 2, 3]) == 6
    assert (total.hits, total.misses) == (0, 0)

    sq.cache_clear()
    assert (sq.hits, sq.misses) == (0, 0)
    sq(3)
    assert calls[-1] == 3

    print('Все проверки пройдены!')

    print('Эксперимент с рекурсией!')
    experiment()

'''
В варианте A имя fast_fib указывает на обёртку, но глобальное имя fib
остаётся исходной функцией. Поэтому рекурсивные вызовы fib внутри
функции обходят кэш, и ускорение почти отсутствует.
В варианте B имя fib переназначается на обёртку. При рекурсивном
вызове имя fib ищется по LEGB во время выполнения функции, и в
глобальной области уже находится обёртка. Поэтому рекурсивные вызовы
тоже кэшируются, а каждое значение вычисляется только один раз.
'''