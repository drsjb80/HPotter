import os
import numpy as np
import tensorflow as tf


class Model:
    def __init__(self, args):
        pass

    def _encoder(self, encoded_input):
        pass

    def _decoder(self, encoded_state, decoded_input):
        pass

    def _optimizer(self, loss):
        pass

    def _process_decoder_input(self, target_data, char_to_code, batch_size):
        pass

    def _lstm_cell(self, num_hidden_layers):
        pass

    def _weight_and_bias(self, input_size, output_size):
        pass
