Two approaches for dealing with issue that `viviz.py:vivizconfig()` may require a long time to finish when only `server` is given and there are many datasets (because function needs to make one request per dataset in the catalog to generate ViViz catalog).

To work around this, could send an intermediate page that shows progress. In both approaches, would need to deal with fact that a request may come in while another request is doing the same process.

Should also consider parallelizing requests for metadata.

# Approach 1

`server.py` is based on [1](https://mortoray.com/2014/03/04/http-streaming-of-command-output-in-python-flask/)

Run using
```
 pip install gunicorn eventlet flask
 gunicorn -k eventlet server:app
```
and open http://localhost:8000/. The advantage of this approach is that messages are sent using the event-stream format.

# Approach 2

```
rm -f log.log ; for ((i=0;i<100;i=i+1)); do echo $i >> log.log; sleep 1; done &
gunicorn -k eventlet server:app
```

and open http://localhost:8000/tail.htm. An advantage is that this similifies the server-side code.
