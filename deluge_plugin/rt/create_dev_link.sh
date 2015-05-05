#!/bin/bash
cd /home/muali/cppProjects/real_time_torrent/deluge_plugin/rt
mkdir temp
export PYTHONPATH=./temp
/usr/bin/python setup.py build develop --install-dir ./temp
cp ./temp/rt.egg-link /home/muali/.config/deluge/plugins
rm -fr ./temp
