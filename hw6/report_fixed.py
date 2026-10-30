# Формулировка задания
#
# Задание 3. Ревью кода от LLM
#
# Студент попросил ассистента написать модуль отчета по заказам. Код выглядит аккуратно,
# у функций есть docstring, но в нем не меньше шести проблем. Часть из них роняет программу,
# часть молча дает неправильный результат, а одна станет проблемой только на большом файле.
#
# Скопируйте код в hw6/report.py без изменений (там исходная версия).
#
# Сдать нужно три файла:
# hw6/review.md: таблица найденных проблем (функция; что не так; конкретный сценарий;
#   серьезность: падение / тихо неверный результат / производительность);
# hw6/report_fixed.py: исправленная версия с тем же интерфейсом функций. Для last_orders
#   найдите решение, которое не читает весь файл в память (подсказка: collections.deque
#   с параметром maxlen);
# hw6/test_report.py: для каждой проблемы одна проверка, которая падает на report.py и
#   проходит на report_fixed.py.
#
# Ожидаемый правильный отчет на тестовых данных: 5 заказов, суммы
# {'anna': 800.0, 'bob': 80.0, 'kate': 300.0}, крупных заказов нет, VIP с превышением
# лимита: ['anna', 'bob']. Для Кейт лимит не указан: решение по ней обосновано в review.md.

from collections import deque


def read_orders(path):
    """Лениво читает заказы из файла: на каждой строке user,amount."""
    # генераторная функция: файл закрывается при исчерпании генератора, а не на return
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                yield line.split(',')


def totals_by_user(orders):
    """Сумма заказов по каждому пользователю."""
    result = {}
    for order in orders:
        user, amount = order[0], order[1]
        result[user] = result.get(user, 0.0) + float(amount)
    return result


def has_large_orders(orders, threshold=1000):
    """Есть ли хотя бы один заказ дороже threshold."""
    return any(float(o[1]) > threshold for o in orders)


def vip_over_limit(totals, vip_users, vip_limits):
    """VIP-клиенты, превысившие свой лимит. VIP без лимита пропускается (см. review.md)."""
    limits = dict(zip(vip_users, vip_limits))
    return [u for u in vip_users if u in limits and totals.get(u, 0) > limits[u]]


def last_orders(path, n=5):
    """Последние n строк файла заказов."""
    with open(path, encoding='utf-8') as f:
        tail = deque(f, maxlen=n)  # в памяти только последние n строк
    return [line.strip() for line in tail]


def build_report(path, vip_users, vip_limits):
    # read_orders одноразовый, поэтому открываем файл заново для каждого потребителя
    count = sum(1 for _ in read_orders(path))
    totals = totals_by_user(read_orders(path))
    return {
        'orders': count,
        'totals': totals,
        'has_large': has_large_orders(read_orders(path)),
        'vip_over_limit': vip_over_limit(totals, vip_users, vip_limits),
        'last': last_orders(path, 3),
    }
