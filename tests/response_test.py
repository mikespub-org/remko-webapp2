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

import six

import webapp2
from tests import test_base


class NoStringOrUnicodeConversion:
    pass


class StringConversion:
    def __str__(self):
        return "foo" if six.PY3 else b"foo"


class UnicodeConversion:
    def __str__(self):
        return "bar"


class TestResponse(test_base.BaseTestCase):
    def test_write(self):
        var_1 = NoStringOrUnicodeConversion()
        var_2 = StringConversion()
        var_3 = UnicodeConversion()

        rsp = webapp2.Response()
        rsp.write(var_1)
        rsp.write(var_2)
        rsp.write(var_3)
        self.assertEqual(rsp.body, webapp2._to_utf8(f"{var_1!r}foobar"))

        rsp = webapp2.Response()
        rsp.write(var_1)
        rsp.write(var_3)
        rsp.write(var_2)
        self.assertEqual(rsp.body, webapp2._to_utf8(f"{var_1!r}barfoo"))

        rsp = webapp2.Response()
        rsp.write(var_2)
        rsp.write(var_1)
        rsp.write(var_3)
        self.assertEqual(rsp.body, webapp2._to_utf8(f"foo{var_1!r}bar"))

        rsp = webapp2.Response()
        rsp.write(var_2)
        rsp.write(var_3)
        rsp.write(var_1)
        self.assertEqual(rsp.body, webapp2._to_utf8(f"foobar{var_1!r}"))

        rsp = webapp2.Response()
        rsp.write(var_3)
        rsp.write(var_1)
        rsp.write(var_2)
        self.assertEqual(rsp.body, webapp2._to_utf8(f"bar{var_1!r}foo"))

        rsp = webapp2.Response()
        rsp.write(var_3)
        rsp.write(var_2)
        rsp.write(var_1)
        self.assertEqual(rsp.body, webapp2._to_utf8(f"barfoo{var_1!r}"))

    def test_write2(self):
        rsp = webapp2.Response()
        rsp.charset = None
        rsp.write("foo")

        self.assertEqual(rsp.body, b"foo")
        self.assertEqual(rsp.charset, "utf-8")

        # test for python's 3 write bytestring
        rsp = webapp2.Response()
        rsp.charset = None
        rsp.write(b"foo")

        self.assertEqual(rsp.body, b"foo")

        rsp = webapp2.Response()
        rsp.charset = None
        rsp.write("föö")

        self.assertEqual(rsp.body, "föö".encode())

    def test_status(self):
        rsp = webapp2.Response()

        self.assertEqual(rsp.status, "200 OK")
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.status_message, "OK")

        rsp.status = "200 OK"
        self.assertEqual(rsp.status, "200 OK")
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.status_message, "OK")

        rsp.status_message = "Weee"
        self.assertEqual(rsp.status, "200 Weee")
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.status_message, "Weee")

        rsp.status = 404
        self.assertEqual(rsp.status, "404 Not Found")
        self.assertEqual(rsp.status_int, 404)
        self.assertEqual(rsp.status_message, "Not Found")

        rsp.status = "403 Wooo"
        self.assertEqual(rsp.status, "403 Wooo")
        self.assertEqual(rsp.status_int, 403)
        self.assertEqual(rsp.status_message, "Wooo")

        rsp.status_int = 500
        self.assertEqual(rsp.status, "500 Internal Server Error")
        self.assertEqual(rsp.status_int, 500)
        self.assertEqual(rsp.status_message, "Internal Server Error")

        self.assertRaises(TypeError, rsp._set_status, ())

    def test_has_error(self):
        rsp = webapp2.Response()
        self.assertFalse(rsp.has_error())
        rsp.status = 400
        self.assertTrue(rsp.has_error())
        rsp.status = 404
        self.assertTrue(rsp.has_error())
        rsp.status = 500
        self.assertTrue(rsp.has_error())
        rsp.status = 200
        self.assertFalse(rsp.has_error())
        rsp.status = 302
        self.assertFalse(rsp.has_error())

    def test_wsgi_write(self):
        res = []

        def write(status, headers, body):
            return res.extend([status, headers, body])

        def start_response(status, headers):
            return lambda body: write(status, headers, body)

        rsp = webapp2.Response(body="Page not found!", status=404)
        rsp.wsgi_write(start_response)

        rsp = webapp2.Response(status=res[0], body=res[2], headers=res[1])
        self.assertEqual(rsp.status, "404 Not Found")
        self.assertEqual(rsp.body, b"Page not found!")

        """
        # webob >= 1.0
        self.assertEqual(res, [
            '404 Not Found',
            [
                ('Content-Type', 'text/html; charset=utf-8'),
                ('Cache-Control', 'no-cache'),
                ('Expires', 'Fri, 01 Jan 1990 00:00:00 GMT'),
                ('Content-Length', '15')
            ],
            'Page not found!'
        ])
        """

    def test_get_all(self):
        rsp = webapp2.Response()
        rsp.headers.add("Set-Cookie", "foo=bar;")
        rsp.headers.add("Set-Cookie", "baz=ding;")

        self.assertEqual(rsp.headers.get_all("set-cookie"), ["foo=bar;", "baz=ding;"])

        rsp = webapp2.Response()
        rsp.headers = {"Set-Cookie": "foo=bar;"}
        self.assertEqual(rsp.headers.get_all("set-cookie"), ["foo=bar;"])

    def test_add_header(self):
        rsp = webapp2.Response()
        rsp.headers.add_header("Content-Disposition", "attachment", filename="bud.gif")
        self.assertEqual(
            rsp.headers.get("content-disposition"), 'attachment; filename="bud.gif"'
        )

        rsp = webapp2.Response()
        rsp.headers.add_header("Content-Disposition", "attachment", filename=None)
        self.assertEqual(rsp.headers.get("content-disposition"), "attachment; filename")

        rsp = webapp2.Response()
        rsp.headers.add_header("Set-Cookie", "", foo="")
        self.assertEqual(rsp.headers.get_all("set-cookie"), ["; foo"])

        rsp = webapp2.Response()
        rsp.headers.add_header("Set-Cookie", "", foo=";")
        self.assertEqual(rsp.headers.get_all("set-cookie"), ['; foo=";"'])

    # Tests from Python source: wsgiref.headers.Headers
    def test_headers_MappingInterface(self):
        rsp = webapp2.Response()
        test = [("x", "y")]
        self.assertEqual(len(rsp.headers), 3)
        rsp.headers = test[:]
        self.assertEqual(len(rsp.headers), 1)
        self.assertEqual(list(rsp.headers.keys()), ["x"])
        self.assertEqual(list(rsp.headers.values()), ["y"])
        self.assertEqual(list(rsp.headers.items()), test)
        rsp.headers = test
        self.assertFalse([] is test)  # must be copy!

        rsp = webapp2.Response()
        h = rsp.headers
        # this doesn't raise an error in wsgiref.headers.Headers
        # del h['foo']

        h["Foo"] = "bar"
        for m in h.has_key, h.__contains__, h.get, h.get_all, h.__getitem__:
            self.assertTrue(m("foo"))
            self.assertTrue(m("Foo"))
            self.assertTrue(m("FOO"))
            # this doesn't raise an error in wsgiref.headers.Headers
            # self.assertFalse(m('bar'))

        self.assertEqual(h["foo"], "bar")
        h["foo"] = "baz"
        self.assertEqual(h["FOO"], "baz")
        self.assertEqual(h.get_all("foo"), ["baz"])

        self.assertEqual(h.get("foo", "whee"), "baz")
        self.assertEqual(h.get("zoo", "whee"), "whee")
        self.assertEqual(h.setdefault("foo", "whee"), "baz")
        self.assertEqual(h.setdefault("zoo", "whee"), "whee")
        self.assertEqual(h["foo"], "baz")
        self.assertEqual(h["zoo"], "whee")

    def test_headers_RequireList(self):
        def set_headers():
            rsp = webapp2.Response()
            rsp.headers = "foo"
            return rsp.headers

        self.assertRaises(TypeError, set_headers)

    def test_headers_Extras(self):
        rsp = webapp2.Response()
        rsp.headers = []
        h = rsp.headers
        self.assertEqual(str(h), "\r\n")

        h.add_header("foo", "bar", baz="spam")
        self.assertEqual(h["foo"], 'bar; baz="spam"')
        self.assertEqual(str(h), 'foo: bar; baz="spam"\r\n\r\n')

        h.add_header("Foo", "bar", cheese=None)
        self.assertEqual(h.get_all("foo"), ['bar; baz="spam"', "bar; cheese"])

        self.assertEqual(
            str(h), 'foo: bar; baz="spam"\r\n' "Foo: bar; cheese\r\n" "\r\n"
        )


