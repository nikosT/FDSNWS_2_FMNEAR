#!/usr/bin/env python

import logging
import os, os.path, shutil, sys
from obspy.clients.fdsn.client import Client
from obspy.core import UTCDateTime

import config as cfg # local lib

# create check window
# get current UTC time
endtime=UTCDateTime.now()

starttime=endtime-cfg.check_time # sec

# prepare the log file
# location is based according to configuration
logging.basicConfig(filename=cfg.logfile, level=logging.INFO, format='%(asctime)s %(message)s\n')

try:
    logging.info("Connecting to FDSN Server:  " + cfg.fdsnws_url+"...")
    fdsn = Client(cfg.fdsnws_url)

    # get the first event
    logging.info('Checking for timespan: ' + str(starttime) + ' - ' + str(endtime))
    catalog=fdsn.get_events(starttime=starttime, 
                          endtime=endtime, 
                          minmagnitude=cfg.mag_thres,
                          magnitudetype="MLh",
                          includeallorigins=False,
                          includeallmagnitudes=False,
                          includearrivals=True,
                          orderby="time-asc",
                          limit=cfg.event_limit)

    # for every event that is found, call the process
    for event in catalog:
        logging.info(str(event))

        # call the python code
        os.system("python " + cfg.extract + " " + str(event.origins[0].time))
        # get event datetime
        # cut off microseconds
       # date=UTCDateTime(str(event.origins[0].time).partition(".")[0])
        # create working dir folder respective to the event datetime
       # working_dir=os.path.join(cfg.output_dir, date.strftime("%Y%m%d%H%M%S"))

      #  if os.path.exists(working_dir): 
      #      logging.info("Invoking the next process...")



except Exception as e:
    if e.__class__.__name__=="FDSNNoDataException":
        logging.info('No event is found...')

    else:
        logging.exception('Exception Raised')


