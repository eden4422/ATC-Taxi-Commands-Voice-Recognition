class Word:
    def __init__(self, word, certainty):
        self.word = word
        self.certainty = certainty

class Sentence:
    def __init__(self):
        self.words = []
        self.certainty_ranges = []

    def __init__(self, certainty_ranges):
        self.words = []
        self.certainty_ranges = certainty_ranges

    def __init__(self, certainty_ranges, words):
        self.words = words
        self.certainty_ranges = certainty_ranges

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

# Example usage:
word1 = Word("Hello", 0.8)
word2 = Word("world", 0.5)
word3 = Word("Python", 0.9)

# Specify different certainty ranges and their corresponding colors
certainty_ranges = [(0.0, 0.4, "31"),  # Red for low certainty
                    (0.4, 0.7, "33"),  # Yellow for medium certainty
                    (0.7, 1.0, "32")]  # Green for high certainty

# Create a sentence object
sentence = Sentence()

# Add words to the sentence
sentence.add_word(word1)
sentence.add_word(word2)
sentence.add_word(word3)

# Get the colored representation of the sentence and print it
colored_sentence = sentence.to_string(certainty_ranges)
print(colored_sentence)