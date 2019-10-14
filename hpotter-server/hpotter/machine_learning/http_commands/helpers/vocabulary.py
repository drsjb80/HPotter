import json
import os


class Vocabulary:
    def __init__(self):
        self.vocab_file = os.path.dirname(os.path.abspath(__file__)) + "/vocab.json"
        with open(self.vocab_file, 'r') as vocab_file:
            self.vocab = json.load(vocab_file)
        self.reverse_vocab = {v: k for k, v in self.vocab.items()}

    def string_to_int(self, text):
        try:
            if "b'" in text:
                text = text.decode('utf-8')
            chars = list(text)
        except Exception as err:
            chars = ['<UNK>']

        chars.append('<EOS>')
        char_ids = [self.vocab.get(char, self.vocab['<UNK>']) for char in chars]
        return char_ids

    def int_to_string(self, char_ids):
        characters = []
        for i in char_ids:
            characters.append(self.reverse_vocab[i])
        return characters
