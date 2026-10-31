
class LRUCache:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity должен быть положительным")

        self._capacity = capacity
        self._data = {}

    def get(self, key, default=None):
        if key not in self._data:
            return default

        # Делаем ключ самым свежим.
        value = self._data.pop(key)
        self._data[key] = value

        return value

    def put(self, key, value):
        # Если ключ уже есть, удаляем старую запись,
        # чтобы вставить его в конец словаря.
        if key in self._data:
            del self._data[key]
        elif len(self._data) >= self._capacity:
            # Первый ключ словаря — самый старый.
            oldest_key = next(iter(self._data))
            del self._data[oldest_key]

        self._data[key] = value

    def __len__(self):
        return len(self._data)

    def __contains__(self, key):
        # Проверка наличия не меняет порядок.
        return key in self._data


if __name__ == '__main__':
    c = LRUCache(2)

    c.put('a', 1)
    c.put('b', 2)

    assert c.get('a') == 1
    c.put('c', 3)

    assert 'b' not in c
    assert c.get('a') == 1
    assert c.get('c') == 3

    c.put('a', 10)
    c.put('d', 4)

    assert c.get('c') is None
    assert c.get('a') == 10
    assert len(c) == 2

    # Проверка default.
    assert c.get('missing', -1) == -1

    # Проверка, что __contains__ не делает ключ свежим.
    c = LRUCache(2)
    c.put('a', 1)
    c.put('b', 2)

    assert 'a' in c
    c.put('c', 3)

    assert 'a' not in c
    assert 'b' in c

    # Перезапись существующего ключа не увеличивает размер.
    c.put('b', 20)
    assert len(c) == 2
    assert c.get('b') == 20

    print("Все проверки пройдены!")

'''
В Python dict сохраняет порядок вставки. Самый старый ключ
находится в начале словаря, поэтому его можно получить через
next(iter(self._data)), а затем удалить через del. Получение
первого элемента итератора и удаление по ключу работают за O(1)
в среднем, поэтому операции кэша тоже имеют среднюю сложность O(1).
Для обновления свежести ключ удаляется и вставляется заново.
'''
