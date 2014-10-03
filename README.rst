Nothing to see yet.

Just a free time game project.


Setup development environment
-----------------------------

Execute the following commands::

  sudo apt-get install python python-virtualenv`
  virtualenv .env
  . .env/bin/activate
  python setup.py develop

This will setup a development environment and install laneya including all
dependencies into it. You can activate the virtual environment anytime by
calling::

  . .env/bin/activate

laneya consists of two programs: A server called ``laneyad`` and a client
called ``laneya``.
