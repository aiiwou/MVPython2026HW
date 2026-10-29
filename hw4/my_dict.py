from time import perf_counter

class MyDict:
    def __init__(self, size=8):
        if size <= 0:
            raise ValueError("Размер таблицы должен быть положительным")

        self._buckets = [[] for _ in range(size)]
        self._len = 0

    def _get_bucket_index(self, key):
        return hash(key) % len(self._buckets)

    def _find_entry(self, bucket, key):
        for index, (stored_key, _) in enumerate(bucket):
            if stored_key == key:
                return index
        return None

    def __setitem__(self, key, value):
        bucket_index = self._get_bucket_index(key)
        bucket = self._buckets[bucket_index]

        entry_index = self._find_entry(bucket, key)

        if entry_index is not None:
            bucket[entry_index] = (key, value)
            return

        bucket.append((key, value))
        self._len += 1

        if self._len > len(self._buckets) * 2 / 3:
            self._resize()

    def __getitem__(self, key):
        bucket_index = self._get_bucket_index(key)
        bucket = self._buckets[bucket_index]

        entry_index = self._find_entry(bucket, key)

        if entry_index is None:
            raise KeyError(key)

        return bucket[entry_index][1]

    def __delitem__(self, key):
        bucket_index = self._get_bucket_index(key)
        bucket = self._buckets[bucket_index]

        entry_index = self._find_entry(bucket, key)

        if entry_index is None:
            raise KeyError(key)

        del bucket[entry_index]
        self._len -= 1

    def __contains__(self, key):
        bucket_index = self._get_bucket_index(key)
        bucket = self._buckets[bucket_index]

        return self._find_entry(bucket, key) is not None

    def __len__(self):
        return self._len

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def _resize(self):
        old_buckets = self._buckets
        new_size = len(old_buckets) * 2

        self._buckets = [[] for _ in range(new_size)]

        for bucket in old_buckets:
            for key, value in bucket:
                index = self._get_bucket_index(key)
                self._buckets[index].append((key, value))

    def stats(self):
        bucket_count = len(self._buckets)
        longest = max(len(bucket) for bucket in self._buckets)

        return bucket_count, self._len, longest

    def __repr__(self):
        entries = []

        for bucket in self._buckets:
            for key, value in bucket:
                entries.append(f"{key!r}: {value!r}")

        return f"MyDict({{{', '.join(entries)}}})"


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

    # Проверка обновления значения без изменения размера.
    d['x'] = 1
    d['x'] = 2
    assert d['x'] == 2
    assert len(d) == 1000

    # Проверка удаления последнего элемента из корзины.
    del d['x']
    assert 'x' not in d
    assert len(d) == 999

    # Проверка коллизий.
    class BadHash:
        def __init__(self, value):
            self.value = value

        def __hash__(self):
            return 42

        def __eq__(self, other):
            if not isinstance(other, BadHash):
                return NotImplemented
            return self.value == other.value

    collision_dict = MyDict()
    collision_dict[BadHash('a')] = 10
    collision_dict[BadHash('b')] = 20

    assert collision_dict[BadHash('a')] == 10
    assert collision_dict[BadHash('b')] == 20
    assert len(collision_dict) == 2

    print(d.stats())
    print(collision_dict.stats())

    print('\nЭксперимент для ответа на второй вопрос')
    # Эксперимент: сравнение обычных ключей и ключей с коллизиями.
    string_dict = MyDict()
    start = perf_counter()

    for i in range(1000):
        string_dict[f'key{i}'] = i

    string_time = perf_counter() - start

    bad_hash_dict = MyDict()
    start = perf_counter()

    for i in range(1000):
        bad_hash_dict[BadHash(i)] = i

    bad_hash_time = perf_counter() - start

    print("Строковые ключи:")
    print("stats:", string_dict.stats())
    print(f"Время вставки: {string_time:.6f} сек.")

    print("\nКлючи с одинаковым хешем:")
    print("stats:", bad_hash_dict.stats())
    print(f"Время вставки: {bad_hash_time:.6f} сек.")

    if string_time > 0:
        print(f"\nЗамедление: {bad_hash_time / string_time:.1f}x")


'''
Ответы на теоретические вопросы
1. При увеличении таблицы нельзя просто копировать пары в корзины
с прежними номерами, потому что индекс вычисляется как hash(key) % N,
где N — текущее количество корзин. После увеличения N индекс может
измениться, поэтому все пары необходимо распределить заново.

2. Для 1000 строковых ключей stats() в моём эксперименте вернул
(2048, 1000, 6). Для 1000 объектов с одинаковым хешем результат
составил (2048, 1000, 1000). Время вставки составило примерно
0.001474 с для строковых ключей и 0.046536 с для ключей с коллизиями.
При одинаковом хеше все элементы попадают в одну цепочку, поэтому
поиск при вставке становится линейным, а суммарное время вставки
1000 элементов растёт примерно квадратично.
'''
