from hpotter.machine_learning.http_commands.helpers.helper import create_checkpoints_dir
from hpotter.machine_learning.http_commands.helpers.parser import Data
from hpotter.machine_learning.http_commands.helpers.vocabulary import Vocabulary
from hpotter.machine_learning.http_commands.model import Model, BASE_PATH
from hpotter.machine_learning.http_commands.trainer import Trainer

create_checkpoints_dir(BASE_PATH + "checkpoints/")
d = Data(path=BASE_PATH + 'data/benign_requests.txt')
rnn = Model(num_layers=2, hidden_size=64, vocab=Vocabulary(), embedding_size=64)
trainer = Trainer(batch_size=128, checkpoints_path=BASE_PATH + 'checkpoints/', dropout=0.7)
steps = 10 ** 6
epochs = 40
train_gen = d.train_gen(batch_size=128, num_epochs=epochs)
train_size = d.train_size
trainer.train(model=rnn, training_data=train_gen, training_data_size=train_size,
              num_steps=steps, num_epochs=epochs)
