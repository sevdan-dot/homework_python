# Формулировка задания
#
# Задание 3. Ревью кода от LLM (файл hw6/test_report.py).
#
# Для каждой проблемы из review.md одна проверка, которая падает на report.py и проходит
# на report_fixed.py. Модуль подключается через переменную, чтобы прогнать тесты на обеих
# версиях:
#   python test_report.py report_fixed   # исправленная версия, все проверки проходят
#   python test_report.py report         # исходная версия, падает

import importlib
import sys
import tracemalloc

module = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else 'report_fixed')

ORDERS = 'orders.txt'


def setup():
    with open(ORDERS, 'w', encoding='utf-8') as f:
        f.write('anna,100\nbob,50\n\nanna,700\nkate,300\nbob,30\n')


def test_read_orders_file_not_closed():  # проблема 1: генератор над закрытым файлом
    rows = list(module.read_orders(ORDERS))
    assert len(rows) == 5 and rows[0] == ['anna', '100']


def test_totals_by_user_unsorted():  # проблема 3: groupby по неотсортированному входу
    orders = [['anna', '100'], ['bob', '50'], ['anna', '700'], ['kate', '300'], ['bob', '30']]
    assert module.totals_by_user(orders) == {'anna': 800.0, 'bob': 80.0, 'kate': 300.0}


def test_has_large_orders():  # проблема 4: bool(генератор) всегда True
    assert module.has_large_orders([['anna', '100'], ['bob', '50']], 1000) is False
    assert module.has_large_orders([['x', '2000']], 1000) is True


def test_vip_over_limit():  # проблема 5: zip усекает список лимитов (латентная, см. review.md)
    # Прямой вызов на данных задания одинаков в обеих версиях и лишь фиксирует решение по Кейт.
    assert module.vip_over_limit(
        {'anna': 800.0, 'bob': 80.0, 'kate': 300.0},
        ['anna', 'bob', 'kate'], [500, 10]) == ['anna', 'bob']
    # Регрессия ловится на уровне build_report (report.py там падает по проблеме 1).
    report = module.build_report(ORDERS, ['anna', 'bob', 'kate'], [500, 10])
    assert report['vip_over_limit'] == ['anna', 'bob']


def test_build_report_no_generator_reuse():  # проблема 2: повторное чтение исчерпанного генератора
    report = module.build_report(ORDERS, ['anna', 'bob', 'kate'], [500, 10])
    assert report['orders'] == 5
    assert report['totals'] == {'anna': 800.0, 'bob': 80.0, 'kate': 300.0}
    assert report['has_large'] is False
    assert report['last'] == ['anna,700', 'kate,300', 'bob,30']


def test_last_orders_streaming():  # проблема 6: readlines() читает весь файл в память
    big = 'orders_big.txt'
    with open(big, 'w', encoding='utf-8') as f:
        for i in range(200_000):
            f.write(f'user{i % 100},{i % 1000}\n')
    tracemalloc.start()
    tail = module.last_orders(big, 3)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert len(tail) == 3
    assert peak < 1_000_000


if __name__ == '__main__':
    setup()
    tests = [fn for name, fn in sorted(globals().items())
             if name.startswith('test_') and callable(fn)]
    for fn in tests:
        fn()
        print('ok', fn.__name__)
    print(f'все {len(tests)} проверки прошли на модуле {module.__name__}')
