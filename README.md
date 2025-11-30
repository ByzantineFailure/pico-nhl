# pico-nhl

A small server+Micropython library for enabling a Raspberry Pi Pico (2) W to react to events in NHL games

Consists of two parts:

1.  A server which proxies the NHL APIs and slims down the JSON they return to something that can easily fit within a Pico W's memory
2.  A Micropython library which makes requests to the server and returns well-formatted objects for use

See each individual directory for their use and APIs

## Notes

I could have _probably_ done this without the server if I wasn't too lazy to process the JSON responses as a stream.  However, I _am_ lazy _and_ happen to have a server around the house to host the API.

