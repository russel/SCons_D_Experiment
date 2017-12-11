"""
Attempt and fail to get a package with a totally ridiculous name.
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

import TestSCons

from SCons.Environment import Base

from os.path import abspath, dirname

import sys
sys.path.insert(1, abspath(dirname(__file__) + '/../../../Support'))

from executablesSearch import isExecutableOfToolAvailable


def testForTool(tool):

    test = TestSCons.TestSCons()

    if not isExecutableOfToolAvailable(test, tool):
        test.skip_test("Required executable for tool '{0}' not found, skipping test.\n".format(tool))

    if tool == 'gdc':
        version_string = subprocess.check_output(('gdc', '--version')).decode().splitlines()[0].split()[3]
        major, minor, bugfix = [int(x) for x in version_string.split('.')]
        if major < 7 or (major == 7 and minor >= 2):
            test.skip_test("gdc as at version 7.2.0 cannot compile the test code, D version is too old.\n")

    test.write('SConstruct', '''
environment = Environment(tools=['dub', '{}'])
environment.AddDubLibrary('thisisapackagenamethatnooneintheuniversewilleveruse')
'''.format(tool))

    test.run(status=2, stdout=None, stderr=None)

    test.fail_test('Do not know how to create a target from source' not in test.stderr())

    test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
