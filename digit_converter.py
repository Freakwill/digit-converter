#-*- coding: utf-8 -*-

"""Convert a number to an array of digits, and inversely

BaseClass:
BaseConverter
    tonumber(lst) -> number
    tolist(number, L) -> list (Digits)

Classes:
BinaryConverter
IntervalConverter
"""

import types
try:
    from collections.abc import Iterable
    Digits = Iterable[int]
except:
    from typing import Iterable
    Digits = Iterable[int]

import numpy as np


def length(num):
    s = str(num)
    if s.startswith('-'):
        return len(s) - 1
    return len(s)


def toint(lst, base=10):
    # all numbers in lst are positive
    return sum(digit * base ** k for k, digit in enumerate(lst[::-1]))


class BaseConverter:
    """type converter

    transform a list to a number and reversely
    """
    
    def tonumber(self, l):
        """list -> number 
        transform a list (or an iterable obj) to a number
        """
        raise NotImplementedError

    def tolist(self, n, L:int):
        # as the inverse of tonumber
        raise NotImplementedError


class DigitConverter(BaseConverter):
    """DigitConverter < BaseConverter

    real number <-> list of digits

    Arguments:
        base: uint, base of system
        exponent: int, 1.111 * base^exponent
        sign[None]: the sign of number

    Example:
    c = DigitConverter(10, 3)
    d = c.tolist(12.223, 6)
    print(d, '<->' ,c.tonumber(d))

    [0, 0, 1, 2, 2, 2] <-> 12.22
    """

    def __init__(self, base=2, exponent=1, sign=None):
        super().__init__()
        self.__base = base
        self.exponent = exponent
        self.sign = sign


    @property
    def base(self):
        return self.__base
    

    def __call__(self, lst):
        return self.tonumber(lst)


    def tonumber_sign(self, lst):
        if self.sign is None:
            return self(lst)
        return self.sign * self(lst)


    def tonumber(self, lst:Digits):
        """list -> number
        
        transform a list (or an iterable obj) to a number
        make sure all elements in lst < .base
        
        Arguments:
            lst {Iterable} -- a list of digits
        
        Returns:
            a number
        """
        # assert np.all(lst < self.base)
        res = sum(digit * self.base ** (self.exponent - k) for k, digit in enumerate(lst))
        return self.postprocess(res)

    def postprocess(self, x):
        return x


    def pretty(self, lst:Digits) -> str:
        return ' + '.join(f'{self.base}^{{{self.exponent - k}}}' if digit == 1 else f'{digit}*{self.base}^{{{self.exponent - k}}}'
            for k, digit in enumerate(lst) if digit !=0)


    def scientific(self, lst:Digits) -> str:
        # scientific notation
        if self.exponent == 0:
            return f"{lst[0]}.{' '.join(lst[1:])}" 
        elif self.exponent == 1:
            return f"{lst[0]}.{' '.join(lst[1:])} X {self.base}"
        else:
            return f"{lst[0]}.{' '.join(lst[1:])} X {self.base}^{self.exponent}"


    def isint(self, lst:Digits) -> bool:
        # `lst` represents an integer
        return np.all(digit == 0 for k, digit in enumerate(lst) if k > self.exponent)


    def tolist(self, num, L=8) -> Digits:
        """number -> list with length L
        
        The core of the code

        Arguments:
            num {number} -- the number will be converted
        
        Keyword Arguments:
            L {int} -- length of the list (default: {8})
        
        Returns:
            a list
        """

        b = self.base
        lst = []
        I = int(np.floor(num))
        D = num - I
        while True:
            q, r = divmod(I, b)
            lst = [r] + lst
            if q == 0:
                break
            else:
                I = q
        lst = [0] * (self.exponent + 1 - len(lst)) + lst
        while D > 0:
            num = D * b
            I = int(np.floor(num))
            D = num - I
            lst.append(I)
            ll = len(lst)
            if ll == L:
                return lst
            elif ll > L:
                while lst[-1] == 0 and ll>L:
                    lst.pop(-1)
                    ll -= 1
                return lst
        return lst + [0] * (L-len(lst))


    def fix_len(self, L=8):
        # redefine tolist method with a fixed length
        def g(obj, num):
            # obj.len = L
            return DigitConverter.tolist(obj, num, L=L)
        self.tolist = types.MethodType(g, self)


