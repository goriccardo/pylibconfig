#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Riccardo Gori <goriccardo@gmail.com>
# License: GPL-3 http://www.gnu.org/licenses/gpl.txt

def main():
    read_test()
    write_test()

def read_test():
    from pylibconfig import libconfigFile
    test = libconfigFile('test/cfgfiles/test.cfg')
    appwin = test.application.window
    assert appwin.title == "My Application"
    assert appwin.size.w == 640
    assert appwin.size.h == 480
    assert appwin.pos.x == 350
    assert appwin.pos.y == 250
    app = test.application
    assert app.a == 5
    assert app.b == 6
    assert app.ff == 1e6
    assert test.get('application.test-comment') == "/* hello\n \"there\"*/"
    assert test.get('application.test-long-string') == "A very long string that spans multiple lines. " \
                                                       "Adjacent strings are automatically concatenated."
    assert test.get('application.test-escaped-string') == "\"This is\n a test.\""
    gr1 = test.application.group1
    assert gr1.x == 5
    assert gr1.y == 10
    assert gr1.my_array == range(10,23)
    assert gr1.flag == True
    assert gr1.group2.zzz == "this is a test"
    assert gr1.states == ["CT", "CA", "TX", "NV", "FL"]
    assert test.binary == [0xAA, 0xBB, 0xCC]
    #TODO: Not working tests!
    #assert test.get('list') == [ ["abc", 123, True], 1.234, [], [1,2,3]]
    #assert test.books
    msc = test.misc
    assert msc.port == 5000
    assert msc.pi == 3.14159265
    assert msc.enabled == False
    assert msc.mask == 0xAABBCCDD
    assert msc.unicode == "STARGΛ̊TE SG-1"
    assert msc.bigint == 9223372036854775807
    assert msc.bighex == 0x1122334455667788

def write_test():
    from pylibconfig import libconfigFile
    test = libconfigFile('/tmp/pylibconfigtest.cfg', True)
    #Test strings
    assert test.set('string.short', 'hi', True)
    lls = """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    Vestibulum fermentum, eros nec lacinia convallis, lectus est consequat
    tellus, in condimentum risus metus èu tellus. Suspendisse potenti.
    Proin bibendum, sapién at feugiat auctor, turpis nisi molestie lorem,
    at pretium dolor leo vel eros. In commodo ultricies tortor at sagittis.
    Vestibulum at nunc vel mi adipiscing dapibùs. Morbi velit justo,
    luctus congue commodo eget, sodales non màssa. Mauris ac mauris sem.
    Integer semper fermentum suscipit. Nunc eu purus urna.
    Nam nec ultrices urna. Quisque eu mauris egestas nisl faucibus semper
    eget malesuada purus. Etìam dignissim ligula at tellus consequat aliquam.
    Nam hendrerit, magna ac placerat tincidunt, lorem liberò laoreet lacus,
    nec tempor tellus eros a odio. Integer lectus nisi, ultricies ut rutrum
    sed, sodales in quam.
    """
    assert test.set('string.long-long-string', lls, True)
    assert test.set('math.unicode', '⨕⨘dA≉⥁ℜ', True)
    #Test numbers
    assert test.set('math.integer', -3400, True)
    assert test.set('math.smallfact', reduce(lambda x,y:x*y, range(1,10)), True)
    hugeness = 21
    assert test.set('math.hugefact', reduce(lambda x,y:x*y, range(1,hugeness)), True)
    assert test.math.hugefact == reduce(lambda x,y:x*y, range(1,hugeness))
    #TODO: solve problems with longlong integers
    assert test.set('math.floats.small', 1.452e-16, True)
    assert test.set('math.floats.big', 140301e156, True)
    #Test bools
    assert test.set('math.is.a.nice.thing.right.question.mark', True, add=True)
    assert test.set('The.Cretans.are.always.liars', False, add=True)
    #Test lists and arrays
    assert test.set('math.fibonacci', [1,2,3,5,8,13], True)
    assert test.set('personal.mynames', ['John', 'Patrick', 'Michel', 'Jack'], True)
    assert test.set('personal.mynames', ['Richard', 'Lagrange'])
    assert test.get('personal.mynames') == ['Richard', 'Lagrange']
    #Dump the file
    test.write()

if __name__ == '__main__':
    main()
