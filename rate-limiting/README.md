# Rate limiting examples

These are simple client/server examples of rate limiting


Requires: aiohttp, Python 3.6


## Run

To run the server, just:

```
python server.py
```

The server will run on port 8080

Then, the client to load test the server:

```
python client.py
```


## Request/sec

The server will output Req/sec to the console but you can also request `http://localhost:8080/rate`
to get the current request per second.

You can also get the rate over a different time period by using the `interval` query param:
`http://localhost:8080/rate?interval=20`