import re
from collections import Counter


class SearchIndex:
    """Инвертированный индекс по текстовым документам.

    _index: слово -> множество id документов, где оно есть. Множество, потому что id в нем не повторяются,
    а пересечение и объединение множеств как раз дают search_all и search_any.
    _docs: id документа -> Counter слов этого документа. По нему remove и повторный add знают, из каких
    множеств убрать id, и не перебирают весь индекс.
    _totals: Counter слов по всем документам, чтобы top_words не пересчитывал все документы заново.
    """

    def __init__(self):
        self._index = {}
        self._docs = {}
        self._totals = Counter()

    @staticmethod
    def _words(text):
        return re.findall(r'\w+', text.lower())

    def add(self, doc_id, text):
        if doc_id in self._docs:
            self.remove(doc_id)
        counts = Counter(self._words(text))
        self._docs[doc_id] = counts
        self._totals.update(counts)
        for word in counts:
            self._index.setdefault(word, set()).add(doc_id)

    def remove(self, doc_id):
        counts = self._docs.pop(doc_id, None)
        if counts is None:
            return
        self._totals.subtract(counts)
        for word in counts:
            if self._totals[word] <= 0:
                del self._totals[word]
            docs = self._index[word]
            docs.discard(doc_id)
            if not docs:
                del self._index[word]

    def _query_words(self, words):
        result = []
        for word in words:
            result.extend(self._words(str(word)))
        return result

    def search_all(self, *words):
        sets = [self._index.get(word, set()) for word in self._query_words(words)]
        if not sets:
            return set()
        sets.sort(key=len)
        result = set(sets[0])
        for s in sets[1:]:
            result &= s
        return result

    def search_any(self, *words):
        result = set()
        for word in self._query_words(words):
            result |= self._index.get(word, set())
        return result

    def top_words(self, n):
        if n <= 0:
            return []
        return sorted(self._totals.items(), key=lambda item: (-item[1], item[0]))[:n]

    def search_ranked(self, query, limit=10):
        words = set(self._words(query))
        scores = {}
        for doc_id in self.search_any(*words):
            counts = self._docs[doc_id]
            scores[doc_id] = sum(counts[word] for word in words)
        return sorted(scores, key=lambda doc_id: (-scores[doc_id], doc_id))[:limit]


if __name__ == '__main__':
    idx = SearchIndex()
    idx.add(1, 'Python is a programming language.')
    idx.add(2, 'A dict is a hash table; a set is a hash table too!')
    idx.add(3, 'Python dict and set are fast.')
    assert idx.search_all('python') == {1, 3}
    assert idx.search_all('dict', 'set') == {2, 3}
    assert idx.search_all('python', 'hash') == set()
    assert idx.search_any('language', 'fast') == {1, 3}
    assert idx.search_all('PYTHON') == {1, 3}
    assert idx.search_all('nothing') == set()
    assert idx.top_words(2) == [('a', 5), ('is', 3)]

    assert idx.search_ranked('hash table python') == [2, 1, 3]
    assert idx.search_ranked('python', limit=1) == [1]
    assert idx.search_ranked('nothing here') == []
    assert idx.search_ranked('') == []

    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()
    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}

    assert 'python' not in idx._index and 'language' not in idx._index
    assert 'python' not in dict(idx.top_words(100))
    assert idx.search_all() == set() and idx.search_any() == set()
    idx.remove(100)

    result = idx.search_all('hash')
    result.add(999)
    assert idx.search_all('hash') == {2}

    assert idx.search_all('table.') == {2}
    assert idx.search_any('new text') == {3}
    assert idx.search_all('...') == set()
    assert idx.top_words(0) == [] and idx.top_words(-1) == []

    idx.add(5, 'version 1')
    assert idx.search_all(1) == {5}
    idx.remove(5)

    idx.remove(2)
    idx.remove(3)
    assert idx._index == {} and idx.top_words(5) == []
    print('все проверки прошли')
