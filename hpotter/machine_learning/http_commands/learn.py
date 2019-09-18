from hpotter.machine_learning.http_commands.helpers.helper import create_checkpoints_dir
from hpotter.machine_learning.http_commands.helpers.parser import Data
from hpotter.machine_learning.http_commands.helpers.vocabulary import Vocabulary
from hpotter.machine_learning.http_commands.model import Model
from hpotter.machine_learning.http_commands.trainer import Trainer
BASE_PATH = 'hpotter/machine_learning/http_commands/'

create_checkpoints_dir(BASE_PATH + "checkpoints/")
d = Data(path=BASE_PATH + 'data/benign_requests.txt')
rnn = Model(num_layers=2, hidden_size=64, vocab=Vocabulary(), embedding_size=64)
trainer = Trainer(batch_size=128, checkpoints_path=BASE_PATH + 'checkpoints/', dropout=0.7)
steps = 10 ** 6
epochs = 100
train_gen = d.train_gen(batch_size=128, num_epochs=epochs)
train_size = d.train_size
trainer.train(model=rnn, training_data=train_gen, training_data_size=train_size,
              num_steps=steps, num_epochs=epochs)

import numpy as np

from hpotter.machine_learning.http_commands.helpers.parser import Data
from hpotter.machine_learning.http_commands.helpers.vocabulary import Vocabulary
# from hpotter.machine_learning.http_commands.learn import BASE_PATH
from hpotter.machine_learning.http_commands.predictor import Predictor

d = Data(path=BASE_PATH + 'data/benign_requests.txt')
predictor = Predictor(checkpoint_path=BASE_PATH + "checkpoints/", std_factor=6.0, vocab=Vocabulary())
value_generator = d.validation_gen()
predictor.set_threshold(data_generator=value_generator)

test_generator = d.test_gen()
valid_predictions, valid_losses = predictor.predict(data_generator=test_generator)
fps = np.sum(valid_predictions)
num_samples = len(valid_predictions)
print("\r\nNumber of False Positives: ", fps)
print("Number of Samples: ", num_samples)
print("False Positive Rate: ", (fps / num_samples))

predicted_data = Data(path=BASE_PATH + 'data/anomalous_requests.txt', predict=True)
predicted_generator = predicted_data.predict_gen()
anomalous_predictions, anomaly_losses = predictor.predict(data_generator=predicted_generator)
tps = np.sum(anomalous_predictions)
num_samples = len(anomalous_predictions)
print("\r\nNumber of True Positives: ", tps)
print("Number of Samples: ", num_samples)
print("True Positive Rate: ", (tps / num_samples))
