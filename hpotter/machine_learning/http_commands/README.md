# HTTP Command Anomaly Detection
A machine learning algorithm that detects and highlights anomalous HTTP requests. 
 
## Training Datasets
The model is set to train over 40 epochs or until a minimum average training loss lower than 0.35 is 
achieved. The training data is held in the `hpotter/machine_learning/http_commands/data.tar.gz` file.
To extract the data directory, do:

    tar -xzvf hpotter/machine_learning/http_commands/data.tar.gz -C hpotter/machine_learning/http_commands/
    
Train, test and validation split is created from 310,000 benign samples from the `hpotter/machine_learning/http_commands/data/benign_requests.txt`
file and 15,402 anomalous samples from the `anomalous_requests.txt` file in the same directory.

<!---[![Build Status](https://travis-ci.org/drsjb80/HPotter.svg?branch=master)](https://travis-ci.org/drsjb80/HPotter)---> 
## Training and Predictions
To ensure the necessary packages are installed, do:

    pip3 install -r requirements.txt 
 
To train the machine learning algorithm itself, do:

    python3 -m hpotter.machine_learning.http_commands.learn

To make predictions using the saved model and weights after training, do:

    python3 -m hpotter.machine_learning.http_commands.predict

## Model
The algorithm used to classify anomalous HTTP commands is a Long Short Term Memory (LSTM) Recurrent Neural Network 
(RNN) that uses a sequence to sequence encoder/decoder of character embeddings. Each character is encoded into an 
integer value then fed into the algorithm, where it attempts to predict/reproduce the input and anything that
does not match is then considered an anomaly. Below demonstrates a high level architecture of the algorithm:

![Screen Shot 2019-09-23 at 11 49 45 AM](https://user-images.githubusercontent.com/32188816/65449483-52a9d300-ddf8-11e9-8af0-4d2840a9e167.png)
 
Once the machine learning algorithm is trained and predictions are made, `hpotter/machine_learning/http_commands/anomaly_report.html`
will be generated which contains the HTTP requests detected as anomalies. The text in this file enumerates 
each malicious HTTP request and the associated characters that contributed to the anomalous prediction highlighted in 
red, as shown below.
  
![Screen Shot 2019-10-05 at 11 56 55 AM](https://user-images.githubusercontent.com/32188816/66258858-5548e880-e767-11e9-8493-e09e0a500fdb.png)
  
## Saved Model
Checkpoints of the model's training progress are saved if adjustments need to be made or for future training/prediction
 purposes. These checkpoints are stored in the `hpotter/machine_learning/http_commands/checkpoints` directory.
