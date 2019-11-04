Introduction
=============

Abstract
----------
A cool tool for digits converting.

It could be applied in GA

Keywords
----------
Converter, Digits

Content
=========

Classes::

    BaseConverter: .tonumber(lst), .tolist(num, L)
    DigitConverter
    BinaryConverter: subclass of DigitConverter
    IntervalConverter

Objects::

    _256Converter: instance of BinaryConverter
    _unitIntervalConverter: instance of IntervalConverter

Grammar
=========

import
-------------

import digit_converter

Basic usage
-------------

Codes::

    print(f'256-converter: {_256Converter.tonumber([1,0,1,0,1,1,1,0])}<->{_256Converter.tolist(174)}')

    c = BinaryConverter(exponent=4)
    d = c.tolist(12.223, L=8)
    print(f'binary-converter: {d}<->{c.tonumber(d)}={c.pretty(d)}')
    c = IntervalConverter(a=0, b=10)
    d = c.tolist(2.4, L=8)
    print(f'[{c.a},{c.b}]-converter: {d}<->{c.tonumber(d)}={c.pretty(d)}')

OUTPUT::

    256-converter: 174<->[1, 0, 1, 0, 1, 1, 1, 0]
    binary-converter: [0, 1, 1, 0, 0, 0, 0, 1]<->12.125=0*2^4 + 1*2^3 + 1*2^2 + 0*2^1 + 0*2^0 + 0*2^-1 + 0*2^-2 + 1*2^-3
    [0,10]-converter: [0, 0, 1, 1, 1, 1, 0, 1]<->2.3828125=0*2^1 + 0*2^0 + 1*2^-1 + 1*2^-2 + 1*2^-3 + 1*2^-4 + 0*2^-5 + 1*2^-6
