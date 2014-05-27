import requests
import logging
import os

from flask import session
from requests.models import Request, Response
from requests.compat import builtin_str
from hulk.utils import build_filename
from urlparse import urlparse

CURRENT_DATASET = None # FIXME: This should be more robust... much more.

def patched_request(dataset):

    global CURRENT_DATASET

    CURRENT_DATASET = dataset

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

def with_dataset(dataset_name):
    """
    This decorator wraps a patch_requests() call around the associated function. When that function is called we will
    change the data set that is being injected by hulk. Once the function returns, we revert to the previous dataset.
    """
    
    def instantiate_func(original_func):

        def wrapped_func(*a, **kw):
            print "======================================== I WAS JUST IN WRAPPED_FUNC()"
            print "CURRENT_DATASET", CURRENT_DATASET
            print 'dataset_name', dataset_name

            previous_dataset = CURRENT_DATASET
            patch_requests(dataset_name)
            return_value = original_func(*a, **kw)
            patch_requests(previous_dataset)
            return return_value

        return wrapped_func

    return instantiate_func
