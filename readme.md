# Домашние задания по Python
## Лекция 2 (`hw3/`)

- **Задание 1.** Трекер книг с осознанным выбором коллекций: [hw3/tracker.py](hw3/tracker.py), объяснение выбора коллекций в [hw3/README.md](hw3/README.md).
- **Задание 2.** Свой баг-репорт: [hw3/my_bug.py](hw3/my_bug.py).
- **Задание 3 (дополнительное).** Mutable default argument в реальном проекте, CKAN, `ckan/lib/mailer.py`:
  https://github.com/ckan/ckan/blob/88b5aa3b1838c4ddca248f78690cd4f309689d06/ckan/lib/mailer.py#L31
  (`headers={}` в `_mail_recipient`, в https://github.com/ckan/ckan/pull/4034 его заменили на `headers=None`).
  Еще два таких же `headers={}` в этом файле (строки 101 и 109) PR не тронул. Сам `headers` в функциях только читается,
  так что реально ничего не ломалось, но словарь общий на все вызовы, и любое изменение попало бы в следующие письма.

## Лекция 4 (`hw4/`)

- **Задание 1 и 1\*.** Своя хеш-таблица `MyDict`: [hw4/my_dict.py](hw4/my_dict.py).
- **Задание 2.** Хешируемый класс `Money`: [hw4/money.py](hw4/money.py).
- **Задание 3 и 3\*.** Поисковый индекс `SearchIndex`: [hw4/search_index.py](hw4/search_index.py).
- **Задание 4.** Кэширование через замыкание `memoize` и эксперимент с `fib`: [hw4/memoize.py](hw4/memoize.py).
- **Задание 5\*.** LRU-кэш на обычном словаре: [hw4/lru.py](hw4/lru.py).
- **Задание 6\*.** Конфиг с доступом через точку: [hw4/config.py](hw4/config.py).

## Лекция 6 (`hw6/`)

- **Задание 1.** Ленивая обработка выгрузки продаж генераторами: [hw6/sales.py](hw6/sales.py).
- **Задание 2 и 2\*.** Свой диапазон дат `DateRange` со срезами: [hw6/date_range.py](hw6/date_range.py).
- **Задание 3.** Ревью кода от LLM: таблица проблем в [hw6/review.md](hw6/review.md), исправленная версия [hw6/report_fixed.py](hw6/report_fixed.py), тесты [hw6/test_report.py](hw6/test_report.py); исходный код без изменений — [hw6/report.py](hw6/report.py).

Ответы на вопросы из заданий лежат в комментариях в конце соответствующих файлов. Исключения: обоснование структур
`SearchIndex` в docstring класса, как просит условие, а объяснение выбора коллекций к заданию 1 лекции 2 в `hw3/README.md`.
