# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import polklibrary.form.leaverequests


class PolklibraryFormLeaverequestsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=polklibrary.form.leaverequests)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'polklibrary.form.leaverequests:default')


POLKLIBRARY_FORM_LEAVEREQUESTS_FIXTURE = PolklibraryFormLeaverequestsLayer()


POLKLIBRARY_FORM_LEAVEREQUESTS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(POLKLIBRARY_FORM_LEAVEREQUESTS_FIXTURE,),
    name='PolklibraryFormLeaverequestsLayer:IntegrationTesting'
)


POLKLIBRARY_FORM_LEAVEREQUESTS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(POLKLIBRARY_FORM_LEAVEREQUESTS_FIXTURE,),
    name='PolklibraryFormLeaverequestsLayer:FunctionalTesting'
)


POLKLIBRARY_FORM_LEAVEREQUESTS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        POLKLIBRARY_FORM_LEAVEREQUESTS_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='PolklibraryFormLeaverequestsLayer:AcceptanceTesting'
)
