
class MyDict:
    def __init__(self, size=8):
        if size < 1:
            raise ValueError("Размер таблицы должен быть положительным")

        self._buckets = [[] for _ in range(size)]
        self._entries = []
        self._len = 0

    def _bucket_index(self, key):
        return hash(key) % len(self._buckets)

    def _find_entry(self, key):
        """Возвращает индекс записи или None, если ключ не найден."""
        bucket_index = self._bucket_index(key)

        for entry_index in self._buckets[bucket_index]:
            stored_key = self._entries[entry_index][0]

            if stored_key == key:
                return entry_index

        return None

    def _rebuild_buckets(self, size=None):
        """Перестраивает корзины по текущим записям."""
        if size is not None:
            self._buckets = [[] for _ in range(size)]
        else:
            self._buckets = [[] for _ in range(len(self._buckets))]

        for entry_index, (key, _) in enumerate(self._entries):
            bucket_index = self._bucket_index(key)
            self._buckets[bucket_index].append(entry_index)

    def _resize(self):
        new_size = len(self._buckets) * 2
        self._rebuild_buckets(new_size)

    def __setitem__(self, key, value):
        bucket_index = self._bucket_index(key)

        for entry_index in self._buckets[bucket_index]:
            stored_key = self._entries[entry_index][0]

            if stored_key == key:
                self._entries[entry_index] = (stored_key, value)
                return

        entry_index = len(self._entries)
        self._entries.append((key, value))
        self._buckets[bucket_index].append(entry_index)
        self._len += 1

        if self._len > len(self._buckets) * 2 / 3:
            self._resize()

    def __getitem__(self, key):
        entry_index = self._find_entry(key)

        if entry_index is None:
            raise KeyError(key)

        return self._entries[entry_index][1]

    def __delitem__(self, key):
        bucket_index = self._bucket_index(key)
        entry_index = None

        for index in self._buckets[bucket_index]:
            if self._entries[index][0] == key:
                entry_index = index
                break

        if entry_index is None:
            raise KeyError(key)

        self._entries.pop(entry_index)
        self._len -= 1
        self._rebuild_buckets()

    def __contains__(self, key):
        return self._find_entry(key) is not None

    def __len__(self):
        return self._len

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return [key for key, _ in self._entries]

    def values(self):
        return [value for _, value in self._entries]

    def items(self):
        return self._entries.copy()

    def __iter__(self):
        return (key for key, _ in self._entries)

    def stats(self):
        longest = max(len(bucket) for bucket in self._buckets)
        return len(self._buckets), self._len, longest

    def __repr__(self):
        content = ", ".join(
            f"{key!r}: {value!r}"
            for key, value in self._entries
        )
        return f"MyDict({{{content}}})"


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

    assert d.get('nope') is None
    assert d.get('nope', 0) == 0

    for bad in (
        lambda: d['nope'],
        lambda: d.__delitem__('nope'),
    ):
        try:
            bad()
            assert False, 'ожидали KeyError'
        except KeyError:
            pass

    buckets, size, longest = d.stats()
    assert size == 999
    assert size <= buckets * 2 / 3

    # Проверка порядка вставки.
    d = MyDict(size=2)
    d['b'] = 2
    d['a'] = 1
    d['c'] = 3 

    assert list(d) == ['b', 'a', 'c']
    assert d.keys() == ['b', 'a', 'c']
    assert d.values() == [2, 1, 3]
    assert d.items() == [('b', 2), ('a', 1), ('c', 3)]

    # Обновление не меняет порядок.
    d['a'] = 10
    assert list(d) == ['b', 'a', 'c']

    # Удаление и повторная вставка.
    del d['a']
    d['a'] = 100
    assert list(d) == ['b', 'c', 'a']

    assert repr(d) == "MyDict({'b': 2, 'c': 3, 'a': 100})"

    print(d.stats())
    print("Все проверки пройдены!")
