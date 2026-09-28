# Data Source & Authenticity

## Primary prototype source
Open-Meteo Historical Weather API:
https://open-meteo.com/en/docs/historical-weather-api

The API provides historical weather data from reanalysis datasets including ERA5.
The historical API supports hourly temperature, relative humidity, precipitation,
pressure and wind variables.

## Official India source
IMD Data Service Portal:
https://dsp.imdpune.gov.in/

IMD is the official India Meteorological Department source for historical
meteorological observation data. Access to some historical observation datasets
requires registration/procurement.

## Important distinction
Open-Meteo/ERA5 = genuine scientific reanalysis/model data.
IMD station observation = official Indian observational data.

They are NOT interchangeable. The application preserves provenance using
`source.name` and `source.dataset`.

## For Round 1
Use the real Open-Meteo/ERA5 data in this package for a reproducible working demo.
If the team obtains an IMD dataset, add it as a separate source and do not relabel
ERA5 values as IMD observations.
