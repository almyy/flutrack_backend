# Flutrack backend
This system is a part of a master's thesis at NTNU, done by Martin Almvik and Mikael Rino Solstad. The thesis was delivered 6th of June, 2016.

## Purpose
The goal is to create an open-source web application (angularJS frontend and Django backend), available for everyone, that will predict where and when the flu will spread through air traffic, and visualize this over a time period.
It uses tweets gathered from [Flutrack.org](http://www.flutrack.org) for detecting influenza incidences, which the prediction is built upon. Visit their project on [GitHub](https://github.com/flutrack/Twitter_module-Flutrack.org-source-code-).

Furthermore, the system will use flight traffic data from [BTS](http://www.transtats.bts.gov/databaseinfo.asp?DB_ID=111), and an algorithm to calculate the risk of infection in cities connected via air traffic. The algorithm is created by Rvachev and Longini in 1985, and our results correlates with the results they have found.

## The API
The API is hosted at flutrack-backend.herokuapp.com, and has two publicly available endpoints:

|Endpoint       |Description|
|---------------|-----------|
|GET /tweets    |Returns every influenza related tweet. The tweets are directly piped from [Flutrack.org](http://www.flutrack.org)|
|GET /prediction|Returns a list of an entire pandemic forecast, where each element represents one day in the forecast. Each day is represented as a list of all the cities included in the forecast with their respective morbidity and location.|

## Front-end
As a visualized interface to this API, we have created a simple single-page front-end. It's hosted at [flutrack.almyy.xyz](http://flutrack.almyy.xyz), and the open-source project can be found at [GitHub](https://github.com/almyy/flutrack_frontend).

## Installation
The system is based on Python and Django, as well as some third party libraries. The steps required to install and reproduce our results is listed below.

### Cloning the project
The main source of the system is this Git repository, and everyone is free to use this project as sees fit. The project can be cloned or forked by the use of [Git](https://git-scm.com/), using these commands:

```
git clone https://github.com/almyy/flutrack_backend.git
```
or
```
git clone https://github.com/almyy/flutrack_backend.git
```

### MongoDB
The system uses MongoDB as datastore, and in order to test the API locally, you need MongoDB, which can be downloaded from [here](https://www.mongodb.org/). 

### Python and pip
We have used Python 3.5.1, but should work on all installations over version 3.0. Install Python from [here](https://www.python.org/downloads/). This download also includes pip, which we will use to install third party libraries.

After you have downloaded Python and the project, you can navigate into the project directory, and install the following required libraries using pip:

```
pip install django djangorestframework tweepy requests pymongo xlrd
```

Django and Django Rest Framework are used to setup the API, Tweepy is used for utilizing the Twitter API, Requests makes it easier to make HTTP requests, Pymongo is used to communicate with our MongoDB instance, and xlrd is used to read .xls-files.

## Running the API
Now that you have everything installed, you should be able to run a local instance of the API. First you need to populate the database with data, so that it has some data to calculate. This can be done by running the setup.py script. In the project root folder, run the following command:

```
python setup.py
```

This step may take a while.
This will populate the database with the required cities, as well as some updated tweets from the Flutrack API. The script also sets an environment variable called SECRET_KEY, which Django uses for key generation. If you ever want to deploy the API to a production server, this key should be changed and hidden.

When the database is populated and the secret key is set, the API is ready to be run. You can run the following command to start the API locally:

```
python manage.py runserver
```

This hosts the API locally on localhost:8000, and can be browsed using e.g. [Postman](https://www.getpostman.com/). When running locally, the API also serves a browsable version through browsers, so you can visit the API in any browser.

Example request: GET localhost:8000/prediction