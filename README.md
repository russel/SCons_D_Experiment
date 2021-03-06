# SCons D Experiment

This repository is really a playground for trying out ideas for extending the D support in the SCons build
system. It is a place to try things out before putting things into my clone of the mainline SCons repository
([see here](https://github.com/russel/scons)) prior to creating pull requests.

Currently this repository has copies of ldc.py, dmd.py, and gdc.py from the SCons repository just in case
some experimentation is needed outside of the SCons repository: evolution of these tools will normally be
done in the SCons repository itself using feature branches.

The main experiment at the moment is Dub support for SCons in dub.py. A first draft of the tool is written
and works for the author, but there are only minimal tests.  Many more tests have to be written before there
is any possibility of getting it into the SCons mainline, hence the work here.

## Installation

### Linux, UNIX, and MacOS

The canonical way of installing tools from this repository is to clone this repository and then put symbolic links to the
files you want to use (and also DCommon.py if you are using dmd.py, ldc.py, or gdc.py from here) in either
<project-root>/site\_scons/site\_tools for use with a single project, or ~/.scons/site\_scons/site\_tools
for use with all your projects.

A pair of scripts are in the repository to automate the installation and un-installation of all files to the personal
SCons tools directory for use with all your projets: setup.sh and teardown.sh. Clone this repository and run
setup.sh and it should do the right thing so the tools in this repository are used instead of the built-in SCons
ones. Running teardown.sh should reverse this. Most of the time though people will want to be more selective and
just make links to files manually. The scripts can guide you what to do.

If things aren't working for you please email me.

### Windows

Help sought.

## Licence

The files here are licensed using the MIT licence since that is required for inclusion in SCons.
