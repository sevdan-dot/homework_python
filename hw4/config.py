class Config:
    def __init__(self, data):
        object.__setattr__(self, '_data', data)

    def __getattr__(self, name):
        if name == '_data':
            raise AttributeError(name)
        try:
            value = self._data[name]
        except KeyError:
            raise AttributeError(f'в конфиге нет ключа {name!r}') from None
        if isinstance(value, dict):
            return Config(value)
        return value

    def __setattr__(self, name, value):
        if isinstance(value, Config):
            value = value.to_dict()
        self._data[name] = value

    def __dir__(self):
        keys = {key for key in self._data if isinstance(key, str)}
        return sorted(set(super().__dir__()) | keys)

    def __repr__(self):
        return f'Config({self._data!r})'

    def to_dict(self):
        return self._data


if __name__ == '__main__':
    raw = {'db': {'host': 'localhost', 'port': 5432}, 'debug': True}
    cfg = Config(raw)
    assert cfg.debug is True
    assert cfg.db.host == 'localhost' and cfg.db.port == 5432
    assert getattr(cfg, 'timeout', 30) == 30
    assert hasattr(cfg.db, 'user') is False
    cfg.db.port = 6543                    # запись меняет исходный словарь
    assert raw['db']['port'] == 6543
    cfg.timeout = 10
    assert raw['timeout'] == 10
    assert cfg.to_dict() is raw
    assert 'db' in dir(cfg)               # подсказка: метод __dir__

    assert cfg.db.to_dict() is raw['db']
    cfg.cache = {'size': 100}
    assert cfg.cache.size == 100
    cfg.cache.size = 200
    assert raw['cache'] == {'size': 200}
    cfg.copy_db = cfg.db
    assert raw['copy_db'] is raw['db']
    assert 'to_dict' in dir(cfg) and 'host' in dir(cfg.db)

    assert 'x' in dir(Config({1: 'a', 'x': 1}))

    try:
        cfg.nope
        assert False, 'ожидали AttributeError'
    except AttributeError:
        pass

    import copy
    copied = copy.deepcopy(cfg)
    assert copied.db.host == 'localhost' and copied.to_dict() is not raw
    print(cfg)
    print('все проверки прошли')

# 1. hasattr и getattr со значением по умолчанию ловят только AttributeError. Если бросить KeyError,
# hasattr(cfg.db, 'user') не вернет False, а упадет с KeyError, и getattr(cfg, 'timeout', 30) тоже упадет
# вместо того чтобы вернуть 30.
#
# 2. Словарь лежит в атрибуте _data, и в __init__ я записываю его через object.__setattr__, потому что мой
# __setattr__ сам обращается к self._data, а его еще нет. После этого self._data находится обычным поиском
# в __dict__ экземпляра, и __getattr__ для него не вызывается. Но если объект создан без __init__
# (например при copy.deepcopy), _data нет и __getattr__ искал бы self._data бесконечно, поэтому
# для имени '_data' сразу бросаю AttributeError.
