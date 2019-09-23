# HTTP Command Anomaly Detection
A machine learning algorithm that detects and highlights anomalous HTTP requests. 
 

<!---[![Build Status](https://travis-ci.org/drsjb80/HPotter.svg?branch=master)](https://travis-ci.org/drsjb80/HPotter)---> 
## Training and Predictions
To ensure the necessary packages are installed, do:

    pip3 install -r requirements.txt 
 
To train the machine learning algorithm itself, do:

    python3 -m hpotter.machine_learning.http_commands.learn

To make predictions using a saved model checkpoint after training, do:

    python3 -m hpotter.machine_learning.http_commands.predict

## Model Definition
The algorithm used to classify anomalous HTTP commands is a Long Short Term Memory (LSTM) Recurrent Neural Network 
(RNN) that uses a sequence to sequence encoder/decoder of character embeddings. Each character is encoded into an 
integer value then fed into the algorithm, where it attempts to predict/reproduce the input and anything that
does not match is then considered an anomaly. Below demonstrates a high level architecture of the algorithm:

![Screen Shot 2019-09-23 at 11 49 45 AM](https://user-images.githubusercontent.com/32188816/65449483-52a9d300-ddf8-11e9-8af0-4d2840a9e167.png)
 
Once the machine learning algorithm is trained and predictions are made, text will be generated
that contains the HTTP requests that were detected as anomalies. This text highlights each malicious HTTP request
and the associated characters that contributed to the anomalous prediction highlighted in red, as shown below.
  
  
![Screen Shot 2019-09-23 at 11 46 52 AM](https://user-images.githubusercontent.com/32188816/65449319-f646b380-ddf7-11e9-9036-7ae2ff520b7e.png)

  
## Training Datasets
The model is set to train over 60 epochs or until a minimum average training loss of 0.20 or lower is 
achieved. It is trained on 30,000 benign samples from the `hpotter/machine_learning/http_commands/data/benign_requests.txt`
file and 15,402 anomalous samples from the `anomalous_requests.txt` file in the same directory.
  
## Saved Model Checkpoints
Training the model takes time, and as such it is important to save checkpoints in the model's training
process if adjustments need to be made. These checkpoints are stored in the `hpotter/machine_learning/http_commands/checkpoints`
directory are used to make predictions on future HTTP requests.
