# Copyright 2011 webapp2 AUTHORS.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest

from google.appengine.ext import testbed
from google.appengine.ext.ndb import model, tasklets

import webapp2


def main():
    unittest.main()


def check_webob_version(minimum_version):
    try:
        # WebOb < 1.0 (App Engine SDK).
        return 0.96 >= minimum_version
    except ImportError:
        # WebOb >= 1.0.
        return 1.0 <= minimum_version


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        """Set up the test framework.

        Service stubs are available for the following services:

        - Datastore (use init_datastore_v3_stub)
        - Memcache (use init_memcache_stub)
        - Task Queue (use init_taskqueue_stub)
        - Images (only for dev_appserver; use init_images_stub)
        - URL fetch (use init_urlfetch_stub)
        - User service (use init_user_stub)
        - XMPP (use init_xmpp_stub)
        """
        # First, create an instance of the Testbed class.
        self.testbed = testbed.Testbed()

        # Then activate the testbed, which prepares the service stubs for use.
        self.testbed.activate()

        # To set custom env vars, pass them as kwargs *after* activate().
        # self.setup_env()

        # Next, declare which service stubs you want to use.
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_user_stub()

        # Only when testing ndb.
        self.reset_kind_map()
        self.setup_context_cache()

    def tearDown(self):
        # This restores the original stubs so that tests do not interfere
        # with each other.
        self.testbed.deactivate()
        # Clear thread-local variables.
        self.clear_globals()

    def reset_kind_map(self):
        model.Model._reset_kind_map()

    def setup_context_cache(self):
        """Set up the context cache.

        We only need cache active when testing the cache, so the default
        behavior is to disable it to avoid misleading test results. Override
        this when needed.
        """
        ctx = tasklets.get_context()
        ctx.set_cache_policy(False)
        ctx.set_memcache_policy(False)

    def clear_globals(self):
        webapp2._local.__release_local__()

    def register_model(self, name, cls):
        model.Model._kind_map[name] = cls
