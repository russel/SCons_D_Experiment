from __future__ import print_function

"""SCons.Tool.dub

A tool for integrating use of Dub with ldc, dmd, and gdc tools.

Developed by Russel Winder (russel@winder.org.uk)
2017-04-13 onwards.
"""

import os
import subprocess

import SCons.Builder
import SCons.Node
import SCons.Errors

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


def _check_correct_calling(target, source):
    if len(target) != 1:
        SCons.Errors.StopError('Incorrect number of targets.')
    if len(source) != 0:
        SCons.Errors.StopError('Incorrect number of sources')


def _do_nothing(target, source, env):
    _check_correct_calling()


def _do_nothing_print_message(*args):
    pass  # print(args)


def _unit_threaded_special_processing(env):
    def reassign_target(target, source, env):
        _check_correct_calling(target, source)
        return [env.File(source[0].name)], [source[0].dir.srcnode()]

    def make_main(target, source, env):
        _check_correct_calling(target, source)
        modules = tuple(f for f in os.listdir(str(source[0])) if f.endswith('.d'))
        opening = """//Automatically generated do not edit by hand.
import unit_threaded;
int main(string[] args) {
    return args.runTests!(
"""
        closing = """    );
}
"""
    with open(str(target[0]), 'w') as f:
        f.write(opening + ''.join(tuple('"{}",\n'.format(m.replace('.d', '')) for m in modules)) + closing)

    env['BUILDERS']['UnitThreadedMakeMain'] = SCons.Builder.Builder(
        action=make_main,
        emitter=reassign_target,
        single_source=True,
        PRINT_CMD_LINE_FUNC=_do_nothing_print_message,
    )


class _Library(SCons.Node.FS.File):

    def __init__(self, env, name, version):
        self.env = env
        self.name = name
        self.key_name = name.replace('-', '_')
        self.version = version
        self.directory = os.path.join(os.environ['HOME'], '.dub', 'packages', name + '-' + version, name)
        self.compiler = env['DC']

        if not os.path.isdir(self.directory):
            print('Fetching', name, 'from Dub repository.')
            command = 'dub fetch {} --version={}'.format(name, version) if version != '' else 'dub fetch {}'.format(name)
            process = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
            rc = process.wait()
            if rc != 0:
                print('dub fetch returned error code', rc)
                stderr = process.stderr.read()
                if 'Skipping execution' not in stderr:
                    raise SCons.Errors.StopError('Something weird happened. ' + stderr)

        def collect_library_versions():
            return [f for f in os.listdir(build_directory) if f.startswith('library-debug-linux.posix-x86_64-' + ('ldc' if self.compiler == 'ldc2' else self.compiler))]

        def compile_library():
            print('Compiling fetched', name)
            process = subprocess.Popen('dub build --build=debug --compiler={}'.format(self.compiler), shell=True, stderr=subprocess.PIPE, cwd=self.directory)
            rc = process.wait()
            if rc != 0:
                print('dub build returned error code', rc)
                stderr = process.stderr.read()
                if 'Skipping execution' not in stderr:
                    raise SCons.Errors.StopError('Something really weird happened. ' + stderr)

        build_directory = os.path.join(self.directory, '.dub', 'build')
        if not os.path.isdir(build_directory):
            compile_library()
        selected_versions = collect_library_versions()
        if len(selected_versions) == 0:
            compile_library()
            selected_versions = collect_library_versions()
            if len(selected_versions) == 0:
                raise SCons.Errors.StopError('Cannot compile {} for {}.'.format(name, compiler))
        if len(selected_versions) > 1:
            raise SCons.Errors.StopError('Multiple compiled library versions found, this cannot happen.')
        path_to_library = os.path.join(build_directory, selected_versions[0], 'lib' + name + '.a')
        if not os.path.isfile(path_to_library):
            compile_library()
            if not os.path.isfile(path_to_library):
                raise SCons.Errors.StopError('The library file {} is not there.'.format(path_to_library))
        env.Precious(path_to_library)
        env.NoClean(path_to_library)

        if name == 'unit-threaded':
            _unit_threaded_special_processing(env)

        compiled_library_directory = os.path.join(build_directory, selected_versions[0])
        self.library_file = os.path.join(compiled_library_directory, 'lib' + name + '.a')
        env.Append(DPATH=os.path.join(self.directory, 'source'))
        env.Append(LIBPATH=compiled_library_directory)
        env.Append(LIBS=name)
        SCons.Node.FS.File.__init__(self, name, env.Dir(compiled_library_directory), self)


def _ensure_library_present_and_amend_target_path(target, source, env):
    _check_correct_calling()
    library = _Library(env, target[0].name, source[0].value)
    if 'library_' + library.key_name in env:
        print('Library {} already found'.format(library.key_name))
    else:
        env['LIBRARIES'][library.key_name] = library
    return [env.File(library.library_file)], []


def generate(env):
    env['DUB'] = env.Detect('dub') or 'dub'
    env['LIBRARIES'] = {}
    env['BUILDERS']['AddDubLibrary'] = SCons.Builder.Builder(
        action=_do_nothing,
        emitter=_ensure_library_present_and_amend_target_path,
        target_factory=SCons.Node.FS.File,
        source_factory=SCons.Node.Python.Value,
        single_source=True,
        PRINT_CMD_LINE_FUNC=_do_nothing_print_message,
    )


def exists(env):
    return env.Detect('dub')

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
