from setuptools import setup
from distutils.command.build import build
from setuptools.command.install_lib import install_lib


setup(
    name='laneya',
    version='0.0.0',
    description="multiplayer roguelike game",
    long_description=open('README.rst').read(),
    url='https://github.com/xi/leneya',
    author='Tobias Bengfort',
    author_email='tobias.bengfort@posteo.de',
    packages=['laneya'],
    install_requires=[
        'twisted',
    ],
    license='GPLv2+',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Framework :: Twisted',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v2 or later '
            '(GPLv2+)',
        'Topic :: Games/Entertainment :: Role-Playing',
    ])
