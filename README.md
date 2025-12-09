# TRNG-FastAPI
A true hardware random number generator. Inspired by Cloudflare's LavaRand

# TODO
- Complete performance optimization / overhaul. Go through codebase and remove redundant stuff
    - SDR stream is prone to websocket closing, add better handling entropy engine side, rn it just outputs None
- Dockerize deployment, after User MVP done

# Issues
- Video service bottleneck: Bottleneck: Camera acquisition takes 69.5ms/frame 70% of time camera delivering 10 FPS instead of 30 FPS; remove cv2.imshow() (saves 20ms) and configure camera with options={'framerate': '30', 'video_size': '640x480'}
- Above issue sounds like he camera is lagging because every frame is writing to the redis stream at this line
`r.xadd('video_data_stream', {'frame': img_binary}, maxlen=100, approximate=True)`

# Running
## Prerequisities
- Python 3
- Install requirements from requirements.txt
- Redis

# User MVP
- API endpoint that provides random number, user provides space
- Random color generator, takes 9 digit RN, wraps it in RGB, generates the color
- Coin flipper, Binary RN

# LTG
- Mathematical randomness analysis, refer randomness-testing doc
- Periodically rotate SDR bands based on location of SDR and time of day
- Implement seismic service
- Port latency critical modules to Go or Rust (maybe microservce architecture with Go?)

## Logic
- First source of entropy X, a camera pointed towards large quantity of moving leaves. This raw rgb data will be used. Since its always moving, even small movements change the RGB value( right now it doesnt change the RGB value much, it varies but still in a range. I need to figure out can i make it even more varied)

- Second source of entropy Y, a SDR capturing truly random raw atmoshperic data.  http://websdr.org/ has various sources

- We will do F(X, Y), where F is some mathematical computation that introduces confusion, where F(X, Y) produces E, Where E is raw data stream driven by pure environmental entropy 

- This E will be exposed via an API that also has functionality for returning specific length of values. ex: /endpoint/return?size=10 returns 10 random numbers


## Notes
- normal ws (websocket) streams do not work with normal websocket implementations, but i found one wss which works ->  wss://3.radiorubka.org/~~stream?v=11