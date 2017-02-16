import os, sys

#enc, esc = sys.getfilesystemencoding(), 'surrogateescape'

def wsgi_to_bytes(s):
    return s.encode('iso-8859-1')

def make_server(host, port, app):
    pass #FIXME

def run_wsgi(application, environ, out):
    headers_set = []
    headers_sent = []

    def write(data):
        #out = sys.stdout.buffer

        if not headers_set:
             raise AssertionError("write() before start_response()")

        elif not headers_sent:
             # Before the first output, send the stored headers
             status, response_headers = headers_sent[:] = headers_set
             out.write(wsgi_to_bytes('HTTP/1.0: %s\r\n' % status))
             for header in response_headers:
                 out.write(wsgi_to_bytes('%s: %s\r\n' % header))
             out.write(wsgi_to_bytes('\r\n'))

        out.write(data)
        try:
            out.flush()
        except AttributeError:
            pass

    def start_response(status, response_headers, exc_info=None):
        if exc_info:
            try:
                if headers_sent:
                    # Re-raise original exception if headers sent
                    raise exc_info[1].with_traceback(exc_info[2])
            finally:
                exc_info = None     # avoid dangling circular ref
        elif headers_set:
            raise AssertionError("Headers already set!")

        headers_set[:] = [status, response_headers]

        # Note: error checking on the headers should happen here,
        # *after* the headers are set.  That way, if an error
        # occurs, start_response can only be re-called with
        # exc_info set.

        return write

    result = application(environ, start_response)
    try:
        for data in result:
            if data:    # don't send headers until body appears
                write(data)
        if not headers_sent:
            write(b'')   # send headers now if body was empty
    finally:
        if hasattr(result, 'close'):
            result.close()
