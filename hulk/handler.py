import logging
import os

from urlparse import urlparse
from hulk.application import app
from hulk.utils import create_dataset_folder, build_filename, serve_file, \
    load_original, save_original, make_response, dataset_folder, record_file


logger = logging.getLogger()


def handle_request(request, path):
    """Handles the incoming request.
    """
    url = urlparse(request.url)
    original = request.url
    hostname = url.netloc
    dataset = app.config.get('dataset')
    logging.debug('URL requested {}'.format(url))
    # fix the path for consistency
    path = '/' + path

    # make sure the hostname folder exists
    create_dataset_folder(dataset_folder, '/'.join([dataset, hostname]))
    # create file name for http verbs
    hashname, full_query_name = build_filename(path, request.values)
    # check for file
    file_path = os.path.join(dataset_folder, dataset, hostname, hashname)
    logger.info('File path: {}'.format(file_path))

    # load file
    if os.path.exists(file_path):
        logging.info('File exists...')
        return serve_file(request, file_path)
    else:
        logging.info('File doesn\'t exist...')

        if app.config.get('load_origin'):
            logging.info('load_origin is set, loading original...')
            content = load_original(request)
            # TODO: maintain line-in-file <hash> <original-url>
            # TODO: prompt when overwriting files?
            save_original(file_path, content)

            # create a record of this file for later
            record_file(dataset, hashname, request.mimetype, ''.join(
                [hostname, full_query_name]))

            response = make_response(content)
            response.headers["Content-type"] = request.mimetype
            return response
        else:
            logging.info('load_origin NOT set, ignoring...')
            # TODO: write to 'missing.txt'

    return "nothing here", 404