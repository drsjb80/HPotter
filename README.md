<h1 align="center">
  <br>
  <img src="https://i.imgur.com/gNYWW8e.png" alt="Hpotter" width="200">
  <br>
  Hpotter
  <br>
</h1>

<h4 align="center">A clever threat analysis honeypot built leveraging machine learning.</h4>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#project-structure">Project Structure</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#credits">Credits</a> •
  <a href="#license">License</a>
</p>

## Features

* Gather data on attempted attacks from a variety of sources.
* Compatible with the Raspberry Pi
* A full dashboard for your data
* Utilize machine learning to analyze your data.

## Project Structure
The Hpotter project is divided into two portions. The core product which collects data, Hpotter-server, and a front end for viewing the data and analysing it, Hpotter-app. Hpotter-server is extremely lightweight and built to be deployable even on single-board computers like the Raspberry Pi. Meanwhile, Hpotter-app is built to be run on your home or work computer to work upon the data after collection. 


## How To Use

### Hpotter-server

To clone and run hpotter-server, you'll need [Git](https://git-scm.com) and [Python 3](https://www.python.org/) installed on your computer. From your command line:

```bash
# Clone this repository
$ git clone https://github.com/sheet-t/HPotter

# Navigate to Hpotter-server
$ cd hpotter-server

# Install Hpotter-server's dependencies
$ pip install -r requirements.txt

# On Windows, use
$ pip install -r winrequirements.txt

```

From there, you can run the Honeypot with:

```bash
# Run Hpotter-server
$ python3 -m hpotter

```

For more advanced details, see the included README.md file within hotter-server.

### Hpotter-app
To clone and run hpotter-app, you'll need [Git](https://git-scm.com) and [Node.js](https://nodejs.org/en/download/) installed on your computer. From your command line:

```bash
# Clone this repository
$ git clone https://github.com/sheet-t/HPotter

# Navigate to Hpotter-app
$ cd hpotter-app

# Install Hpotter-app's dependencies
$ npm install

# Run the app
$ npm start
```

## Credits

This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com.

## License

MIT
