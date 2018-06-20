****************************
FogLAMP South OpenWeatherMap
****************************

This directory contains a South service plugin that fetches weather report from
OpenWeatherMap API on a regular (configured default to x seconds) interval.



**Known issues:**

- For now this debian works with default configuration, it does not work if the Admin API config gets:

      1. host, port, https scheme changes

      2. authentication as mandatory
