import sys
import requests
import logging
import os
from urlparse import urlparse

from flask import session
from requests.models import Request, Response
from requests.compat import builtin_str
from hulk.utils import build_filename, dataset_folder, CURRENT_DATASET_FILENAME

DEFAULT_DATASET = os.environ.get("HULK_DATASET", "default")

def set_default_dataset(dataset):
    """
    Sets the default dataset. Typically called during initialization of the 
    hosting application.
    """

    global DEFAULT_DATASET      # TODO: Not certain if this is a good way to do 
    DEFAULT_DATASET = dataset   # this...

def patched_request():

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
        values = params or {}
        if data:
            values.update(data)

        parsed_url = urlparse(url)
        filename = build_filename(parsed_url.path, values)

        # determine which dataset to use
        dataset = None

        try:
            with open(CURRENT_DATASET_FILENAME, "r") as f:
                dataset = f.read().strip()  # NOTE! `dataset` may be set to ""
        except IOError:
            pass

        if not dataset:
            dataset = DEFAULT_DATASET

        # try to load file
        full_path = os.path.join(dataset_folder, dataset, parsed_url.hostname, 
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


def patch_requests():
    requests.Session.request = patched_request()

def with_dataset(dataset_name, print_on_call=True):
    """
    This decorator wraps a patch_requests() call around the associated 
    function. When that function is called we will change the dataset that is 
    being injected by hulk. Once the function returns, we revert to the 
    previous dataset.

    :param dataset_name: The name of the dataset (folder underneath the hulk 
        base directory) to use for this function call.

    :param print_on_call: If True then the name of the dataset will be printed
        out. Helpful when the test runner is running the verbose flag.
    """
    
    def instantiate_func(original_func):

        def wrapped_func(*a, **kw):

            if print_on_call: #"-v" in sys.argv:
                sys.stdout.write('(dataset: ' + dataset_name + ') ')
                sys.stdout.flush()

            # First, signal to hulk to switch to the correct dataset

            with open(CURRENT_DATASET_FILENAME, "w") as current_dataset:
                current_dataset.write(dataset_name)

            return_value = original_func(*a, **kw)    # Now try calling the test

            # Lastly, signal to hulk to switch to the original dataset

            with open(CURRENT_DATASET_FILENAME, "w") as current_dataset:
                current_dataset.write("")

            return return_value     # Annnddd, we're done.

        return wrapped_func

    return instantiate_func
