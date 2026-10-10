import time


class MyDict:
    def __init__(self, size=8):
        if size < 1:
            raise ValueError('size должен быть больше 0')
        self._buckets = [[] for _ in range(size)]
        self._len = 0
        self._order = []

    def _bucket(self, key):
        return self._buckets[hash(key) % len(self._buckets)]

    def _resize(self):
        old_buckets = self._buckets
        self._buckets = [[] for _ in range(len(old_buckets) * 2)]
        for bucket in old_buckets:
            for key, value in bucket:
                self._bucket(key).append((key, value))

    def __setitem__(self, key, value):
        bucket = self._bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (k, value)
                return
        bucket.append((key, value))
        self._order.append(key)
        self._len += 1
        if self._len > len(self._buckets) * 2 / 3:
            self._resize()

    def __getitem__(self, key):
        for k, v in self._bucket(key):
            if k == key:
                return v
        raise KeyError(key)

    def __delitem__(self, key):
        bucket = self._bucket(key)
        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._order.remove(k)
                self._len -= 1
                return
        raise KeyError(key)

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        return True

    def __len__(self):
        return self._len

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def stats(self):
        longest = max(len(bucket) for bucket in self._buckets)
        return len(self._buckets), self._len, longest

    def keys(self):
        return list(self._order)

    def values(self):
        return [self[key] for key in self._order]

    def items(self):
        return [(key, self[key]) for key in self._order]

    def __iter__(self):
        return iter(self.keys())

    def __repr__(self):
        pairs = ', '.join(f'{k!r}: {v!r}' for k, v in self.items())
        return f'MyDict({{{pairs}}})'


class BadKey:
    def __init__(self, value):
        self.value = value

    def __hash__(self):
        return 42

    def __eq__(self, other):
        return isinstance(other, BadKey) and self.value == other.value


if __name__ == '__main__':
    d = MyDict()
    for i in range(1000):
        d[f'key{i}'] = i
    assert len(d) == 1000
    assert d['key42'] == 42
    assert 'key7' in d and 'nope' not in d
    d['key42'] = -1
    assert d['key42'] == -1 and len(d) == 1000
    del d['key42']
    assert 'key42' not in d and len(d) == 999
    assert d.get('nope') is None and d.get('nope', 0) == 0
    for bad in (lambda: d['nope'], lambda: d.__delitem__('nope')):
        try:
            bad()
            assert False, 'ожидали KeyError'
        except KeyError:
            pass
    buckets, size, longest = d.stats()
    assert size == 999 and size <= buckets * 2 / 3
    print(d.stats())

    empty = MyDict()
    assert len(empty) == 0 and repr(empty) == 'MyDict({})'
    assert empty.stats() == (8, 0, 0)

    try:
        MyDict(0)
        assert False, 'ожидали ValueError'
    except ValueError:
        pass

    small = MyDict()
    small['a'] = 1
    small['b'] = 2
    assert repr(small) == "MyDict({'a': 1, 'b': 2})"
    small[None] = 'none'
    small[(1, 2)] = 'tuple'
    assert small[None] == 'none' and small[(1, 2)] == 'tuple'
    try:
        small[[1, 2]] = 'list'
        assert False, 'ожидали TypeError'
    except TypeError:
        pass

    ordered = MyDict(size=2)
    for i in range(20):
        ordered[i] = i * 10
    del ordered[5]
    ordered[5] = 'new'
    ordered[0] = 'zero'
    assert ordered.keys() == [i for i in range(20) if i != 5] + [5]
    assert ordered.values()[0] == 'zero'
    assert ordered.items()[-1] == (5, 'new')
    assert list(ordered) == ordered.keys()

    start = time.perf_counter()
    normal = MyDict()
    for i in range(1000):
        normal[f'key{i}'] = i
    normal_time = time.perf_counter() - start

    start = time.perf_counter()
    bad = MyDict()
    for i in range(1000):
        bad[BadKey(i)] = i
    bad_time = time.perf_counter() - start

    assert bad[BadKey(500)] == 500
    print('строковые ключи:', normal.stats(), f'{normal_time:.4f} сек')
    print('hash всегда 42:', bad.stats(), f'{bad_time:.4f} сек')

# 1. Номер корзины считается как hash(key) % len(self._buckets), а после увеличения таблицы len(self._buckets)
# становится другим. Если оставить пары в старых корзинах, то при поиске мы посчитаем новый номер корзины
# и будем искать ключ не там, где он лежит, поэтому все пары надо разложить заново.
#
# 2. Для 1000 строковых ключей stats() показывает (2048, 1000, n), где n обычно 4-5 (зависит от сида
# хеширования строк, бывает от 3 до 6), то есть ключи разложены равномерно и самая длинная корзина маленькая,
# поиск почти мгновенный. Если __hash__ всегда возвращает 42,
# все ключи попадают в одну корзину: stats() дает (2048, 1000, 1000) и таблица превращается в список.
# Каждая вставка тогда проходит по всей корзине и сравнивает ключи через ==, вставка 1000 ключей идет
# за O(n^2), у меня это примерно 0.07 сек против 0.002 сек, то есть в 35-40 раз медленнее.
