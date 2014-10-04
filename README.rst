Nothing to see yet.

Just a free time game project.


Setup development environment
-----------------------------

Execute the following commands::

  sudo apt-get install python python-virtualenv
  virtualenv .env
  . .env/bin/activate
  python setup.py develop

This will setup a development environment and install laneya including all
dependencies into it. You can activate the virtual environment anytime by
calling::

  . .env/bin/activate

laneya consists of two programs: A server called ``laneyad`` and a client
called ``laneya``.


Build Documentation
-------------------

An HTML documentation can be automatically generated from source code using
`sphinx`_::

  pip install sphinx
  python setup.py build_sphinx
  xdg-open docs/build/html/index.html

To add a new module to the documentation, create a corresponding file in
``docs/source/`` and add an entry to the table of contents in
``docs/source/index.rst``.


Run Tests
---------

You can automatically run all tests via tox::

  pip install tox
  tox

This will setup virtual environments for multiple versions of python and run
all tests with each of these versions.

Alternatively you can run the tests manually::

  pip install flake8 nose coverage
  flake8
  nosetests
  xdg-open .cover/index.html


.. _sphinx: http://sphinx-doc.org
