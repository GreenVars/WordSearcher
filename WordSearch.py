# http://puzzlemaker.discoveryeducation.com/WordSearchSetupForm.asp
__author__ = 'Sam'
from bisect import bisect_left


def bi_contains(lst, item):
    if len(lst) == 0:
        return False
    return (item <= lst[-1]) and (lst[bisect_left(lst, item)] == item)

def fuzzy_contains(text, words):
    if type(text == list) or type(text == tuple):
        text = ''.join(text)
    elif not type(text == str):
        raise TypeError("Key: {} is type: {}".format(
            text, type(text)))
    possible = '' # return longest word
    words.sort(key=len)
    for word in words:
        if len(word) > len(text):
            continue
        elif text[0:len(word)] == word:
            possible = word
    return possible

class WordSearch(object):
    def __init__(self, puzzle=(), words=(), file_path=""):
        self.puzzle = puzzle
        self.words = words
        self.file_path = file_path
        if file_path:
            with open(file_path, 'r') as puzzle_info:
                lines = puzzle_info.readlines()
                words_to_add = []
                for index, line in enumerate(lines):
                    if line == "\n":  # Empty Line represents start of puzzle
                        break
                    else:
                        words_to_add.append(line.strip())
                else:
                    raise Exception("Word Search not found in {}".format(file_path))
                self.words = tuple(words_to_add)
                self.puzzle = lines[index + 1:]  # puzzle is every line after answers
        self.clean_puzzle()
        self.max_word = len(max(self.words, key=len))
        self.min_word = len(min(self.words, key=len))
        self.solutions = []
        self.word_pairs = []
        for word in self.words:
            if len(word) >= 3:
                if not bi_contains(self.word_pairs, word[0:2]):
                    self.word_pairs.append(word[0:2])

    def clean_puzzle(self):
        self.puzzle = [''.join(line.split()).strip() for line in self.puzzle]

    def get_column(self, index, length, start=0, backwards=1):
        chars = []
        for i in range(length):
            try:
                chars.append(self[index, start + (i * backwards)])
            except IndexError:
                break
        return chars

    def get_row(self, index, length, start=0, backwards=1):
        chars = []
        for i in range(length):
            try:
                chars.append(self[start + (i * backwards), index])
            except IndexError:
                break
        return chars

    def get_diagonal(self, x, y, length, horizontal=1, vertical=1):
        """
        :param x: Starting x (column) coordinate
        :param y: Starting y (row) coordinate
        :param length: How many letters get in diagonal
        :param horizontal: Indicates whether x moves in positive or negative direction
        :param vertical: Indicates whether y moves in positive or negative direction
        :return: list of characters in diagonal
        """
        chars = []
        for i in range(length):
            try:
                chars.append(self[x + (i * horizontal), y + (i * vertical)])
            except IndexError:
                break
        return chars

    def neighbors(self, x, y):
        chars = []
        i = 0  # Index of delta cords
        for delta_x in range(-1, 2):
            for delta_y in range(-1, 2):
                if delta_x == 0 and delta_y == 0:  # Not include character in neighbors
                    continue
                try:
                    chars.append((self[(x + delta_x, y + delta_y)], i))
                except IndexError:
                    pass
                i += 1
        return chars

    def find_words(self):
        c = []
        for y in range(len(w.puzzle)):
            for x in range(len(w.puzzle[0])):
                neighbors = w.neighbors(x, y)
                for char, index in neighbors:
                    pair = w[x, y] + char
                    if bi_contains(self.word_pairs, pair):

                        if index == 0:  # Diagonal - -
                            text = self.get_diagonal(x, y, self.max_word, horizontal=-1, vertical=-1)
                        elif index == 1:  # Horizontal -
                            text = self.get_row(y, self.max_word, start=x, backwards=-1)
                        elif index == 2:  # Diagonal - +
                            text = self.get_diagonal(x, y, self.max_word, horizontal=-1, vertical=1)
                        elif index == 3:  # Vertical -
                            text = self.get_column(x, self.max_word, start=y, backwards=-1)
                        elif index == 4:  # Vertical +
                            text = self.get_column(x, self.max_word, start=y)
                        elif index == 5:  # Diagonal + -
                            text = self.get_diagonal(x, y, self.max_word, horizontal=1, vertical=-1)
                        elif index == 6:  # Horizontal +
                            text = self.get_row(y, self.max_word, start=x, backwards=1)
                        elif index == 7:  # Diagonal + +
                            text = self.get_diagonal(x, y, self.max_word, horizontal=1, vertical=1)

                        found_word = fuzzy_contains(text, self.words_with_pair(pair))
                        if found_word:
                            self.solutions.append((x, y, index, found_word))

    def write_solution(self):
        index_to_direction = ("Diagonal , Direction: Up, Left",
                              "Horizontal: Left",
                              "Diagonal , Directions: Down, Left",
                              "Vertical: Up",
                              "Vertical: Down",
                              "Diagonal , Direction: Up, Right",
                              "Horizontal: Right",
                              "Diagonal , Direction: Down, Right")
        if self.solutions:
            with open(self.file_path.split('.')[0] + "Solution.txt", 'w') as sol:
                sol.write(str(self) + '\n\n')
                self.solutions.sort(key=lambda x: x[-1]) # Sort by found word
                for solution in self.solutions:
                    sol.write("{word} at ({x} , {y}) going {d}\n".format(
                                                                word=solution[3],
                                                                x=solution[0],
                                                                y=solution[1],
                                                                d=index_to_direction[solution[2]]))

    def words_with_pair(self, pair):
        return [word for word in self.words if word[0:2] == pair]

    def __iter__(self):
        for line in self.puzzle:
            yield line

    def __getitem__(self, item):
        if (not isinstance(item, tuple)) or \
                any(i >= len(self.puzzle) or i < 0 for i in item):
            raise IndexError("Key {} of type: {} could not access puzzle"
                             .format(item, type(item)))
        x, y = item
        return self.puzzle[y][x]

    def __str__(self):
        return '\n'.join([' '.join(list(line)) for line in self])

    def change_word_list(self, words):
        self.words = words
        self.max_word = len(max(self.words, key=len))
        self.min_word = len(min(self.words, key=len))
        self.word_pairs = []
        for word in self.words:
            if len(word) >= 3:
                if not bi_contains(self.word_pairs, word[0:2]):
                    self.word_pairs.append(word[0:2])

if __name__ == '__main__':
    w = WordSearch(file_path="Puzzles/ComputerSearch.txt")
    with open("possible_words.txt") as f:
        words = f.readlines()
        words = [word.strip() for word in words if len(word) > 3]
    w.change_word_list(words)
    w.find_words()
    w.write_solution()