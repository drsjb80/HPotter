import json

import numpy as np

from machine_learning.http_commands.helpers.parser import Data
from machine_learning.http_commands.helpers.vocabulary import Vocabulary
from machine_learning.http_commands.predictor import Predictor


def predict(json_file, num_samples):
    with open(json_file, 'r') as json_handle, \
         open('machine_learning/http_commands/data/samples.txt', 'a+') as text_handle:
        data = json.load(json_handle)
        start = 'START\r\n----------\r\n'
        end = '\r\n----------\r\nEND\r\n\r\n'
        try:
            for i, request_dict in enumerate(data['data']['requests']):
                if i < num_samples:
                    text_handle.write(start + request_dict['request'].strip() + end)
                else:
                    break
        except KeyError as err:
            raise Exception('Key Error, Expecting JSON in the Following Format: ' +
                            json.dumps({'data': {'requests': [{'id': 'id_goes_here', 'request': 'data_goes_here',
                                                               'requestType': 'Web/SQL/Shell'}]}}, indent=4))

    predictor = Predictor(checkpoint_path="machine_learning/http_commands/checkpoints/",
                          std_factor=25.0, vocab=Vocabulary())
    predicted_data = Data(path='machine_learning/http_commands/data/samples.txt')
    predicted_generator = predicted_data.predict_gen()
    anomalous_predictions, anomaly_losses = predictor.predict(data_generator=predicted_generator)
    tps = np.sum(anomalous_predictions)
    num_samples = len(anomalous_predictions)
    print("\r\nNumber of True Positives: ", tps)
    print("Number of Samples: ", num_samples)
    print("True Positive Rate: ", (tps / num_samples))
    print("Prediction Accuracy: %.6f%%" % (tps / num_samples))


predict(num_samples=3, json_file='dashboard/test.json')
