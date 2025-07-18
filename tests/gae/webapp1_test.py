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

import test_base
from google.appengine.ext import webapp

import webapp2


# Old WSGIApplication, new RequestHandler.
class NewStyleHandler(webapp2.RequestHandler):
    def get(self, text):
        self.response.out.write(text)


app = webapp.WSGIApplication(
    [
        (r"/test/(.*)", NewStyleHandler),
    ]
)


# New WSGIApplication, old RequestHandler.
class OldStyleHandler(webapp.RequestHandler):
    def get(self, text):
        self.response.out.write(text)


class OldStyleHandler2(webapp.RequestHandler):
    def get(self, text=None):
        self.response.out.write(text)


class OldStyleHandlerWithError(webapp.RequestHandler):
    def get(self, text):
        raise ValueError()

    def handle_exception(self, e, debug):
        self.response.set_status(500)
        self.response.out.write("ValueError!")


app2 = webapp2.WSGIApplication(
    [
        (r"/test/error", OldStyleHandlerWithError),
        (r"/test/(.*)", OldStyleHandler),
        webapp2.Route(r"/test2/<text>", OldStyleHandler2),
    ]
)


class TestWebapp1(test_base.BaseTestCase):
    def test_old_app_new_handler(self):
        req = webapp2.Request.blank("/test/foo")
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.body, "foo")

        req = webapp2.Request.blank("/test/bar")
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.body, "bar")

        self.assertTrue(issubclass(OldStyleHandler, webapp.RequestHandler))

    def test_new_app_old_handler(self):
        req = webapp2.Request.blank("/test/foo")
        rsp = req.get_response(app2)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.body, "foo")

        req = webapp2.Request.blank("/test/bar")
        rsp = req.get_response(app2)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.body, "bar")

    def test_new_app_old_handler_405(self):
        req = webapp2.Request.blank("/test/foo")
        req.method = "POST"
        rsp = req.get_response(app2)
        self.assertEqual(rsp.status_int, 405)
        self.assertEqual(rsp.headers.get("Allow"), "GET")

    def test_new_app_old_handler_405_2(self):
        app2.allowed_methods = list(app2.allowed_methods) + ["NEW_METHOD"]
        req = webapp2.Request.blank("/test/foo")
        req.method = "NEW_METHOD"
        rsp = req.get_response(app2)
        self.assertEqual(rsp.status_int, 405)

    def test_new_app_old_handler_501_2(self):
        req = webapp2.Request.blank("/test/foo")
        req.method = "WHATMETHODISTHIS"
        rsp = req.get_response(app2)
        self.assertEqual(rsp.status_int, 501)

    def test_new_app_old_handler_with_error(self):
        req = webapp2.Request.blank("/test/error")
        rsp = req.get_response(app2)
        self.assertEqual(rsp.status_int, 500)
        self.assertEqual(rsp.body, "ValueError!")

    def test_new_app_old_kwargs(self):
        req = webapp2.Request.blank("/test2/foo")
        rsp = req.get_response(app2)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.body, "foo")

    def test_unicode_cookie(self):
        """see
        http://stackoverflow.com/questions/6839922/unicodedecodeerror-is-raised-when-getting-a-cookie-in-google-app-engine
        """
        import urllib

        # This is the value we want to set.
        initial_value = "äëïöü"
        # WebOb version that comes with SDK doesn't quote cookie values.
        # So we have to do it.
        quoted_value = urllib.quote(initial_value.encode("utf-8"))

        rsp = webapp.Response()
        rsp.headers["Set-Cookie"] = f"app={quoted_value}; Path=/"

        cookie = rsp.headers.get("Set-Cookie")
        req = webapp.Request.blank("/", headers=[("Cookie", cookie)])

        # The stored value is the same quoted value from before.
        stored_value = req.cookies.get("app")
        self.assertEqual(stored_value, quoted_value)

        # And we can get the initial value unquoting and decoding.
        final_value = urllib.unquote(stored_value.encode("utf-8")).decode("utf-8")
        self.assertEqual(final_value, initial_value)


if __name__ == "__main__":
    test_base.main()
