class Word:
    def __init__(self, word, certainty):
        self.word = word
        self.certainty = certainty

class Sentence:
    def __init__(self):
        self.words = []

    def add_word(self, word):
        if not isinstance(word, Word):
            raise ValueError("Input must be an instance of Word")
        self.words.append(word)

    def to_string(self, certainty_ranges):
        colored_words = []
        for word in self.words:
            color = self.get_color(word.certainty, certainty_ranges)
            colored_word = f"\033[{color}m{word.word}\033[0m"
            colored_words.append(colored_word)
        return ' '.join(colored_words)

    def get_color(self, certainty, certainty_ranges):
        for range_start, range_end, color_code in certainty_ranges:
            if range_start <= certainty <= range_end:
                return color_code
        return "0"  # Default color code
