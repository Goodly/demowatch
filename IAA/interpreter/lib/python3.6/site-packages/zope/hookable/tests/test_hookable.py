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
"""Test the hookable support Extension
"""
import unittest

class PyHookableTests(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from zope.hookable import _py_hookable
        return _py_hookable(*args, **kw)

    def test_before_hook(self):
        def _foo():
            return 'FOO'
        hooked = self._callFUT(_foo)
        self.assertTrue(hooked.original is _foo)
        self.assertTrue(hooked.implementation is _foo)
        self.assertEqual(hooked(), 'FOO')

    def test_after_hook(self):
        def _foo():
            return 'FOO'
        def _bar():
            return 'BAR'
        hooked = self._callFUT(_foo)
        old = hooked.sethook(_bar)
        self.assertTrue(old is _foo)
        self.assertTrue(hooked.original is _foo)
        self.assertTrue(hooked.implementation is _bar)
        self.assertEqual(hooked(), 'BAR')

    def test_after_hook_and_reset(self):
        def _foo():
            return 'FOO'
        def _bar():
            return 'BAR'
        hooked = self._callFUT(_foo)
        old = hooked.sethook(_bar)
        hooked.reset()
        self.assertTrue(old is _foo)
        self.assertTrue(hooked.original is _foo)
        self.assertTrue(hooked.implementation is _foo)
        self.assertEqual(hooked(), 'FOO')

    def test_original_cannot_be_deleted(self):
        def _foo():
            return 'FOO'
        hooked = self._callFUT(_foo)
        def _try():
            del hooked.original
        self.assertRaises((TypeError, AttributeError), _try)

    def test_implementation_cannot_be_deleted(self):
        def _foo():
            return 'FOO'
        hooked = self._callFUT(_foo)
        def _try():
            del hooked.implementation
        self.assertRaises((TypeError, AttributeError), _try)

    def test_no_args(self):
        self.assertRaises(TypeError, self._callFUT)

    def test_too_many_args(self):
        def _foo():
            return 'FOO'
        self.assertRaises(TypeError, self._callFUT, _foo, _foo)

    def test_w_implementation_kwarg(self):
        def _foo():
            return 'FOO'
        hooked = self._callFUT(implementation=_foo)
        self.assertTrue(hooked.original is _foo)
        self.assertTrue(hooked.implementation is _foo)
        self.assertEqual(hooked(), 'FOO')

    def test_w_unknown_kwarg(self):
        def _foo():
            return 'FOO'
        self.assertRaises(TypeError, self._callFUT, nonesuch=_foo)


class HookableTests(PyHookableTests):

    def _callFUT(self, *args, **kw):
        from zope.hookable import hookable
        return hookable(*args, **kw)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PyHookableTests),
        unittest.makeSuite(HookableTests),
    ))
