HAPI Plot Server for Python 2/3
===============================

Serve plots from a HAPI server using the `hapiplot` function in `hapiclient <http://github.com/hapi-server/client-python>`_.

Demo: `http://hapi-server.org/plot <http://hapi-server.org/plot>`_

Installation and Startup
------------------------

.. code:: bash

    pip install hapiplotserver
    hapiplotserver --port 5999

then see http://localhost:5999/ for documentation.

Script Usage
------------

See `test_hapiplotserver.py <https://github.com/hapi-server/plotserver-python/hapiplotserver/master/test_hapiplotserver.py>`_

Development
-----------

.. code:: bash

    git clone https://github.com/hapi-server/plotserver-python

To run tests before a commit, execute

.. code:: bash

    make test-repository

Contact
-------

Submit bug reports and feature requests on the `repository issue
tracker <https://github.com/hapi-server/plotserver-python/issues>`__.

Bob Weigel rweigel@gmu.edu