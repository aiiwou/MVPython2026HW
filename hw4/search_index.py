import re
from collections import Counter


class SearchIndex:
    """
    Инвертированный индекс для поиска слов в документах.

    _index хранит множества ID документов для каждого слова.
    _documents хранит частоты слов в каждом документе.
    _word_counts хранит общее количество вхождений каждого слова.

    Такая структура позволяет искать документы через индекс, а при
    удалении или замене документа обновлять только слова этого документа,
    не перебирая весь индекс или все остальные документы.
    """

    def __init__(self):
        self._index = {}
        self._documents = {}
        self._word_counts = Counter()

    @staticmethod
    def _tokenize(text):
        """Разбивает текст на слова в нижнем регистре."""
        return re.findall(r'\w+', text.lower())

    def add(self, doc_id, text):
        """Добавляет документ или заменяет существующий."""
        if doc_id in self._documents:
            self.remove(doc_id)

        words = Counter(self._tokenize(text))
        self._documents[doc_id] = words

        for word, count in words.items():
            if word not in self._index:
                self._index[word] = set()

            self._index[word].add(doc_id)
            self._word_counts[word] += count

    def search_all(self, *words):
        """Возвращает ID документов, содержащих все указанные слова."""
        words = self._tokenize(' '.join(words))

        if not words:
            return set()

        if any(word not in self._index for word in words):
            return set()
        words.sort(key=lambda word: len(self._index[word]))
        result = self._index[words[0]].copy()

        for word in words[1:]:
            result.intersection_update(self._index[word])

            if not result:
                break

        return result

    def search_any(self, *words):
        """Возвращает ID документов, содержащих хотя бы одно слово."""
        words = self._tokenize(' '.join(words))
        result = set()

        for word in words:
            result.update(self._index.get(word, set()))

        return result

    def remove(self, doc_id):
        """Удаляет документ и обновляет индекс."""
        if doc_id not in self._documents:
            return

        words = self._documents.pop(doc_id)

        for word, count in words.items():
            self._index[word].remove(doc_id)
            self._word_counts[word] -= count

            if not self._index[word]:
                del self._index[word]

            if self._word_counts[word] == 0:
                del self._word_counts[word]

    def top_words(self, n):
        """Возвращает n наиболее частых слов и количество их вхождений."""
        if n <= 0:
            return []

        return sorted(
            self._word_counts.items(),
            key=lambda item: (-item[1], item[0])
        )[:n]

    def search_ranked(self, query, limit=10):
        """
        Возвращает ID документов, отсортированных по релевантности.
        Релевантность — сумма вхождений слов запроса в документ.
        При равной релевантности первым идёт меньший ID документа.
        """
        words = self._tokenize(query)
        scores = {}

        for word in words:
            # Берём только документы, в которых есть текущее слово.
            for doc_id in self._index.get(word, set()):
                count = self._documents[doc_id][word]
                scores[doc_id] = scores.get(doc_id, 0) + count

        ranked = sorted(
            scores,
            key=lambda doc_id: (-scores[doc_id], doc_id)
        )

        return ranked[:max(0, limit)]


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

    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()

    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}

    idx = SearchIndex()
    idx.add(1, 'python python is great')
    idx.add(2, 'python is useful')
    idx.add(3, 'python python python')
    idx.add(4, 'java is great')

    assert idx.search_ranked('python great') == [1, 3, 2, 4]
    assert idx.search_ranked('python') == [3, 1, 2]
    assert idx.search_ranked('nothing') == []
    assert idx.search_ranked('python great', limit=2) == [1, 3]
    assert idx.search_ranked('python', limit=0) == []
    assert idx.search_ranked('python', limit=-1) == []
    assert idx.search_ranked('') == []

    print('Все проверки пройдены!')