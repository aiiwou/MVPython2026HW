class Money:
    __slots__ = ('amount', 'currency')

    def __init__(self, amount, currency):
        object.__setattr__(self, 'amount', amount)
        object.__setattr__(self, 'currency', currency)

    def __setattr__(self, name, value):
        raise AttributeError("Объект Money неизменяемый")

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented

        return (
            self.amount == other.amount
            and self.currency == other.currency
        )

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented

        if self.currency != other.currency:
            raise ValueError("Нельзя складывать разные валюты")

        return Money(
            self.amount + other.amount,
            self.currency
        )

    def __repr__(self):
        return f"Money({self.amount!r}, {self.currency!r})"


def total_by_currency(payments):
    totals = {}

    for payment in payments:
        currency = payment.currency

        if currency in totals:
            totals[currency] = totals[currency] + payment
        else:
            totals[currency] = payment

    return totals


if __name__ == '__main__':
    # Равенство и хеширование.
    assert Money(100, 'RUB') == Money(100, 'RUB')
    assert Money(100, 'RUB') != Money(100, 'USD')
    assert len({
        Money(100, 'RUB'),
        Money(100, 'RUB'),
        Money(100, 'USD')
    }) == 2

    # Использование как ключа словаря.
    prices = {Money(100, 'RUB'): 'сто рублей'}
    assert prices[Money(100, 'RUB')] == 'сто рублей'

    # Сложение.
    assert Money(100, 'RUB') + Money(50, 'RUB') == Money(150, 'RUB')

    # Неизменяемость полей и запрет новых атрибутов.
    for action in (
        lambda m: setattr(m, 'amount', 5),
        lambda m: setattr(m, 'extra', 1),
    ):
        try:
            action(Money(1, 'RUB'))
            assert False, 'ожидали AttributeError'
        except AttributeError:
            pass

    # Разные валюты складывать нельзя.
    try:
        Money(1, 'RUB') + Money(1, 'USD')
        assert False, 'ожидали ValueError'
    except ValueError:
        pass

    # Суммирование по валютам.
    pays = [
        Money(100, 'RUB'),
        Money(5, 'USD'),
        Money(250, 'RUB'),
    ]

    assert total_by_currency(pays) == {
        'RUB': Money(350, 'RUB'),
        'USD': Money(5, 'USD'),
    }

    assert repr(Money(1500, 'RUB')) == "Money(1500, 'RUB')"
    assert Money(0, 'RUB') + Money(0, 'RUB') == Money(0, 'RUB')
    assert total_by_currency([]) == {}

    print("Все проверки пройдены!")

'''
Если бы поля Money можно было изменять после помещения объекта
в множество или использования в качестве ключа словаря, изменение
amount или currency могло бы изменить хеш объекта. Например, как
в примере с Point из лекции, изменение координат объекта после
добавления в множество может нарушить поиск по хешу: объект останется
в старой корзине, хотя его новый хеш указывает на другую. Поэтому
объекты, используемые как ключи, должны сохранять хеш и равенство
на протяжении своего нахождения в хеш-таблице.
'''