class TestReturnResponse(unittest.TestCase):
    def test_function_that_returns_response(self):
        def myfunction(request, *args, **kwargs):
            return webapp2.Response("Hello, custom response world!")

        app = webapp2.WSGIApplication(
            [
                ("/", myfunction),
            ]
        )

        req = webapp2.Request.blank("/")
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.body, b"Hello, custom response world!")

    def test_function_that_returns_string(self):
        def myfunction(request, *args, **kwargs):
            return "Hello, custom response world!"

        app = webapp2.WSGIApplication(
            [
                ("/", myfunction),
            ]
        )

        def custom_dispatcher(router, request, response):
            response_str = router.default_dispatcher(request, response)
            return request.app.response_class(response_str)

        app.router.set_dispatcher(custom_dispatcher)

        req = webapp2.Request.blank("/")
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.body, b"Hello, custom response world!")

    def test_function_that_returns_tuple(self):
        def myfunction(request, *args, **kwargs):
            return "Hello, custom response world!", 404

        app = webapp2.WSGIApplication(
            [
                ("/", myfunction),
            ]
        )

        def custom_dispatcher(router, request, response):
            response_tuple = router.default_dispatcher(request, response)
            return request.app.response_class(*response_tuple)

        app.router.set_dispatcher(custom_dispatcher)

        req = webapp2.Request.blank("/")
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 404)
        self.assertEqual(rsp.body, b"Hello, custom response world!")

    def test_handle_exception_that_returns_response(self):
        class HomeHandler(webapp2.RequestHandler):
            def get(self, **kwargs):
                raise TypeError()

        app = webapp2.WSGIApplication(
            [
                webapp2.Route("/", HomeHandler, name="home"),
            ]
        )
        app.error_handlers[500] = "tests.resources.handlers.handle_exception"

        req = webapp2.Request.blank("/")
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.body, b"Hello, custom response world!")

    def test_return_is_not_wsgi_app(self):
        class HomeHandler(webapp2.RequestHandler):
            def get(self, **kwargs):
                return ""

        app = webapp2.WSGIApplication(
            [
                webapp2.Route("/", HomeHandler, name="home"),
            ],
            debug=False,
        )

        req = webapp2.Request.blank("/")
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 500)


if __name__ == "__main__":
    unittest.main()
