#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Riccardo Gori <goriccardo@gmail.com>
# License: GPL-3 http://www.gnu.org/licenses/gpl.txt

def main():
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

if __name__ == '__main__':
    main()
