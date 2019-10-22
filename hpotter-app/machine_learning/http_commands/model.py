import numpy as np
import tensorflow as tf
tf.logging.set_verbosity(tf.logging.FATAL)
BASE_PATH = 'hpotter-app/'


class Model:
    def __init__(self, num_layers, hidden_size, vocab, embedding_size):
        tf.reset_default_graph()
        self.batch_size = tf.placeholder(tf.int32, [], name='batch_size')
        self.max_seq_len = tf.placeholder(tf.int32, [], name='max_seq_len')
        self.inputs = tf.placeholder(tf.int32, [None, None], name='inputs')
        self.targets = tf.placeholder(tf.int32, [None, None], name='targets')
        self.lens = tf.placeholder(tf.int32, [None, ], name='lens')
        self.dropout = tf.placeholder(tf.float32, name='dropout')
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.vocab = vocab
        self.adam_optimizer = tf.train.AdamOptimizer

        decoded_input = self._process_decoder_input(target_data=self.targets,
                                                    batch_size=tf.to_int32(self.batch_size))  # missing arg?
        vocab_size = len(self.vocab.vocab)
        embed_initializer = tf.random_uniform_initializer(-np.sqrt(3), np.sqrt(3))
        with tf.variable_scope('embedding'):
            embeds = tf.get_variable('embed_matrix', [vocab_size, embedding_size],
                                     initializer=embed_initializer, dtype=tf.float32)
            encoded_embed_input = tf.nn.embedding_lookup(embeds, self.inputs)

        encoded_state = self._encoder(encoded_embed_input=encoded_embed_input)

        with tf.variable_scope('embedding', reuse=True):
            decoded_embed_input = tf.nn.embedding_lookup(embeds, decoded_input)

        decoded_outputs = self._decoder(encoded_state=encoded_state, decoded_embed_input=decoded_embed_input)
        weight, bias = self._weight_and_bias(output_size=vocab_size)
        outputs = tf.reshape(decoded_outputs[0].rnn_output, [-1, self.hidden_size])
        logits = tf.matmul(outputs, weight) + bias
        logits = tf.reshape(logits, [-1, self.max_seq_len, vocab_size], name='logits')

        self.probs = tf.nn.softmax(logits=logits, name='probs')
        self.decoder_outputs = tf.argmax(logits, axis=2)
        self.cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=logits, labels=self.targets,
                                                                            name='cross_entropy')
        self.batch_loss = tf.identity(tf.reduce_mean(self.cross_entropy, axis=1), name='batch_loss')
        self.loss = tf.reduce_mean(self.cross_entropy)
        self.train_optimizer = self._optimizer(loss=self.loss)
        self.saver = tf.train.Saver()

    def _encoder(self, encoded_embed_input):
        cells = [self._lstm_cell(num_hidden_layers=self.hidden_size) for _ in range(self.num_layers)]
        multi_lstm = tf.contrib.rnn.MultiRNNCell(cells, state_is_tuple=True)

        _, encoded_state = tf.nn.dynamic_rnn(multi_lstm, encoded_embed_input, sequence_length=self.lens,
                                             swap_memory=True, dtype=tf.float32)
        return encoded_state

    def _decoder(self, encoded_state, decoded_embed_input):
        output_lengths = tf.ones([self.batch_size], tf.int32) * self.max_seq_len
        helper = tf.contrib.seq2seq.TrainingHelper(decoded_embed_input, output_lengths, time_major=False)
        cells = [self._lstm_cell(num_hidden_layers=self.hidden_size) for _ in range(self.num_layers)]
        decoded_cell = tf.contrib.rnn.MultiRNNCell(cells, state_is_tuple=True)
        decoder = tf.contrib.seq2seq.BasicDecoder(decoded_cell, helper, encoded_state)
        dec_outputs = tf.contrib.seq2seq.dynamic_decode(decoder, output_time_major=False,
                                                        impute_finished=True, maximum_iterations=self.max_seq_len,
                                                        swap_memory=True)
        return dec_outputs

    def _optimizer(self, loss):
        def _learning_rate_decay_fn(learning_rate, global_step):
            return tf.train.exponential_decay(learning_rate=learning_rate, global_step=global_step,
                                              decay_steps=10000, decay_rate=0.99)

        starting_learning_rate = 0.001
        starting_global_step = tf.Variable(0, trainable=False)
        optimizer = tf.contrib.layers.optimize_loss(loss=loss, global_step=starting_global_step,
                                                    learning_rate=starting_learning_rate,
                                                    optimizer=self.adam_optimizer,
                                                    learning_rate_decay_fn=lambda learning_rate, global_step:
                                                    _learning_rate_decay_fn(learning_rate=learning_rate,
                                                                            global_step=global_step),
                                                    clip_gradients=5.0)
        return optimizer

    def _process_decoder_input(self, target_data, batch_size):
        ending = tf.strided_slice(target_data, [0, 0], [batch_size, -1], [1, 1])
        decoded_input = tf.concat([tf.fill([batch_size, 1], self.vocab.vocab['<GO>']), ending], 1)
        return decoded_input

    def _lstm_cell(self, num_hidden_layers):
        cell = tf.contrib.rnn.LSTMCell(num_hidden_layers, initializer=tf.contrib.layers.xavier_initializer())
        cell = tf.contrib.rnn.DropoutWrapper(cell, output_keep_prob=self.dropout)
        return cell

    def _weight_and_bias(self, output_size):
        weight = tf.Variable(tf.truncated_normal([self.hidden_size, output_size], stddev=0.01))
        bias = tf.Variable(tf.constant(1.0, shape=[output_size]))
        return weight, bias
