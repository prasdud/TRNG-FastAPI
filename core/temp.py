from obspy.clients.seedlink.easyseedlink import create_client

def on_data(trace):
    # trace.data is a numpy array of raw seismometer readings
    print(f"Received {len(trace.data)} samples: {trace.data}")

client = create_client('rtserve.iris.washington.edu', on_data=on_data)
client.select_stream('IU', 'ANMO', 'BHZ')
client.run()