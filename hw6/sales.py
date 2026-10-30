# Формулировка задания
#
# Задание 1. Ленивая обработка выгрузки продаж
#
# Напишите набор функций-этапов для обработки CSV-выгрузки продаж. Файл может быть
# больше оперативной памяти, поэтому все этапы, кроме итоговых агрузок, должны быть
# генераторами. Модуль csv использовать можно, но и split(',') достаточно.
#
# Формат файла: первая непустая и не-комментарная строка это заголовок
# date,category,product,qty,price. Строки, начинающиеся с #, и пустые строки
# пропускаются. Файл упорядочен по дате.
#
# Функции:
# read_sales(path, errors=None): генератор словарей вида {'date': '2026-10-01',
#   'category': 'food', 'product': 'tea', 'qty': 3, 'price': 120.5}. Битые строки
#   (не то число полей, нечисловые qty или price) пропускаются. Если передан список
#   errors, в него добавляется пара (номер строки в файле, текст строки);
# daily_revenue(rows): генератор пар (дата, выручка за день), выручка округлена до
#   2 знаков. Используйте то, что файл упорядочен по дате;
# running_revenue(daily): генератор пар (дата, выручка нарастающим итогом);
# revenue_by_category(rows): словарь {категория: выручка};
# best_days(daily, n=3): список из n самых прибыльных дней, по убыванию выручки.
#   Подумайте, как сделать это без сортировки всех дней (подсказка: модуль heapq).
#
# Проверка на большом файле: сгенерируйте выгрузку за год (около 1 млн строк, 30 МБ)
# и измерьте через tracemalloc пик памяти для best_days(daily_revenue(read_sales(...))).
# Пик должен быть меньше 1 МБ. Результат замера запишите в комментарий.
#
# В комментарии ответьте: почему daily_revenue дал бы неправильный результат на
# неупорядоченном файле, и как бы вы решили задачу в этом случае (какой ценой по памяти)?

import heapq
from itertools import groupby


def read_sales(path, errors=None):
    with open(path, encoding='utf-8') as f:
        header_seen = False
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            if not header_seen:
                header_seen = True
                continue
            fields = line.split(',')
            if len(fields) != 5:
                if errors is not None:
                    errors.append((lineno, line))
                continue
            date, category, product, qty, price = fields
            try:
                qty = int(qty)
                price = float(price)
            except ValueError:
                if errors is not None:
                    errors.append((lineno, line))
                continue
            yield {'date': date, 'category': category, 'product': product,
                   'qty': qty, 'price': price}


def daily_revenue(rows):
    for date, group in groupby(rows, key=lambda r: r['date']):
        total = sum(r['qty'] * r['price'] for r in group)
        yield date, round(total, 2)


def running_revenue(daily):
    total = 0.0
    for date, revenue in daily:
        total = round(total + revenue, 2)
        yield date, total


def revenue_by_category(rows):
    totals = {}
    for r in rows:
        totals[r['category']] = totals.get(r['category'], 0.0) + r['qty'] * r['price']
    return {category: round(value, 2) for category, value in totals.items()}


def best_days(daily, n=3):
    return heapq.nlargest(n, daily, key=lambda pair: pair[1])


SAMPLE = '''# выгрузка продаж
date,category,product,qty,price

2026-10-01,books,Dune,2,500
2026-10-01,food,tea,3,120.5
2026-10-02,books,Solaris,1,450
# комментарий посреди файла
2026-10-02,food,coffee,много,300
2026-10-02,toys,ball,4,250
2026-10-03,food,tea,10,120.5
2026-10-03,books,Dune
'''


def make_big(path='sales_big.csv', days=365, rows_per_day=3000):
    import random
    from datetime import date, timedelta
    random.seed(0)
    cats = {'books': ['Dune', 'Solaris'], 'food': ['tea', 'coffee'], 'toys': ['ball', 'lego']}
    start = date(2025, 1, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('date,category,product,qty,price\n')
        for d in range(days):
            day = (start + timedelta(days=d)).isoformat()
            for _ in range(rows_per_day):
                c = random.choice(list(cats))
                qty = random.randint(1, 5) if random.random() > 0.001 else 'oops'
                f.write(f'{day},{c},{random.choice(cats[c])},{qty},{random.randint(50, 900)}\n')


if __name__ == '__main__':
    import types
    with open('sales_sample.csv', 'w', encoding='utf-8') as f:
        f.write(SAMPLE)

    errors = []
    rows = list(read_sales('sales_sample.csv', errors))
    assert len(rows) == 5
    assert rows[1] == {'date': '2026-10-01', 'category': 'food', 'product': 'tea', 'qty': 3, 'price': 120.5}
    assert [no for no, _ in errors] == [8, 11]

    daily = list(daily_revenue(read_sales('sales_sample.csv')))
    assert daily == [('2026-10-01', 1361.5), ('2026-10-02', 1450.0), ('2026-10-03', 1205.0)]
    assert list(running_revenue(iter(daily))) == [
        ('2026-10-01', 1361.5), ('2026-10-02', 2811.5), ('2026-10-03', 4016.5)]
    assert revenue_by_category(read_sales('sales_sample.csv')) == {
        'books': 1450.0, 'food': 1566.5, 'toys': 1000.0}
    assert best_days(daily_revenue(read_sales('sales_sample.csv')), 2) == [
        ('2026-10-02', 1450.0), ('2026-10-01', 1361.5)]
    assert isinstance(read_sales('sales_sample.csv'), types.GeneratorType)
    assert isinstance(daily_revenue([]), types.GeneratorType)

    import os
    import tracemalloc
    make_big('sales_big.csv')
    tracemalloc.start()
    top = best_days(daily_revenue(read_sales('sales_big.csv')))
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    os.remove('sales_big.csv')
    assert peak < 1_000_000
    print('топ-3 дня:', top)
    print(f'пик памяти на большом файле: {peak / 1024:.1f} КБ')
    print('все проверки прошли')

# Замер на большом файле (1 095 000 строк, ~31 МБ): пик памяти ≈ 148 КБ (< 1 МБ).
#
# Почему daily_revenue дал бы неправильный результат на неупорядоченном файле и как решить:
# groupby группирует только ПОДРЯД идущие строки с одинаковым ключом. Если даты перемешаны,
# одна дата разобьётся на несколько отдельных групп, и daily_revenue выдаст несколько пар
# (дата, частичная выручка) вместо одной суммы за день, а running_revenue и best_days посчитают
# по обрывкам мусор. Для неупорядоченного файла пришлось бы агрегировать в словарь {дата: выручка}
# за один проход (это уже не генератор) и затем отсортировать даты. Цена — память O(числа
# различных дат): все дни держатся в памяти, тогда как на упорядоченном файле хватает O(1).
