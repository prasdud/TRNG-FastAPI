# TRNG-FastAPI
A true hardware random number generator. Inspired by Cloudflare's LavaRand

# TODO
- Clean requirements.txt

- Using PyAV for low level control over stream raw data, if doesnt work move to OpenCV


## Logic
- First source of entropy X, a camera pointed towards large quantity of moving leaves. This raw rgb data will be used. Since its always moving, even small movements change the RGB value( right now it doesnt change the RGB value much, it varies but still in a range. I need to figure out can i make it even more varied)

- Second source of entropy Y, a SDR capturing truly random raw atmoshperic data.  http://websdr.org/ has various sources

- We will do F(X, Y), where F is some mathematical computation that introduces confusion, where F(X, Y) produces E, Where E is raw data stream driven by pure environmental entropy 

- This E will be exposed via an API that also has functionality for returning specific length of values. ex: /endpoint/return?size=10 returns 10 random numbers