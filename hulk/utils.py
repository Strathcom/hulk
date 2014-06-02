import os
import logging
import requests
import logging
import urllib
import collections
import md5
import errno
import json

from flask import request, make_response
from hulk.exceptions import IFuckedUpException

CURRENT_DATASET_FILENAME = "/tmp/current_dataset.hulk"

logger = logging.getLogger()

dataset_folder = os.environ.get(
    "HULK_DATASET_BASE_DIR", 
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'datasets')
)


def create_dataset_folder(base_folder, child_folder):
    """Creates the dataset folder, recursively.
    """
    try:
        folder_path = os.path.join(base_folder, child_folder)
        logger.debug('Attempting to create dataset folder "{}"'.format(
            folder_path))
        os.makedirs(folder_path)
    except OSError as exception:
        if exception.errno == errno.EEXIST:
            logging.debug('...folder exists')
        else:
            raise


def build_filename(path, vals):
    # in order to make this loading of data consistent, we want to eliminate
    # all key/value pairs that have 'None' for values, and then alphabetize 
    # the keys. This will ensure a consistent cache name.
    values = {}

    if vals:    # may be None if no query string args
        values.update((k, v) for k, v in vals.iteritems() if v is not None)
        values = collections.OrderedDict(sorted(values.items()))                                 

    logger.debug('Using ordered values: {}'.format(values))

    query_string_parts = [path,]

    if values:
        query_string = urllib.urlencode(values)
        logger.debug(' - mashed all params and data into query string: {}'.format(
            query_string))
        query_string_parts.append('?')
        query_string_parts.append(query_string)

    name_to_hash = ''.join(query_string_parts)

    hashed = md5.new(name_to_hash).hexdigest()
    logger.debug('filename before: {}'.format(name_to_hash))
    logger.debug('filename after: {}'.format(hashed))
    return hashed, name_to_hash


def load_original(request):
    logger.debug('loading original request for {}'.format(request))

    # todo: using 'requests' here, check and see if the remote host is
    # localhost, we may be running this in the same environment

    if request.method == 'GET':
        req = requests.get(request.url)

        if req.status_code != 200:
            raise IFuckedUpException(
                'Could\'t load the original data for {}'.format(request))

        logger.debug('success!')
        return req.text

    if request.method == 'POST':
        params = request.args.to_dict()
        data = request.form.to_dict()

        logger.debug('posting with params: {}'.format(params))
        logger.debug('posting with data: {}'.format(data))
        req = requests.post(request.url, data=data, params=params)

        if req.status_code != 200:
            raise IFuckedUpException(
                'Could\'t load the original data for {}'.format(request))

        logger.debug('success!')
        return req.text

    if request.method == 'PUT':
        # we have to parse out the data into a dict for proxying
        # eg: we have foo=bar&this=that
        params = request.args.to_dict()
        data = request.form.to_dict()

        logger.debug('putting with params: {}'.format(params))
        logger.debug('putting with data: {}'.format(data))
        req = requests.put(request.url, data=data, params=params)
        
        if req.status_code != 200:
            raise IFuckedUpException(
                'Could\'t load the original data for {}'.format(request))

        logger.debug('success!')
        return req.text
        
    # raise Exception('We don\'t handle that method type.')


def get_dataset_folder():
    return dataset_folder


def save_original(path, content):
    logger.debug('writing file {}'.format(path))
    with open(path, 'w') as original:
        original.write(content.encode('utf-8'))
    logger.debug('file written!')


def serve_file(request, path):
    logging.debug('serving file from disk {}'.format(path))
    response = make_response(open(path).read())
    response.headers["Content-type"] = request.mimetype
    return response


def record_file(dataset, hashname, content_type, full_url):
    filename = 'dataset.json'
    file_path = os.path.join(dataset_folder, dataset, filename)

    # create the file if not there
    if not os.path.exists(file_path):
        open(file_path, 'w').close()

    record = {}
    with open(file_path, 'r+') as infile:
        content = infile.read()
        if content:
            record = json.loads(content)
            infile.seek(0)
            infile.truncate()

        record[hashname] = {
            'content-type': content_type,
            'url': full_url
        }

        infile.write(json.dumps(record))
