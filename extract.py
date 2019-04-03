#!/usr/bin/env python

import logging
import os, os.path, shutil, sys
from obspy.clients.fdsn.client import Client
from obspy.clients.filesystem.sds import Client as Client_SDS
from obspy.core import UTCDateTime
from obspy import read
import tarfile

import config as cfg # local lib


if not len(sys.argv)==2:
    print "Usage: ./" + sys.argv[0] + ' <YYYY-MM-DDThh:mm:ss.ms>'
    sys.exit(0)

# get event datetime as first argument of the script
input=sys.argv[1]

# prepare the log file
# location is based according to configuration
logging.basicConfig(filename=cfg.logfile, level=logging.INFO, format='%(asctime)s %(message)s\n')

try:
    # get event datetime
    # cut off microseconds
    date=UTCDateTime(input.partition(".")[0])
    
    # create working dir folder respective to the event datetime
    working_dir=os.path.join(cfg.output_dir, date.strftime("%Y%m%d%H%M%S"))
    
    if os.path.exists(working_dir):
        logging.info("Working directory already exists, thus event ("+str(input)+") is already calculated! Exiting...")
    
    else:
        logging.info("Creating working directory ("+working_dir+")...")
        os.makedirs(working_dir)
    
        logging.info("Connecting to FDSN Server:  " + cfg.fdsnws_url+"...")
        fdsn = Client(cfg.fdsnws_url)

        if cfg.sds_url:
            logging.info("Connecting to SDS archive:  " + cfg.sds_url+"...")
            sds = Client_SDS(cfg.sds_url)
    
        logging.info("Retrieving event's info...")
    
        # get events info
        # catalog object is returned and
        # the first element -event object- is retrieved
        # get the event between 1 second from
        # the input event time
        # if two events occur between 1 second
        # it will just get the first one
        event=fdsn.get_events(starttime=date, 
                            #endtime=date+1, 
                            minmagnitude=cfg.mag_thres,
                            magnitudetype="MLh",
                            includeallorigins=False,
                            includeallmagnitudes=False,
                            includearrivals=True,
                            orderby="time-asc",
                            limit=1)[0]
    
        # the requested time window
        # of which start time is set 'timewindow_start' minutes before the Origin
        # and end time is set 'timewindow_end' minutes after the Origin
        starttime=event.origins[0].time-cfg.timewindow_start #sec
        endtime=event.origins[0].time+cfg.timewindow_end #sec

        # select those picks with stations
        # that have been not been excluded
        # picks/stations are sorted in ascending order of pick time
        picks=filter(lambda pick: not pick.waveform_id['station_code'] \
              in cfg.stations_exclude, event.picks)
        
        # select those picks with stations
        # that have been not been excluded
        # e.g not BH channel types
        for chan_type in cfg.channel_type_exclude:
            picks=filter(lambda pick: not pick.waveform_id['channel_code'][:2]==chan_type, picks)

        # and also the total number of stations
        # can reach no more that 40 stations
        picks=picks[:cfg.maxstations]

        # get all available waveforms with their responses attached
        # merged to a stream object
        # through SDS (if sds_url exist)
        if cfg.sds_url:
            logging.info("Requesting waveforms for the associated picks through SDS...")
            service=sds

        else:
            logging.info("Requesting waveforms for the associated picks through FDSNWS...")
            service=fdsn

        for i, pick in enumerate(picks):
            # get waveform data
            _st = service.get_waveforms(pick.waveform_id['network_code'],
                                        pick.waveform_id['station_code'],
                                        pick.waveform_id['location_code'] or '',
                                        pick.waveform_id['channel_code'][:2]+'?',
                                        starttime,
                                        endtime)

            # get station metadata
            _inv = fdsn.get_stations(starttime=starttime, 
                                     endtime=endtime, 
                                     network=pick.waveform_id['network_code'],
                                     station=pick.waveform_id['station_code'],
                                     location=pick.waveform_id['location_code'] or '',
                                     channel=pick.waveform_id['channel_code'][:2]+'?',
                                     level="channel")

            # Rotating streams when necessary while trimming to the same length all of them
            _st=_st.rotate(method="->ZNE", inventory=_inv, components=('ZNE'))

            # append stream to streams and inventory to inventories
            if i==0: 
                st=_st
                inv=_inv      
            else: 
                st+=_st
                inv+=_inv
    
        logging.info("The available waveforms are shown below...")
        logging.info(st.__str__(extended=True))

        logging.info("Creating the respective SAC files...")
        # loop for all available waveforms/stations
        for s in st:
            try:
                # select only specific trace's inventory 
                _inv = inv.select(starttime=starttime, 
                                  endtime=endtime, 
                                  network=s.stats.network,
                                  station=s.stats.station,
                                  location=s.stats.location,
                                  channel=s.stats.channel)
               
                # create the filename
                filename=s.stats.network+'.'+s.stats.station + '.' + \
                         '.' + s.stats.channel + '.XXXX.XXXXX.SAC'
    
                # create the full path to SAC file
                filepath=os.path.join(working_dir, filename)
 
                # we need to write and read it in order to invoke
                # the sac headers
                #print filepath
                s.write(filepath, format='SAC')
                s=read(filepath, debug_headers=True)[0]
    
                # populate the SAC header
                s.stats.sac['stla'] = _inv[0][0][0].latitude
                s.stats.sac['stlo'] = _inv[0][0][0].longitude
                s.stats.sac['stel'] = _inv[0][0][0].elevation
                s.stats.sac['cmpaz'] = _inv[0][0][0].azimuth
                s.stats.sac['cmpinc'] = _inv[0][0][0].dip
                s.stats.sac['kcmpnm'] = s.stats.channel
                s.stats.sac['scale'] = _inv[0][0][0].response.instrument_sensitivity.__dict__['value']
                s.stats.sac['mag'] = round(float(event.magnitudes[0].mag),1)
                s.stats.sac['evla'] = event.origins[0].latitude
                s.stats.sac['evlo'] = event.origins[0].longitude
                s.stats.sac['evdp'] = float(event.origins[0].depth)/1000
                s.stats.sac['lcalda'] = 1
                s.stats.sac['o'] = abs(s.stats.starttime-event.origins[0].time)
    
                #print s.stats.sac['stlo']
                #print s.stats.sac['stel']
                #print s.stats.sac['cmpaz']
                #print s.stats.sac['cmpinc']
                #print s.stats.sac['kcmpnm']
                #print s.stats.sac['scale']
                #print s.stats.sac['mag']
                #print s.stats.sac['evla']
                #print s.stats.sac['evlo']
                #print s.stats.sac['evdp']
                #print s.stats.sac['lcalda']
                #print s.stats.sac['o']

                # write final SAC file with modified header
                s.write(filepath, format='SAC')
    
                # report generation of SAC file
                logging.info(filepath + ' has been created...')

            except:
                logging.exception('Exception Raised')
                try:
                    os.remove(filepath)
                    logging.info(filepath + ' has been removed due to error...')
                except OSError:
                    pass
                continue

        # zip everything to tar.gz
        _tarname=os.path.join(working_dir, date.strftime("%Y%m%d%H%M%S"))
        logging.info("Creating " + _tarname + ".tar.gz containing the available waveforms...")
        tar = tarfile.open(_tarname +".tar.gz", "w:gz")
        tar.add(working_dir, arcname=date.strftime("%Y%m%d%H%M%S"))
        tar.close()

        # copy calMWandFM_noa executable, in order to run the process
        calMWandFM_noa=os.path.join(working_dir, os.path.basename(cfg.calMWandFM_noa))
        logging.info("Copying the " + cfg.calMWandFM_noa + " to " + calMWandFM_noa + "...")
        shutil.copy(cfg.calMWandFM_noa, calMWandFM_noa)

        # call the calMWandFM_noa executable
        logging.info("Running the " + calMWandFM_noa + " executable...")
        # change current directory
        os.chdir(working_dir)
        # call executable
        os.system(calMWandFM_noa + " >> " + cfg.logfile + " 2>&1 <<EOF\nEOF")
        #os.system(calMWandFM_noa+"<<EOF\nEOF" + " >>" + cfg.logfile + " 2>&1")

        ## Copy result to official dir

        # create the final dir where the results are going to be copied
        # in order to be read from other scripts
        result_dir=os.path.join(cfg.results_dir, date.strftime("%Y%m%d%H%M%S"))
        logging.info("Copying the results to " + result_dir)
        # create result dir folder respective to the event datetime
        os.makedirs(result_dir)
            
        # copy results from MWNEAR/calMwext dir
        # cp MWNEAR/calMwext/$event/result_Mw /home/user/results/$event/$event.mwnear
        logging.info("Copying result_Mw...")
        shutil.copy(
            os.path.join(cfg.output_dir, 'MWNEAR', 'calMwext', date.strftime("%Y%m%d%H%M%S"), 'result_Mw'),
            os.path.join(result_dir, date.strftime("%Y%m%d%H%M%S") + '.mwnear')
            )
            
        # copy results from FMNEAR dir
        # cp FMNEAR/$event/resmeca /home/user/results/$event/$event.fmnear
        logging.info("Copying resmeca...")
        shutil.copy(
            os.path.join(cfg.output_dir, 'FMNEAR', date.strftime("%Y%m%d%H%M%S"), 'resmeca'),
            os.path.join(result_dir, date.strftime("%Y%m%d%H%M%S") + '.fmnear')
            )
            
        # cp FMNEAR/$event/focmec.ps /home/user/results/$event/$event"_focmec.ps"
        logging.info("Copying focmec.ps...")
        shutil.copy(
            os.path.join(cfg.output_dir, 'FMNEAR', date.strftime("%Y%m%d%H%M%S"), 'focmec.ps'),
            os.path.join(result_dir, date.strftime("%Y%m%d%H%M%S") + '_focmec.ps')
            )
            
        # cp FMNEAR/$event/concatsig.ps /home/user/results/$event/$event"_wave.ps"
        logging.info("Copying concatsig.ps...")
        shutil.copy(
            os.path.join(cfg.output_dir, 'FMNEAR', date.strftime("%Y%m%d%H%M%S"), 'concatsig.ps'),
            os.path.join(result_dir, date.strftime("%Y%m%d%H%M%S") + '_wave.ps')
            )
            
        # cp FMNEAR/$event/map.ps /home/user/results/$event/$event"_map.ps"
        logging.info("Copying map.ps...")
        shutil.copy(
            os.path.join(cfg.output_dir, 'FMNEAR', date.strftime("%Y%m%d%H%M%S"), 'map.ps'),
            os.path.join(result_dir, date.strftime("%Y%m%d%H%M%S") + '_map.ps')
            )
            
        # cp FMNEAR/$event/map.ps /home/user/results/$event/$event"_controlqc"
        logging.info("Copying controlqc...")
        shutil.copy(
            os.path.join(cfg.output_dir, date.strftime("%Y%m%d%H%M%S"), 'controlqc'),
            os.path.join(result_dir, date.strftime("%Y%m%d%H%M%S") + '_controlqc')
            )

        # create an file ("$event"_event_id) in the results dir that contains one line with the event id
        # touch /home/user/results/$event/$event"_event_id"
        with open(os.path.join(result_dir, date.strftime("%Y%m%d%H%M%S") + '_event_id'), 'a') as event_id_file:
            event_id_file.write(str(event.resource_id).split('/')[-1])


except:
    logging.exception('Exception Raised')
    try:
        # delete working directory in order to try again
        # depends on our policy
        shutil.rmtree(working_dir, ignore_errors=False, onerror=None)
        shutil.rmtree(result_dir, ignore_errors=False, onerror=None)
        shutil.rmtree(os.path.join(cfg.output_dir, 'MWNEAR', 'calMwext', date.strftime("%Y%m%d%H%M%S")), ignore_errors=False, onerror=None)
        shutil.rmtree(os.path.join(cfg.output_dir, 'FMNEAR', date.strftime("%Y%m%d%H%M%S")), ignore_errors=False, onerror=None)

    except:
        logging.exception('Exception Raised')
