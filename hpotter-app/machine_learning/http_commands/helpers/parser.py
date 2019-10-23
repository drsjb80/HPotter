import random

from sklearn.model_selection import train_test_split

from machine_learning.http_commands.helpers.helper import get_requests_from_file, batch_generator, \
    single_generator
from machine_learning.http_commands.helpers.vocabulary import Vocabulary


class Reader(object):
    def __init__(self, path, vocab=Vocabulary()):
        self.vocab = vocab
        data = get_requests_from_file(path=path)
        print("Downloaded %d samples from %s" % (len(data), path))
        map_data = lambda i: [x[i] for x in map(self._process_requests, data)]
        self.data = map_data(0)
        self.lens = map_data(1)
        assert len(self.data) == len(self.lens)

    def _process_requests(self, request):
        sequence = self.vocab.string_to_int(text=request)
        sequence_len = len(sequence)
        return sequence, sequence_len


class Data(Reader):
    def __init__(self, path, vocab=Vocabulary(), predict=False):
        super(Data, self).__init__(path, vocab)

        if not predict:
            self._train_test_split()

    def _train_test_split(self):
        data, lens = self._shuffle(self.data, self.lens)
        X_train, X_test, y_train, y_test = train_test_split(data, lens, test_size=0.1)
        X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.2)
        self.X_train, self.y_train = X_train, y_train
        self.X_test, self.y_test = X_test, y_test
        self.X_val, self.y_val = X_val, y_val
        self.train_size = len(X_train)
        self.test_size = len(X_test)
        self.val_size = len(X_val)

    def _shuffle(self, data, lens):
        temp = list(zip(data, lens))
        random.shuffle(temp)
        data, lens = zip(*temp)
        return data, lens

    def train_gen(self, batch_size, num_epochs):
        return batch_generator(inputs=self.X_train, lens=self.y_train, num_epochs=num_epochs,
                               batch_size=batch_size, vocab=self.vocab)

    def validation_gen(self):
        return single_generator(inputs=self.X_val, lens=self.y_val)

    def predict_gen(self):
        return single_generator(inputs=self.data, lens=self.lens)

    def test_gen(self):
        return single_generator(inputs=self.X_test, lens=self.y_test)
