#! /usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

SCRIPT_NAME = "rtraceroute"
SCRIPT = (
    "_JLOG_EXTRACTOR_COMPLETE=source {script_name} > "
    "auto-completion.sh".format(script_name=SCRIPT_NAME)
)

setup(
    name='rtraceroute',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'click',
        'ripe.atlas.cousteau',
        'pydot',
        'graphviz',
        'networkx',
        'ipwhois',
        'shell',
    ],
    entry_points='''
        [console_scripts]
        {script_name}=rtraceroute.rtraceroute:run
    '''.format(script_name=SCRIPT_NAME),
)
