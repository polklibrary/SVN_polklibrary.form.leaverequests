# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from polklibrary.form.leaverequests.testing import POLKLIBRARY_FORM_LEAVEREQUESTS_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that polklibrary.form.leaverequests is properly installed."""

    layer = POLKLIBRARY_FORM_LEAVEREQUESTS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if polklibrary.form.leaverequests is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'polklibrary.form.leaverequests'))

    def test_browserlayer(self):
        """Test that IPolklibraryFormLeaverequestsLayer is registered."""
        from polklibrary.form.leaverequests.interfaces import (
            IPolklibraryFormLeaverequestsLayer)
        from plone.browserlayer import utils
        self.assertIn(IPolklibraryFormLeaverequestsLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = POLKLIBRARY_FORM_LEAVEREQUESTS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['polklibrary.form.leaverequests'])

    def test_product_uninstalled(self):
        """Test if polklibrary.form.leaverequests is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'polklibrary.form.leaverequests'))

    def test_browserlayer_removed(self):
        """Test that IPolklibraryFormLeaverequestsLayer is removed."""
        from polklibrary.form.leaverequests.interfaces import IPolklibraryFormLeaverequestsLayer
        from plone.browserlayer import utils
        self.assertNotIn(IPolklibraryFormLeaverequestsLayer, utils.registered_layers())
