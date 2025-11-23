'''
seismic_service.py
Captures live raw seismometer data from a SeedLink server and returns it as a raw data stream.
Not implemented yet in the entropy engine, maybe later
'''
from obspy.clients.seedlink.easyseedlink import create_client
from utils.logger import logger as log
def on_data(trace):
    # trace.data is a numpy array of raw seismometer readings
    log.info(f"Received {len(trace.data)} samples: {trace.data}")

client = create_client('rtserve.iris.washington.edu', on_data=on_data)
client.select_stream('IU', 'ANMO', 'BHZ')
client.run()