class BinaryConverter(DigitConverter):
    """
    Converter for binary system

    set base = 2
    """
    def __init__(self, *args, **kwargs):
        super().__init__(base=2, *args, **kwargs)


class IntegerConverter(DigitConverter):
    """
    converter for integers
    """

    def tonumber(self, lst):
        """list -> number
        
        transform a list (or an iterable obj) to a number
        make sure all elements in lst < .base
        
        Arguments:
            lst {Iterable} -- a list of digits
        
        Returns:
            a number
        """
        # assert np.all(lst < self.base)
        return toint(lst, base=self.base)

    def tolist(self, num, L=8):
        """int -> list with length L
        
        The core of the code

        Arguments:
            num {int} -- the number will be converted
        
        Keyword Arguments:
            L {int} -- length of the list (default: {8})
        
        Returns:
            a list
        """
        self.exponent = L - 1
        b = self.base
        lst = []

        while True:
            q, r = divmod(num, b)
            lst = [r] + lst
            if q == 0:
                break
            else:
                num = q
        return [0] * (L-len(lst)) + lst


class IntervalConverter(IntegerConverter):
    """Convert numbers in an interval
    
    Take base 2 as an example, map the number before converting
    n -> (n-lb)/(ub-lb)*2^L, with base 2.
    Finally, we should have
    lb --> [0,0,...0]
    ub --> [1,1,...1]
    
    Extends:
        IntegerConverter
    """

    def __init__(self, lb=0, ub=1, *args, **kwargs):
        """
        Keyword Arguments:
            lb {number} -- the lower bound of the interval (default: {0})
            ub {number} -- the upper bound (default: {1})
        """
        super().__init__(*args, **kwargs)
        self.lb = lb
        self.ub = ub
        self.h = ub-lb
        

    def tonumber(self, lst):
        """list -> number
        
        transform a list (or an iterable obj) to a number
        make sure all elements in lst < .base
        
        Arguments:
            lst {Iterable} -- a list of digits
        
        Returns:
            a number
        """
        # assert np.all(lst < self.base)
        res = super().tonumber(lst)
        N = self.base ** len(lst)
        return self.lb + self.h * res/N


    def tolist(self, num, L=8):
        """number -> list
        
        Arguments:
            num {number} -- the number will be converted
        
        Keyword Arguments:
            L {number} -- the length of list (default: {8})
        
        Returns:
            Iterable -- list of digits
        """
        # assert self.a <= num <= self.b
        N = self.base ** L
        num = int((num - self.lb)*N / (self.h))
        return super().tolist(num, L)


# define Converter of numbers 0~255
colorConverter = BinaryConverter(exponent=7)
f = lambda obj, x: int(super(BinaryConverter, obj).tonumber(x))
colorConverter.tonumber = types.MethodType(f, colorConverter)
colorConverter.fix_len(8)

# converter for the numbers on unit interval [0, 1] with default parameters.
unitIntervalConverter = IntervalConverter()


if __name__ == '__main__':
    print(f'color-converter: {colorConverter.tonumber([1,0,1,0,1,1,1,0])}<->{colorConverter.tolist(174)}')

    c = BinaryConverter(exponent=3)
    d = c.tolist(12.223, L=8)
    print(f'binary-converter: {d}<->{c.tonumber(d)}={c.pretty(d)}')

    c = IntervalConverter(lb=0, ub=10)
    d = c.tolist(2.4, L=8)
    print(f'[{c.lb},{c.ub}]-converter: {d}<->{c(d)} -> {c.pretty(d)}-th number')

    c = DigitConverter(base=16)
    d = c.tolist(2.4, L=8)
    print(f'16-converter: {d}<->{c(d)}={c.pretty(d)}')

