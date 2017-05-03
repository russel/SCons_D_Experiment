# SCons D Experiment

This repository contains the D tools from the SCons distribution but extended with lots of new stuff.

This is really a playground for trying out idea for extending the SCons tools.

## Installation

The canonical way of "installing" this currently is to clone this repository and then put symbolic links to
the dmd.py, ldc.py, gdc.py, and DCommon files of the repository in ~/.scons/site\_scons/site\_tools
directory.

### Linux, UNIX, and MacOS

A pair of scripts are in the repository to "automate" the installation and un-installation: setup.sh and
teardown.sh. Clone this repository and run setup.sh and it should do the right thing so tools in this
repository are used instead of the built-in SCons ones. Running teardown.sh should reverse this.

If this isn't working for you please put an issue in place.

### Windows

Help sought.
