class BookTracker:
    def __init__(self):
        self.books = []
        self.by_id = {}
        self.authors = set()
        self._next_id = 1

    def add(self, title, author, year):
        book = (self._next_id, title, author, year)
        self._next_id += 1
        self.books.append(book)
        self.by_id[book[0]] = book
        self.authors.add(author)
        return book[0]

    def get(self, book_id):
        return self.by_id.get(book_id)

    def remove(self, book_id):
        book = self.by_id.pop(book_id, None)
        if book is None:
            return False
        self.books.remove(book)
        self.authors = {b[2] for b in self.books}
        return True

    def by_author(self, author):
        return [b for b in self.books if b[2] == author]

    def all_books(self):
        return list(self.books)


if __name__ == '__main__':
    tracker = BookTracker()
    first = tracker.add('Мастер и Маргарита', 'Булгаков', 1940)
    tracker.add('Собачье сердце', 'Булгаков', 1925)
    third = tracker.add('Пикник на обочине', 'Стругацкие', 1971)

    assert tracker.get(first) == (1, 'Мастер и Маргарита', 'Булгаков', 1940)
    assert tracker.get(100) is None
    assert tracker.authors == {'Булгаков', 'Стругацкие'}
    assert len(tracker.by_author('Булгаков')) == 2

    books = tracker.all_books()
    books.append('мусор')
    assert len(tracker.books) == 3

    second_tracker = BookTracker()
    assert second_tracker.books == [] and second_tracker.authors == set()

    assert tracker.remove(third)
    assert not tracker.remove(third)
    assert tracker.authors == {'Булгаков'}
    assert len(tracker.books) == 2

    for book in tracker.all_books():
        print(book)
