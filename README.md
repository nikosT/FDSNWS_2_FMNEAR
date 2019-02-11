# FDSNWS_2_FMNEAR
FDSN Web Services integrated with Automatic Moment Tensor calculation

The Python code (check.py) requests near real-time Events through the FDSNWS-event for a particular time window specified in the configuration file. The periodical check is performed via a Linux Cron Job. For all of the events returned by the FDSNWS-event, the Python code (extract.py) is triggered for each one of them, sequentially. The current implementation passes the event's datetime stamp as input argument to the Python code.


The Python code (extract.py) checks if the specific event that was passed as input argument is already (or being) calculated. The current implementation of the Python code will only trigger new events that were not processed before.


More:

FDSN Web Services integrated with Automatic Moment Tensor
calculation
Nikolaos Triantafyllis (1,2) and Christos Evangelidis (1)
(1) National Observatory of Athens, Institute of Geodynamics, Athens, Greece (triantafyl@noa.gr), (2) National Technical
University of Athens, School of Electrical and Computer Engineering, Computing Systems Laboratory, Athens, Greece
Moment Tensors (MT) are used in a wide range of seismological research fields, such as stress inversion, shakemap
generation, tsunami warnings, and many other studies, constituting the automatic and quick determination an
important task. The Fortran software calMwandFM provides the ability for a near real-time automatic MT
computation by applying the FMNEAR and MWNEAR calculation approaches (Delouis et al., 2009 and 2014).
Meanwhile, the Federation of Digital Broad-Band Seismograph Networks (FDSN) (Ahern, 2003), developer of
the Standard for the Exchange of Earthquake Data (SEED), has additionally produced a utility for homogeneous
seismological data distribution; the FDSN Web Services (FDSNWS). These web services unfold exchange
of time series data (FDSNWS-dataselect), related metadata (FDSNWS-station) and seismic event information
(FDSNWS-event). More and more institutes and data centers are supporting the FDSNWS either for external
or internal use. This can also be acknowledged since it became a seismological data distribution standard for
the European Integrated Data Archive (EIDA). Thus, the same client software that supports the FDSNWS
interconnection could be attached to and work with any data center that runs these Web Services. The Python
library ObsPy (Beyreuther et al., 2010), which facilitates the development of seismological software packages and
workflows, supports the FDSNWS interconnection via its Python API. This feature offers the ability to determine
a way of integrating the FDSNWS to an existing near real-time seismological application, like the automatic MT
computation by Delouis, 2014. In this work, we developed a program, written in Python, that supplies the data
center with the ability to check for new seismic events in near real-time served by the FDSNWS and to trigger the
automatic MT process based on specified configurable thresholds. The triggered procedure includes the request
of waveform and stations’ metadata through these Web Services, data manipulation for the related automatic
MT application and results’ preparation and distribution. The program could be attached to any data center that
operates a Linux OS and runs both the FDSNWS and the automatic MT computation by Delouis, 2014. Finally,
since the source code is open and free to the scientific community, it could be easily modified in order to support
other similar near real-time purposes.

References
Delouis, B., Charlety, J., & Vallée, M. (2009). A method for rapid determination of moment magnitude M w for
moderate to large earthquakes from the near-field spectra of strong-motion records (MWSYNTH). Bulletin of the
Seismological Society of America, 99(3), 1827-1840.
Delouis, B. (2014). FMNEAR: Determination of focal mechanism and first estimate of rupture directivity using
near-source records and a linear distribution of point sources. Bulletin of the Seismological Society of America,
104(3), 1479-1500.
Ahern, T. K. (2003). The FDSN and IRIS Data Management System: Providing easy access to terabytes of
information. In International Geophysics (Vol. 81, pp. 1645-1655). Academic Press.
Beyreuther, M., Barsch, R., Krischer, L., Megies, T., Behr, Y., & Wassermann, J. (2010). ObsPy: A Python toolbox
for seismology. Seismological Research Letters, 81(3), 530-533.
