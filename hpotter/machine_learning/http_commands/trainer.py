import timeit

import numpy as np
import tensorflow as tf
from hpotter.machine_learning.http_commands.helpers.helper import print_progress, create_checkpoints_dir
from hpotter.machine_learning.http_commands.helpers.vocab import Vocabulary
from hpotter.machine_learning.http_commands.helpers.reader import Data
from hpotter.machine_learning.http_commands.model import Model


class Trainer:
    def __init__(self, batch_size, checkpoints_path, dropout):
        self.batch_size = batch_size
        self.checkpoints_path = checkpoints_path
        self.path_to_graph = checkpoints_path + 'rnn'
        self.dropout = dropout

    def train(self, model, training_data, training_data_size, num_steps, num_epochs, min_loss=0.3):
        tf.set_random_seed(1234)
        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())
            total_loss = []
            timings = []
            steps_per_epoch = int(training_data_size/self.batch_size)
            num_epoch = 1

            for step in range(1, num_steps):
                beg_t = timeit.default_timer()
                X, L = training_data.next()
                seq_len = np.max(L)
                feed_dict = {
                    model.inputs: X,
                    model.targets: X,
                    model.lens: L,
                    model.dropout: self.dropout,
                    model.batch_size: self.batch_size,
                    model.max_seq_len: seq_len
                }
                fetches = [model.loss, model.decoder_outputs, model.train_optimizer]
                step_loss, _, _ = sess.run(fetches=fetches, feed_dict=feed_dict)
                total_loss.append(step_loss)
                timings.append(timeit.default_timer() - beg_t)

                if step % steps_per_epoch == 0:
                    num_epoch += 1

                if step % 200 == 0 or step == 1:
                    print_progress(int(step/200), num_epoch, np.mean(total_loss),
                                   np.mean(step_loss), np.sum(timings))
                    timings = []
                if step == 1:
                    _ = tf.train.export_meta_graph(filename=self.path_to_graph + '.meta')
                if np.mean(total_loss) < min_loss or num_epoch > num_epochs:
                    model.saver.save(sess, self.path_to_graph, global_step=step)
                    print("=" * 25 + "\r\n Training is complete!!!\r\n" + "=" * 25 + "\r\n")
                    break


create_checkpoints_dir("./checkpoints")
d = Data('hpotter/machine_learning/http_commands/datasets/benign_requests.txt')
rnn = Model(num_layers=2, hidden_size=64, vocab=Vocabulary(), embedding_size=64)
trainer = Trainer(batch_size=128, checkpoints_path='./checkpoints', dropout=0.7)
steps = 10 ** 6
epochs = 60
train_gen = d.train_gen(batch_size=128, num_epochs=epochs)
train_size = d.train_size
trainer.train(model=rnn, training_data=train_gen, training_data_size=train_size,
              num_steps=steps, num_epochs=epochs)
