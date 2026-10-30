# Формулировка задания
#
# Задание 2. Свой диапазон дат
#
# Напишите класс DateRange(start, stop, step=1), аналог range для дат: от start
# включительно до stop не включительно, step в днях. Это повторение протокола
# итерации (лекция 6) и протокола контейнера (лекция 7).
#
# Требования:
# по объекту можно пройти сколько угодно раз, и вложенные циклы по одному объекту
#   работают правильно;
# len(r), r[i] с отрицательными индексами и IndexError за пределами;
# d in r работает за O(1), без перебора дат (проверка на диапазоне в 3.6 млн дней
#   должна выполняться мгновенно);
# reversed(r) работает без создания списка всех дат;
# step <= 0 вызывает ValueError;
# __repr__ и __eq__.
#
# В комментарии объясните: чем ваш класс отличается от варианта, где __iter__
# возвращает self, и какой баг был бы во втором варианте.
#
# 2*. Поддержите срезы: r[1:3] и r[::2] возвращают новый DateRange, а не список.
# Подсказка: посмотрите, что возвращает range(len(self))[срез].

from datetime import date, datetime, timedelta


class DateRange:
    def __init__(self, start, stop, step=1):
        if step <= 0:
            raise ValueError('step должен быть положительным')
        self.start = start
        self.stop = stop
        self.step = step

    def __len__(self):
        days = (self.stop - self.start).days
        if days <= 0:
            return 0
        return (days + self.step - 1) // self.step  # ceil(days / step)

    def __iter__(self):
        current = self.start
        for _ in range(len(self)):
            yield current
            current += timedelta(days=self.step)

    def __reversed__(self):
        for i in range(len(self) - 1, -1, -1):
            yield self.start + timedelta(days=i * self.step)

    def __contains__(self, item):
        # datetime — подкласс date, но элементы диапазона это чистые date;
        # datetime членом не считаем и не даём упасть на вычитании date-datetime
        if not isinstance(item, date) or isinstance(item, datetime):
            return False
        delta = (item - self.start).days
        total = (self.stop - self.start).days
        return 0 <= delta < total and delta % self.step == 0

    def __getitem__(self, index):
        n = len(self)
        if isinstance(index, slice):
            # range(n)[index] даёт индексы среза как арифметическую прогрессию
            indices = range(n)[index]
            new_start = self.start + timedelta(days=indices.start * self.step)
            new_stop = self.start + timedelta(days=indices.stop * self.step)
            return DateRange(new_start, new_stop, self.step * indices.step)
        if index < 0:
            index += n
        if not 0 <= index < n:
            raise IndexError('DateRange index out of range')
        return self.start + timedelta(days=index * self.step)

    def __eq__(self, other):
        if not isinstance(other, DateRange):
            return NotImplemented
        return (self.start, self.stop, self.step) == (other.start, other.stop, other.step)

    def __repr__(self):
        return f'DateRange({self.start!r}, {self.stop!r}, {self.step})'


if __name__ == '__main__':
    r = DateRange(date(2026, 10, 1), date(2026, 10, 11), 3)
    assert list(r) == [date(2026, 10, 1), date(2026, 10, 4), date(2026, 10, 7), date(2026, 10, 10)]
    assert list(r) == list(r)
    assert sum(1 for a in r for b in r) == 16
    assert len(r) == 4
    assert len(DateRange(date(2026, 1, 1), date(2026, 1, 1))) == 0
    assert len(DateRange(date(2026, 1, 5), date(2026, 1, 1))) == 0
    assert r[0] == date(2026, 10, 1) and r[-1] == date(2026, 10, 10)
    try:
        r[4]
        assert False, 'ожидали IndexError'
    except IndexError:
        pass
    assert date(2026, 10, 7) in r
    assert date(2026, 10, 8) not in r and date(2026, 10, 13) not in r
    assert list(reversed(r))[0] == date(2026, 10, 10)
    assert repr(r) == 'DateRange(datetime.date(2026, 10, 1), datetime.date(2026, 10, 11), 3)'
    assert DateRange(date(2026, 1, 1), date(2026, 1, 3)) == DateRange(date(2026, 1, 1), date(2026, 1, 3))
    big = DateRange(date(1, 1, 1), date(9999, 12, 31))
    assert date(2026, 10, 17) in big and len(big) == 3652058

    try:
        DateRange(date(2026, 1, 1), date(2026, 1, 5), 0)
        assert False, 'ожидали ValueError'
    except ValueError:
        pass
    assert 42 not in r and 'x' not in r
    assert datetime(2026, 10, 7, 12) not in r  # datetime не член и не роняет in
    assert date(5000, 6, 15) in big

    s = r[1:3]
    assert isinstance(s, DateRange) and list(s) == [date(2026, 10, 4), date(2026, 10, 7)]
    assert list(r[::2]) == [date(2026, 10, 1), date(2026, 10, 7)]
    print('все проверки прошли')

# Чем класс отличается от варианта, где __iter__ возвращает self, и какой был бы баг:
# если __iter__ возвращает self, DateRange становится собственным итератором с единственным
# внутренним курсором. Тогда пройти по объекту можно лишь один раз (после первого цикла он
# исчерпан, list(r) второй раз вернёт []), а вложенные циклы for a in r for b in r делят один
# курсор: внутренний исчерпает его, и внешний не получит остальных дат (баг Countdow из лекции).
# Здесь __iter__ возвращает новый генератор на каждый вызов, поэтому каждый проход независим
# (как CountdownRange), а состояние итерации не хранится в самом диапазоне.
