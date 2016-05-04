# Flutrack backend
This system is a part of a master's thesis at NTNU, done by Martin Almvik and Mikael Rino Solstad. The thesis was delivered 6th of June, 2016.

## Purpose
The goal is to create an open-source web application (angularJS frontend and Django backend), available for everyone, that will predict where and when the flu will spread through air traffic, and visualize this over a time period.
It uses tweets gathered from [Flutrack.org](http://www.flutrack.org) for detecting influenza incidences, which the prediction is built upon. Visit their project on [github](https://github.com/flutrack/Twitter_module-Flutrack.org-source-code-).

Furthermore, the system will use flight traffic data from [BTS](http://www.transtats.bts.gov/databaseinfo.asp?DB_ID=111), and an algorithm to calculate the risk of infection in cities connected via air traffic. The algorithm is created by Rvachev and Longini in 1985, and our results correlates with the results they have found.

## The API
The API is hosted at flutrack-backend.herokuapp.com, and has two publicly available endpoints:

|Endpoint       |Description|
|---------------|-----------|
|GET /tweets    |Returns every influenza related tweet. The tweets are directly piped from [Flutrack.org](http://www.flutrack.org)|
|GET /prediction|Returns a list of an entire pandemic forecast, where each element represents one day in the forecast. Each day is represented as a list of all the cities included in the forecast with their respective morbidity and location.|

## Front-end
As a visualized interface to this API, we have created a simple single-page front-end. It's hosted at [flutrack.almyy.xyz], and the open-source project can be found at [GitHub](https://github.com/almyy/flutrack_frontend).

## Installation
Work in progress.