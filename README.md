**HAPI Plot Server for Python 3.6+**

Serve plots from a HAPI server using the `hapiplot` function in [hapiplot package](http://github.com/hapi-server/client-python).

[**Live Demo**](http://hapi-server.org/plot)

# Installation and Startup

```bash
pip install hapiplotserver --upgrade
hapiplotserver --port 5999 --workers 4
```

then see http://localhost:5999/ for API documentation.

# Script Usage

See [test_hapiplotserver.py](https://github.com/hapi-server/plotserver-python/blob/master/hapiplotserver/test/test_hapiplotserver.py).

# Development

```bash
git clone https://github.com/hapi-server/plotserver-python
cd plotserver-python; pip install -e .
```

To run tests before a commit, execute

```bash
make test-repository
```

# Contact

Submit bug reports and feature requests on the [repository issue
tracker](https://github.com/hapi-server/plotserver-python/issues>).
