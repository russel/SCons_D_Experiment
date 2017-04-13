"""SCons.Tool.dub

An tool for integrating use of Dub with ldc, dmd, and gdc tools.

Developed by Russel Winder (russel@winder.org.uk)
2017-04-13 onwards.
"""

#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import subprocess

from SCons.Builder import Builder


def add_dub_library(env, library_name, library_version, compiler):

    library_directory = os.path.join(os.environ['HOME'], '.dub', 'packages', library_name + '-' + library_version, library_name)

    if not os.path.isdir(library_directory):
            command = 'dub fetch {} --version={}'.format(library_name, library_version) if library_version is not None else 'dub fetch {}'.format(library_name)
            process = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
            rc = process.wait()
            if rc != 0:
                print('dub fetch returned error code', rc)
                stderr = process.stderr.read()
                if 'Skipping execution' not in stderr:
                    raise Exception('Something weird happened.' + stderr)

    build_directory = os.path.join(library_directory, '.dub', 'build')
    if not os.path.isdir(build_directory):
        process = subprocess.Popen('dub build --build=release --compiler={}'.format(compiler), shell=True, stderr=subprocess.PIPE, cwd=library_directory)
        rc = process.wait()
        if rc != 0:
            print('dub build returned error code', rc)
            stderr = process.stderr.read()
            if 'Skipping execution' not in stderr:
                raise Exception('Something really weird happened.' + stderr)

        if library_name == 'unit-threaded':
            process = subprocess.Popen('dub build --build=release --compiler={} --config=gen_ut_main'.format(compiler), shell=True, stderr=subprocess.PIPE, cwd=library_directory)
            rc = process.wait()
            if rc != 0:
                print('dub build returned error code', rc)
                stderr = process.stderr.read()
                if 'Skipping execution' not in stderr:
                    raise Exception('Something truly weird happened.' + stderr)

    selected_versions = [f for f in os.listdir(build_directory) if f.startswith('library-release-linux.posix-x86_64-' + ('ldc' if compiler == 'ldc2' else compiler))]
    if len(selected_versions) == 0:
        raise Exception('Library not yet built, this cannot happen.')
    if len(selected_versions) > 1:
        raise Exception('Multiple compiled library versions found, this cannot happen.')
    compiled_library_directory = os.path.join(build_directory, selected_versions[0])
    env.Append(DPATH=os.path.join(library_directory, 'source'))
    env.Append(LIBPATH=compiled_library_directory)
    env.Append(LIBS=library_name)

    if library_name == 'unit-threaded':

        def unit_threaded_make_main(env, targets, sources, library_directory=library_directory):

            print(env, targets, sources,library_directory)

            if targets is None:
                assert len(sources) == 1
                target_name = sources[0]
            else:
                assert len(targets) == 1
                target_name = targets[0]
            gen_ut_main = os.path.join(library_directory, 'gen_ut_main')
            assert os.path.isfile(gen_ut_main), 'get_ut_main not found.'
            rc = subprocess.call([gen_ut_main, '-f', target_name])
            assert rc == 0
            return target_name

        env['BUILDERS']['UnitThreadedMakeMain'] = unit_threaded_make_main


def unit_threaded_make_main(env, targets, sources):

    print('unit_threaded_make_main', env, targets, sources)

    raise Exception('Unit-Threaded is not installed.')


def ensure_dub_library_present(env, targets, sources):

    print('ensure_dub_library_present', env, targets, sources)

    # Subvert the Builder signature protocol.
    if targets is None:
        assert len(sources) == 1, 'No version number and no library name.'
        add_dub_library(env, sources[0], None, env['DC'])
    assert len(targets) == 1, 'Incorrect number of targets.'
    assert len(sources) == 1, 'Incorrect number of sources.'
    add_dub_library(env, targets[0], sources[0], env['DC'])
    return 0


def generate(env):
    env['DUB'] = env.Detect('dub')
    env.Append(BUILDERS={
        'AddDubLibrary': ensure_dub_library_present,
        'UnitThreadedMakeMain': unit_threaded_make_main,
    })


def exists(env):
    return env.Detect('dub')

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
