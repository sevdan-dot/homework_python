class LRUCache:
    def __init__(self, capacity):
        if capacity <= 0:
            raise ValueError('capacity должен быть больше 0')
        self.capacity = capacity
        self._data = {}

    def get(self, key, default=None):
        if key not in self._data:
            return default
        value = self._data.pop(key)
        self._data[key] = value
        return value

    def put(self, key, value):
        if key in self._data:
            del self._data[key]
        elif len(self._data) >= self.capacity:
            oldest = next(iter(self._data))
            del self._data[oldest]
        self._data[key] = value

    def __len__(self):
        return len(self._data)

    def __contains__(self, key):
        return key in self._data


if __name__ == '__main__':
    c = LRUCache(2)
    c.put('a', 1)
    c.put('b', 2)
    assert c.get('a') == 1        # теперь 'a' свежее, чем 'b'
    c.put('c', 3)                 # вытесняется 'b'
    assert 'b' not in c and c.get('a') == 1 and c.get('c') == 3
    c.put('a', 10)                # перезапись делает 'a' свежим
    c.put('d', 4)                 # вытесняется 'c'
    assert c.get('c') is None and c.get('a') == 10 and len(c) == 2

    c = LRUCache(2)
    c.put('x', 1)
    c.put('y', 2)
    assert 'x' in c
    c.put('z', 3)
    assert 'x' not in c and 'y' in c and 'z' in c
    assert c.get('nope', 'default') == 'default'

    c = LRUCache(1)
    c.put('a', None)
    assert 'a' in c and c.get('a', 'default') is None
    c.put('b', 2)
    assert 'a' not in c and len(c) == 1

    try:
        LRUCache(0)
        assert False, 'ожидали ValueError'
    except ValueError:
        pass
    print('все проверки прошли')

# Обычный dict хранит ключи в порядке вставки, поэтому самый старый ключ всегда первый.
# Когда к ключу обращаются, я делаю pop и вставляю его заново, и он переезжает в конец.
# Самый старый ключ достается через next(iter(self._data)), а del по ключу в словаре O(1) в среднем.
# Но в CPython это не O(1): после удаления в начале массива записей словаря остаются пустые места,
# и next(iter()) каждый раз проходит их по одному. Размер словаря не меняется, поэтому он перестраивается,
# только когда в массиве кончается место, и к этому моменту пустых мест набирается порядка capacity.
# В итоге put с вытеснением стоит примерно O(capacity). Я замерил: capacity 1000 около 0.9 мкс на put,
# 4000 около 2.7 мкс, 16000 около 12 мкс, 64000 около 37 мкс, то есть время растет почти линейно.
# Честный O(1) дал бы двусвязный список поверх словаря (как в OrderedDict), но по условию нужен обычный dict.
