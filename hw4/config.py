
class Config:
    def __init__(self, data):
        object.__setattr__(self, '_data', data)

    def __getattr__(self, name):
        # __getattr__ вызывается, если обычный поиск атрибута
        # не нашёл name.
        data = object.__getattribute__(self, '_data')

        if name not in data:
            raise AttributeError(
                f"Config has no attribute {name!r}"
            )

        value = data[name]

        # Вложенный словарь тоже оборачиваем в Config.
        if isinstance(value, dict):
            return Config(value)

        return value

    def __setattr__(self, name, value):
        # Внутреннее состояние храним в самом объекте.
        if name == '_data':
            object.__setattr__(self, name, value)
            return

        # Остальные атрибуты записываем в исходный словарь.
        data = object.__getattribute__(self, '_data')
        data[name] = value

    def __dir__(self):
        # Добавляем ключи словаря к стандартным атрибутам.
        data = object.__getattribute__(self, '_data')
        return sorted(set(object.__dir__(self)) | set(data.keys()))

    def to_dict(self):
        return object.__getattribute__(self, '_data')


if __name__ == '__main__':
    raw = {
        'db': {'host': 'localhost', 'port': 5432},
        'debug': True,
    }

    cfg = Config(raw)

    assert cfg.debug is True
    assert cfg.db.host == 'localhost'
    assert cfg.db.port == 5432

    assert getattr(cfg, 'timeout', 30) == 30
    assert hasattr(cfg.db, 'user') is False

    cfg.db.port = 6543
    assert raw['db']['port'] == 6543

    cfg.timeout = 10
    assert raw['timeout'] == 10

    assert cfg.to_dict() is raw
    assert 'db' in dir(cfg)

    # Проверяем добавление нового вложенного словаря.
    cfg.cache = {'enabled': True, 'size': 100}
    assert cfg.cache.enabled is True
    assert cfg.cache.size == 100
    assert raw['cache']['size'] == 100

    # Проверяем, что отсутствующий атрибут вызывает AttributeError.
    try:
        cfg.unknown
        assert False, 'ожидали AttributeError'
    except AttributeError:
        pass

    print("Все проверки пройдены!")

'''
hasattr и getattr с default используют AttributeError как признак
отсутствующего атрибута. Если выбрасывать KeyError, исключение
не будет обработано этими функциями и выйдет наружу.

Чтобы избежать бесконечной рекурсии при обращении к внутреннему
словарю, я использую object.__getattribute__(self, '_data'),
который обходит переопределённый __getattr__. Для инициализации
и установки внутреннего атрибута используется object.__setattr__.
Вложенные Config хранят ссылки на исходные словари, поэтому
изменения через точку меняют исходный объект.
'''