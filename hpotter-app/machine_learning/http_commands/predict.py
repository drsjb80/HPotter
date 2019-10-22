import numpy as np

from machine_learning.http_commands.helpers.parser import Data
from machine_learning.http_commands.helpers.vocabulary import Vocabulary
from machine_learning.http_commands.model import BASE_PATH
from machine_learning.http_commands.predictor import Predictor

data = Data(path=BASE_PATH + 'data/benign_requests.txt')
predictor = Predictor(checkpoint_path=BASE_PATH + "checkpoints/", std_factor=25.0, vocab=Vocabulary())
validation_generator = data.validation_gen()
predictor.set_threshold(data_generator=validation_generator)

test_generator = data.test_gen()
valid_predictions, valid_losses = predictor.predict(data_generator=test_generator, visual=False)
fps = np.sum(valid_predictions)
num_samples = len(valid_predictions)
print("\r\nNumber of False Positives: ", fps)
print("Number of Samples: ", num_samples)
print("False Positive Rate: ", (fps / num_samples))
print("Test Accuracy: %.6f%%" % (fps / num_samples))

predicted_data = Data(path=BASE_PATH + 'data/anomalous_requests.txt')
predicted_generator = predicted_data.predict_gen()
predictor.write_header()
anomalous_predictions, anomaly_losses = predictor.predict(data_generator=predicted_generator)
tps = np.sum(anomalous_predictions)
num_samples = len(anomalous_predictions)
print("\r\nNumber of True Positives: ", tps)
print("Number of Samples: ", num_samples)
print("True Positive Rate: ", (tps / num_samples))
print("Prediction Accuracy: %.6f%%" % (tps / num_samples))
