# Fixes
* planet.physics.uiowa.edu does not work

# Add option for https://github.com/Brightcells/pngquant

# Code improvements
* Return error if keywords not in allowed list are given.
* Test validity of options in config.py
* Catch un-caught errors and display error.
* Option for self-test of error image and regular image on startup.

# Features
* Add examples based on all.txt
* Add intermediate page as ViViz is set up and allow no id to be specified. See misc/vivizlog.
* Test option for format=plotly for interactive plots.

# Logging
* Have hapi() and hapiplot() have log lines showing pid and date/time.
* Log to file option; consider using standard logging library.
