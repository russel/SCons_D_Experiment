# SCons D Experiment

This repository contains the D tools from the SCons distribution but extended with lots of new stuff.

This is really a playground for trying out idea for extending the SCons tools.

## Installation

### Linux, UNIX, and MacOS

The canonical way of installing these tools is to clone this repository and then put symbolic links to the
dmd.py, ldc.py, gdc.py, and DCommon.py files of the repository in either
<project-root>/site\_scons/site\_tools for use with a single project, or ~/.scons/site\_scons/site\_tools
for use with all your projects.

A pair of scripts are in the repository to automate the installation and un-installation to the personal
SCons tools directory for use with all your projets: setup.sh and teardown.sh. Clone this repository and run
setup.sh and it should do the right thing so the tools in this repository are used instead of the built-in SCons
ones. Running teardown.sh should reverse this.

If this isn't working for you please put an issue in place.

### Windows

Help sought.
