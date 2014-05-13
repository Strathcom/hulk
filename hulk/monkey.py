import requests
import logging
import os

from flask import session
from requests.models import Request, Response
from requests.compat import builtin_str
from hulk.utils import build_filename
from urlparse import urlparse


def patched_request(dataset):

    def patched(self, method, url,
            params=None,
            data=None,
            headers=None,
            cookies=None,
            files=None,
            auth=None,
            timeout=None,
            allow_redirects=True,
            proxies=None,
            hooks=None,
            stream=None,
            verify=None,
            cert=None):
        
        print method
        print url
        print params
        print data

        ### Borrowed directly from requests.Session.request ###
        method = builtin_str(method)

        # Create the Request.
        req = Request(
            method = method.upper(),
            url = url,
            headers = headers,
            files = files,
            data = data or {},
            params = params or {},
            auth = auth,
            cookies = cookies,
            hooks = hooks,
        )
        prep = self.prepare_request(req)

        # build filename
        values = params
        if data:
            values = dict(params.items() + data.items())

        parsed_url = urlparse(url)
        filename = build_filename(parsed_url.path, 
            values)

        # import pdb; pdb.set_trace()
        # try to load file
        full_path = os.path.join(dataset, parsed_url.hostname, 
            filename[0])

        logging.info('Attempting to load dataset: {}'.format(full_path))

        content = ''
        if os.path.exists(full_path):
            with open(full_path, 'r') as original_file:
                content = original_file.read()
                status_code = 200
                # TODO: mime-type
        else:
            status_code = 417
            content = 'The dataset {} could not be found.'.format(full_path)

        # TODO: fail violently on error?
        # Fudge the response object...
        resp = Response()
        resp.status_code = status_code
        resp.url = prep.url
        resp._content = content

        return resp

    return patched


def patch_requests(dataset):
    requests.Session.request = patched_request(dataset)
