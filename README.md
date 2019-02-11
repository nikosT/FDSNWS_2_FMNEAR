# FDSNWS_2_FMNEAR
FDSN Web Services integrated with Automatic Moment Tensor calculation

The Python code (check.py) requests near real-time Events through the FDSNWS-event for a particular time window specified in the configuration file. The periodical check is performed via a Linux Cron Job. For all of the events returned by the FDSNWS-event, the Python code (extract.py) is triggered for each one of them, sequentially. The current implementation passes the event's datetime stamp as input argument to the Python code.


The Python code (extract.py) checks if the specific event that was passed as input argument is already (or being) calculated. The current implementation of the Python code will only trigger new events that were not processed before.
