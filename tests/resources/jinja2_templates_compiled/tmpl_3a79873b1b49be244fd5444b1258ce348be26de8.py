from jinja2.runtime import missing

name = "template1.html"


def root(context, missing=missing):
    resolve = context.resolve_or_missing
    undefined = environment.undefined
    if 0:
        yield None
    l_0_message = resolve("message")
    yield str(undefined(name="message") if l_0_message is missing else l_0_message)


blocks = {}
debug_info = "1=12"
