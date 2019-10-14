import os
import re
import numpy as np

HTTP_RE = re.compile(r"START[\n]-{10}[\n](.*?)[\n]-{10}[\n]END", re.MULTILINE | re.DOTALL)


def parse_http(data):
    return HTTP_RE.findall(data)


def get_requests_from_file(path):
    with open(path, 'r') as requests_file:
        requests_data = requests_file.read()
    return parse_http(data=requests_data)


def batch_generator(inputs, lens, num_epochs, batch_size, vocab):
    i = 0
    input_size = len(inputs)
    for j in range(num_epochs):
        while i + batch_size <= input_size:
            length = lens[i:i + batch_size]
            padded = batch_padding(inputs=inputs[i:i + batch_size], lens=length, vocab=vocab)
            yield padded, length
            i += batch_size
        i = 0


def single_generator(inputs, lens):
    for i in range(len(inputs)):
        yield [inputs[i]], lens[i]


def batch_padding(inputs, lens, vocab):
    max_len = np.max(lens)
    padded = []
    for sample in inputs:
        padded.append(sample + ([vocab.vocab['<PAD>']] * (max_len - len(sample))))
    return padded


def print_progress(step, epoch, loss, step_loss, time):
    print("Step %d (epoch %d), average_train_loss = %.5f, step_loss = %.5f, time_per_step = %.3f" % (
     step, epoch, loss, step_loss, time))


def create_checkpoints_dir(checkpoints_dir):
    if not os.path.exists(checkpoints_dir):
        os.makedirs(checkpoints_dir)
