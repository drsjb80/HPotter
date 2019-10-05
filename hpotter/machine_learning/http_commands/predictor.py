import numpy as np
import tensorflow as tf


tf.logging.set_verbosity(tf.logging.FATAL)


class Predictor:
    def __init__(self, checkpoint_path, std_factor, vocab):
        self.thresh = 0.0
        self.checkpoints_path = checkpoint_path
        self.graph_path = checkpoint_path + 'rnn_checkpoint'
        self.std_factor = std_factor
        self.vocab = vocab
        self.__load()

    def __load(self):
        try:
            tf.reset_default_graph()
            loaded_graph = tf.Graph()
            with loaded_graph.as_default():
                saver = tf.train.import_meta_graph(self.graph_path + '.meta')
            self.sess = tf.Session(graph=loaded_graph)
            saver.restore(self.sess, tf.train.latest_checkpoint(self.checkpoints_path))
            self.inputs = loaded_graph.get_tensor_by_name('inputs:0')
            self.targets = loaded_graph.get_tensor_by_name('targets:0')
            self.lens = loaded_graph.get_tensor_by_name('lens:0')
            self.dropout = loaded_graph.get_tensor_by_name('dropout:0')
            self.batch_size_tensor = loaded_graph.get_tensor_by_name('batch_size:0')
            self.seq_len_tensor = loaded_graph.get_tensor_by_name('max_seq_len:0')
            self.batch_loss = loaded_graph.get_tensor_by_name('batch_loss:0')
            self.probabilities = loaded_graph.get_tensor_by_name('probs:0')
            self.logits = loaded_graph.get_tensor_by_name('logits:0')
        except Exception as err:
            raise ValueError("Unable To Create Model: %s" % err)

    def set_threshold(self, data_generator):
        total_loss = []
        for seq, loss in data_generator:
            batch_loss, _ = self._predict_for_request(X=seq, loss=loss)
            total_loss.extend(batch_loss)
        mean = np.mean(total_loss)
        std = np.std(total_loss)
        self.thresh = mean + (self.std_factor * std)
        print('\r\n\r\nValidation Loss Mean: ', mean)
        print('Validation Loss Std: ', std)
        print('Anomaly Detection Threshold: ', self.thresh)
        return self.thresh

    def predict(self, data_generator, visual=True, num_to_display=100):
        losses = []
        preds = []
        num_displayed = 0

        for seq, loss in data_generator:
            batch_loss, alphas = self._predict_for_request(X=seq, loss=loss)
            losses.extend(batch_loss)
            alphas = self._process_alphas(X=seq, alphas=alphas, batch_size=1)
            mask = np.array([l >= self.thresh for l in batch_loss])
            pred = mask.astype(int)
            preds.extend(pred)

            if visual and num_displayed < num_to_display and pred == [1]:
                print('\r\n\r\nPrediction: ', pred[0])
                print('\r\nLoss: ', batch_loss[0])
                num_displayed += 1
                self._visualize(alphas=alphas, X=seq)
        return preds, losses

    def write_header(self):
        title = 'Detected HTTP Anomalies'
        title_wrapper = self._html_tag('title')
        heading_wrapper = self._html_tag('h1')
        with open('hpotter/machine_learning/http_commands/anomaly_report.html', 'a+') as anomaly_report:
            anomaly_report.write(title_wrapper(title) + heading_wrapper(title))

    def _predict_for_request(self, X, loss):
        lens = [loss]
        max_seq_len = loss
        feed_dict = {
            self.inputs: X,
            self.targets: X,
            self.lens: lens,
            self.dropout: 1.0,
            self.batch_size_tensor: 1,
            self.seq_len_tensor: max_seq_len
        }
        fetches = [self.batch_loss, self.probabilities]
        batch_loss, alphas = self.sess.run(fetches=fetches, feed_dict=feed_dict)
        return batch_loss, alphas

    def _process_alphas(self, X, alphas, batch_size):
        processed_alphas = []
        for i in range(batch_size):
            probs = alphas[i]
            coefficients = np.array([probs[j][X[i][j]] for j in range(len(X[i]))])
            coefficients = coefficients / coefficients.max()
            processed_alphas.append(coefficients)
        return processed_alphas

    def _html_tag(self, tag):
        def _wrap_text(message=''):
            if 'span' in tag:
                return '<{0}>{1}</span>'.format(tag, message)
            elif tag != 'br':
                return '<{0}>{1}</{0}>\r\n'.format(tag, message)
            else:
                return '\r\n<%s>\r\n' % tag
        return _wrap_text

    def _visualize(self, alphas, X):
        color_wrapper = self._html_tag('span style="color:red"')
        newline_wrapper = self._html_tag('br')
        message = ''

        for i, x in enumerate(X):
            coefficients = alphas[i]
            tokens = self.vocab.int_to_string(x)

            for j in range(len(x)):
                token = tokens[j]
                if token == '\n':
                    message += newline_wrapper()
                if token != '<PAD>' and token != '<EOS>' and token != '<UNK>':
                    if coefficients[j] < 0.09:
                        message += color_wrapper(token)
                    else:
                        message += token
            message += newline_wrapper() * 2
        with open('hpotter/machine_learning/http_commands/anomaly_report.html', 'a+') as anomaly_report:
            anomaly_report.write(message)
