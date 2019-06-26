##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Hookable object support
"""

class _py_hookable(object):
    __slots__ = ('_original', '_implementation')
    
    def __init__(self, *args, **kw):
        if len(args) == 0 and 'implementation' in kw:
            args = (kw.pop('implementation'),)
        if kw:
            raise TypeError('Unknown keyword arguments')
        if len(args) != 1:
            raise TypeError('Exactly one argument required')
        self._original = self._implementation = args[0]

    original = property(lambda self: self._original)
    implementation = property(lambda self: self._implementation)

    def sethook(self, new_callable):
        old, self._implementation = self._implementation, new_callable
        return old

    def reset(self):
        self._implementation = self._original

    def __call__(self, *args, **kw):
        return self._implementation(*args, **kw)

hookable = _py_hookable

try:
    from ._zope_hookable import hookable
except ImportError: #pragma NO COVER
    pass
