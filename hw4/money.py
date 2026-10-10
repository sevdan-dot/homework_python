import copy
import pickle


class Money:
    __slots__ = ('amount', 'currency')

    def __init__(self, amount, currency):
        if not isinstance(amount, int) or isinstance(amount, bool):
            raise TypeError('amount должен быть целым числом копеек')
        if not isinstance(currency, str):
            raise TypeError('currency должна быть строкой')
        object.__setattr__(self, 'amount', amount)
        object.__setattr__(self, 'currency', currency)

    def __setattr__(self, name, value):
        raise AttributeError(f'Money нельзя изменить: {name}')

    def __delattr__(self, name):
        raise AttributeError(f'Money нельзя изменить: {name}')

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f'нельзя сложить {self.currency} и {other.currency}')
        return Money(self.amount + other.amount, self.currency)

    def __reduce__(self):
        return Money, (self.amount, self.currency)

    def __repr__(self):
        return f'Money({self.amount}, {self.currency!r})'


def total_by_currency(payments):
    totals = {}
    for payment in payments:
        if payment.currency in totals:
            totals[payment.currency] = totals[payment.currency] + payment
        else:
            totals[payment.currency] = payment
    return totals


if __name__ == '__main__':
    assert len({Money(100, 'RUB'), Money(100, 'RUB'), Money(100, 'USD')}) == 2
    prices = {Money(100, 'RUB'): 'сто рублей'}
    assert prices[Money(100, 'RUB')] == 'сто рублей'
    assert Money(100, 'RUB') + Money(50, 'RUB') == Money(150, 'RUB')
    for action in (lambda m: setattr(m, 'amount', 5), lambda m: setattr(m, 'extra', 1)):
        try:
            action(Money(1, 'RUB'))
            assert False, 'ожидали AttributeError'
        except AttributeError:
            pass
    try:
        Money(1, 'RUB') + Money(1, 'USD')
        assert False, 'ожидали ValueError'
    except ValueError:
        pass
    pays = [Money(100, 'RUB'), Money(5, 'USD'), Money(250, 'RUB')]
    assert total_by_currency(pays) == {'RUB': Money(350, 'RUB'), 'USD': Money(5, 'USD')}

    a = Money(100, 'RUB')
    b = Money(50, 'RUB')
    c = a + b
    assert c is not a and a == Money(100, 'RUB') and b == Money(50, 'RUB')
    assert hash(Money(7, 'USD')) == hash(Money(7, 'USD'))
    assert Money(100, 'RUB') != Money(100, 'USD')
    assert Money(100, 'RUB') != 100
    assert Money(100, 'RUB').__eq__(100) is NotImplemented
    assert repr(Money(1500, 'RUB')) == "Money(1500, 'RUB')"
    assert total_by_currency([]) == {}
    try:
        del a.amount
        assert False, 'ожидали AttributeError'
    except AttributeError:
        pass
    try:
        Money(1, 'RUB') + 1
        assert False, 'ожидали TypeError'
    except TypeError:
        pass
    for args in (('10', 'RUB'), (1.5, 'RUB'), (True, 'RUB'), (10, None)):
        try:
            Money(*args)
            assert False, 'ожидали TypeError'
        except TypeError:
            pass

    m = Money(300, 'USD')
    assert copy.copy(m) == m
    assert copy.deepcopy({'pay': m}) == {'pay': m}
    assert pickle.loads(pickle.dumps(m)) == m
    print('все проверки прошли')

# Хеш объекта считается один раз в момент, когда его кладут в множество или словарь, и по нему выбирается корзина.
# Если потом поменять поля, как с Point на лекции (visited = {p}, потом p.x = 100), то новый хеш
# укажет на другую корзину. Тогда `p in visited` вернет False, хотя объект там лежит, а по ключу из словаря
# нельзя будет достать значение. Плюс в множестве могут оказаться два равных объекта, и оно перестанет быть множеством.
