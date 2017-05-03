#!/bin/sh

here=$(pwd)

cd ~/.scons/site_scons/site_tools/

for f in DCommon.py dmd.py ldc.py gdc.py
do
    ln -s $here/$f .
done
