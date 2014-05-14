import unittest
import md5
import errno
import mock
import requests
import os
import flask

from hulk.utils import build_filename, create_dataset_folder, load_original
from hulk.exceptions import IFuckedUpException


class TestLoadOriginal(unittest.TestCase):

    def test_should_return_response_text_on_get_request(self):
        with mock.patch('requests.get') as patched_get:
            # fudge a requests.Response object
            class FakeResponse(object):
                status_code = 200
                text = 'foo bar'
            patched_get.return_value = FakeResponse()

            # fudge the request
            class FakeRequest(object):
                url = 'http://foo/baz'
                method = 'GET'
            response = load_original(FakeRequest)
            self.assertEqual(response, 'foo bar')

    def test_should_raise_exception_on_get_non_200(self):
        with mock.patch('requests.get') as patched_get:
            # fudge a requests.Response object
            class FakeResponse(object):
                status_code = 500
                text = 'foo bar'
            patched_get.return_value = FakeResponse()

            # fudge the request
            class FakeRequest(object):
                url = 'http://foo/baz'
                method = 'GET'
            with self.assertRaises(IFuckedUpException):
                load_original(FakeRequest)


class TestBuildFilename(unittest.TestCase):

    def test_build_filename_should_alphabetize_params_and_build_url(self):
        path = 'some.place.com'
        query_params = {'foo': 'bar', 'a': 'value'}
        _, result_string = build_filename(path, query_params)
        self.assertEqual(result_string, 'some.place.com?a=value&foo=bar')

    def test_build_filename_should_return_hash_at_first_index(self):
        path = 'some.place.com'
        query_params = {'foo': 'bar', 'a': 'value'}
        result_hash, result_string = build_filename(path, query_params)
        self.assertEqual(result_hash, md5.new(result_string).hexdigest())


class TestCreateDatasetFolder(unittest.TestCase):

    def setUp(self):
        patcher = mock.patch('os.makedirs')
        self.addCleanup(patcher.stop)
        self.mock_os_makedirs = patcher.start()

    def tearDown(self):
        self.mock_os_makedirs.side_effect = None

    def test_should_make_folders_when_not_present(self):
        create_dataset_folder('base/folder', 'child-folder')
        self.mock_os_makedirs.assert_called_once()
        self.mock_os_makedirs.assert_called_with('base/folder/child-folder')

    def test_should_skip_folder_creation_when_present(self):
        test_exception = OSError('this is a test')
        test_exception.errno = errno.EEXIST
        self.mock_os_makedirs.side_effect = test_exception
        create_dataset_folder('foo', 'bar')
        # if we got this far, the test passed.
        self.assertTrue(True)

    def test_should_shit_the_bed_on_any_another_exception(self):
        test_exception = Exception('this is going to fail')
        self.mock_os_makedirs.side_effect = test_exception
        with self.assertRaises(Exception):
            create_dataset_folder('foo', 'bar')
