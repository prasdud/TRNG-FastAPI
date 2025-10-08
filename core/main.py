'''
Sample code for reading live video stream and raw data
'''

import av
import cv2
import numpy as np

container = av.open("/dev/video0") # Adjust the path as necessary for your video source

for frame in container.decode(video=0):
    img = frame.to_ndarray(format='bgr24')

    print(img)
        
    cv2.imshow('Video', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
container.close()
