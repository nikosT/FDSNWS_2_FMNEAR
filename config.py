#!/usr/bin/env python

############# Configuration #############

### EVENT TRIGGER ###
# FDSNWS service
fdsnws_url="http://10.0.0.23:8080"

# SDS archive
# if sds_url="" then the code
# uses the FDSNWS-dataselect
# for retrieving the waveforms
# otherwise through the SDS directory
# (sds is quicker, but script needs to run on
# the computer that contains the SDS)
# on the other hand, fdsnws seems slower
# but can be accessed remotely
# Use FDSNWS for waveforms retrieval
# sds_url=""
# Use SDS for waveforms retrieval
sds_url="archive"

# full path to log file
logfile="/home/user/fdsnws_scripts/FDSNWS_get_events.log"

# magnitude threshold
mag_thres=3.7

# Time interval for checking new events
# it can return more than 1 event
# it must match with the cron interval
check_time=600 # in sec

# max events to be handled per event check
# (per check_time min)
event_limit=5

# event time window based on origin time
timewindow_start=3*60 #sec
timewindow_end=9*60 #sec

### STATION INFO ###
minradius=0
maxradius=6 # degrees from the geographic point
# the maximum number of stations that can be used
maxstations=40
# remove unwanted channel types from picks
channel_type_exclude=['SH', 'BH', 'HN']
# remove unwanted stations from process
stations_exclude=['AIDA', 'DLFA', 'ACRB', 'ACRC', 'ACRD', 'ACRE', 'ACRF', \
                  'IACM', 'SAP1', 'SAP2', 'SAP4', 'EVGI', 'THR2', 'THR3', \
                  'THR5', 'THR6', 'THR7', 'THR8', 'THR9', 'AXS', 'SGD', \
                  'UPR', 'VTN', 'ACOR', 'ATHU', 'DESF', 'DIDY', 'FYTO', \
                  'LOUT', 'PSAR', 'PROD', 'RODI', 'SMIA', 'SNT2', 'SNT1', \
                  'SNT3', 'MALT', 'EIL']

# the output directory
output_dir="/home/user/MWFMNEAR/FMNEAR_classicgreens/working_directory"

# path to Python extract.py code
extract="/home/user/fdsnws_scripts/extract.py"

# path to core executable
calMWandFM_noa="/home/user/MWFMNEAR/FMNEAR_classicgreens/working_directory/calMwandFM_noa"

# path to results folder (where there results are copied to)
results_dir="/home/user/results"

######### end-of Configuration #########

