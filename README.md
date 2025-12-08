# TRNG-FastAPI
A true hardware random number generator. Inspired by Cloudflare's LavaRand

# TODO
- Implement proper redis cleanup on closing / error. It eats RAM rn
- Complete performance optimization / overhaul. Go through codebase and remove redundant stuff
- Mathematical randomness analysis, refer randomness-testing doc
- Dockerize deployment, after User MVP done

# Running
## Prerequisities
- Python 3
- Install requirements from requirements.txt
- Redis

# User MVP
- API endpoint that provides random number, user provides space
- Random color generator, takes 9 digit RN, wraps it in RGB, generates the color
- Coin flipper, Binary RN

## Logic
- First source of entropy X, a camera pointed towards large quantity of moving leaves. This raw rgb data will be used. Since its always moving, even small movements change the RGB value( right now it doesnt change the RGB value much, it varies but still in a range. I need to figure out can i make it even more varied)

- Second source of entropy Y, a SDR capturing truly random raw atmoshperic data.  http://websdr.org/ has various sources

- We will do F(X, Y), where F is some mathematical computation that introduces confusion, where F(X, Y) produces E, Where E is raw data stream driven by pure environmental entropy 

- This E will be exposed via an API that also has functionality for returning specific length of values. ex: /endpoint/return?size=10 returns 10 random numbers


## Notes
- normal ws (websocket) streams do not work with normal websocket implementations, but i found one wss which works ->  wss://3.radiorubka.org/~~stream?v=11