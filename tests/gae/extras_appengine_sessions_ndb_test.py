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

from google.appengine.api import memcache

import webapp2
from tests.gae import test_base
from webapp2_extras import sessions
from webapp2_extras.appengine import sessions_ndb

app = webapp2.WSGIApplication(
    config={
        "webapp2_extras.sessions": {
            "secret_key": "my-super-secret",
        },
    }
)


class TestNdbSession(test_base.BaseTestCase):
    # factory = sessions_ndb.DatastoreSessionFactory

    def setUp(self):
        super().setUp()
        self.register_model("Session", sessions_ndb.Session)

    def test_get_save_session(self):
        # Round 1 -------------------------------------------------------------

        req = webapp2.Request.blank("/")
        req.app = app
        store = sessions.SessionStore(req)

        session = store.get_session(backend="datastore")

        rsp = webapp2.Response()
        # Nothing changed, we want to test anyway.
        store.save_sessions(rsp)

        session["a"] = "b"
        session["c"] = "d"
        session["e"] = "f"

        store.save_sessions(rsp)

        # Round 2 -------------------------------------------------------------

        cookies = rsp.headers.get("Set-Cookie")
        req = webapp2.Request.blank("/", headers=[("Cookie", cookies)])
        req.app = app
        store = sessions.SessionStore(req)

        session = store.get_session(backend="datastore")
        self.assertEqual(session["a"], "b")
        self.assertEqual(session["c"], "d")
        self.assertEqual(session["e"], "f")

        session["g"] = "h"

        rsp = webapp2.Response()
        store.save_sessions(rsp)

        # Round 3 -------------------------------------------------------------

        cookies = rsp.headers.get("Set-Cookie")
        req = webapp2.Request.blank("/", headers=[("Cookie", cookies)])
        req.app = app
        store = sessions.SessionStore(req)

        session = store.get_session(backend="datastore")
        self.assertEqual(session["a"], "b")
        self.assertEqual(session["c"], "d")
        self.assertEqual(session["e"], "f")
        self.assertEqual(session["g"], "h")

        # Round 4 -------------------------------------------------------------

        # For this attempt we don't want the memcache backup.
        sid = session.container.sid
        memcache.delete(sid)

        cookies = rsp.headers.get("Set-Cookie")
        req = webapp2.Request.blank("/", headers=[("Cookie", cookies)])
        req.app = app
        store = sessions.SessionStore(req)

        session = store.get_session(backend="datastore")
        self.assertEqual(session["a"], "b")
        self.assertEqual(session["c"], "d")
        self.assertEqual(session["e"], "f")
        self.assertEqual(session["g"], "h")

    def test_flashes(self):
        # Round 1 -------------------------------------------------------------

        req = webapp2.Request.blank("/")
        req.app = app
        store = sessions.SessionStore(req)

        session = store.get_session(backend="datastore")
        flashes = session.get_flashes()
        self.assertEqual(flashes, [])
        session.add_flash("foo")

        rsp = webapp2.Response()
        store.save_sessions(rsp)

        # Round 2 -------------------------------------------------------------

        cookies = rsp.headers.get("Set-Cookie")
        req = webapp2.Request.blank("/", headers=[("Cookie", cookies)])
        req.app = app
        store = sessions.SessionStore(req)

        session = store.get_session(backend="datastore")

        flashes = session.get_flashes()
        self.assertEqual(flashes, [("foo", None)])

        flashes = session.get_flashes()
        self.assertEqual(flashes, [])

        session.add_flash("bar")
        session.add_flash("baz", "important")

        rsp = webapp2.Response()
        store.save_sessions(rsp)

        # Round 3 -------------------------------------------------------------

        cookies = rsp.headers.get("Set-Cookie")
        req = webapp2.Request.blank("/", headers=[("Cookie", cookies)])
        req.app = app
        store = sessions.SessionStore(req)

        session = store.get_session(backend="datastore")

        flashes = session.get_flashes()
        self.assertEqual(flashes, [("bar", None), ("baz", "important")])

        flashes = session.get_flashes()
        self.assertEqual(flashes, [])

        rsp = webapp2.Response()
        store.save_sessions(rsp)

        # Round 4 -------------------------------------------------------------

        cookies = rsp.headers.get("Set-Cookie")
        req = webapp2.Request.blank("/", headers=[("Cookie", cookies)])
        req.app = app
        store = sessions.SessionStore(req)

        session = store.get_session(backend="datastore")
        flashes = session.get_flashes()
        self.assertEqual(flashes, [])

    def test_misc(self):
        s = sessions_ndb.Session(id="foo")
        key = s.put()

        s = key.get()
        self.assertEqual(s.data, None)


if __name__ == "__main__":
    test_base.main()
