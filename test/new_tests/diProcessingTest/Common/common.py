"""
Test compiling a project using di files.
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

def testForTool(tool):

    _exe = TestSCons._exe
    test = TestSCons.TestSCons()

    if not test.where_is(tool):
        test.skip_test("Could not find '%s', skipping test.\n" % tool)

    #make a directory for the library, which is built making di interface files as a side effect
    test.subdir('source1')
    test.write('source1/SConscript', """\
env = Environment()
env["DPATH"] = ["."]
env["DINTFDIR"] = "../interfaces1"
env.Library("../something","mod1.d")
""")
    test.write('source1/mod1.d', """\
import std.stdio;
void doSomething() { writefln("did something"); }
""")

    #make a program that depends on the library, and imports the di files
    test.subdir('source2')
    test.write('source2/SConscript', """\
env = Environment()
env["DPATH"] = ["../interfaces1"]
env["LIBPATH"] = ['..']
env["LIBS"] = ["something"]
env.Program("../prog",['mod2.d'])
""")
    test.write('source2/mod2.d', """\
import mod1;
void main() { doSomething(); }""")

    #build the two projects
    test.write('SConstruct', """\
SConscript("source1/SConscript",variant_dir="build/source1",src_dir="source1")
SConscript("source2/SConscript",variant_dir="build/source2",src_dir="source2")
""")

    test.run()

    test.fail_test(test.stdout().find(tool) == -1)

    test.must_exist(test.workpath('build/interfaces1/mod1.di'))

    test.must_exist(test.workpath('build/prog'+_exe))

    test.run(program=test.workpath('build/prog'+_exe))

    test.fail_test(not test.stdout() == 'did something\n')

    test.run()

    test.fail_test(test.stdout().find(tool) != -1)

    test.pass_test()
