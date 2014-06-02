#!/usr/bin/env python
# -*- coding: utf-8 -*-

import errno
import flask
import md5
import mock
import os
import requests
import unittest
import hulk.utils
import hulk.application

from hulk.utils import build_filename, create_dataset_folder, load_original, \
    save_original, serve_file, record_file, get_dataset_folder
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
            response = load_original(FakeRequest())
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
                load_original(FakeRequest())

    def test_post_should_process_both_params_and_form_data(self):
        with mock.patch('requests.post') as patched_post:
            # fudge a requests.Response object
            class FakeResponse(object):
                status_code = 200
                text = 'foo bar'
            patched_post.return_value = FakeResponse()

            # fudge the request
            class FakeRequest(object):
                url = 'http://foo/baz'
                method = 'POST'
                args = mock.Mock()
                form = mock.Mock()
                def __init__(self):
                    self.args.to_dict = mock.Mock(return_value={'args':'mock'})
                    self.form.to_dict = mock.Mock(return_value={'form':'mock'})

            response = load_original(FakeRequest())

            # check the params and data are passed properly to requests
            patched_post.assert_called_with('http://foo/baz',
                data={'form':'mock'},params={'args':'mock'})

            # check our response value
            self.assertEqual(response, 'foo bar')

    def test_should_raise_exception_on_post_non_200(self):
        with mock.patch('requests.post') as patched_post:
            # fudge a requests.Response object
            class FakeResponse(object):
                status_code = 500
                text = 'foo bar'
            patched_post.return_value = FakeResponse()

            # fudge the request
            class FakeRequest(object):
                url = 'http://foo/baz'
                method = 'POST'
                args = mock.Mock()
                form = mock.Mock()
                def __init__(self):
                    self.args.to_dict = mock.Mock(return_value={'args':'mock'})
                    self.form.to_dict = mock.Mock(return_value={'form':'mock'})

            with self.assertRaises(IFuckedUpException):
                response = load_original(FakeRequest()) 

    def test_put_should_process_both_params_and_form_data(self):
        with mock.patch('requests.put') as patched_put:
            # fudge a requests.Response object
            class FakeResponse(object):
                status_code = 200
                text = 'foo bar'
            patched_put.return_value = FakeResponse()

            # fudge the request
            class FakeRequest(object):
                url = 'http://foo/baz'
                method = 'PUT'
                args = mock.Mock()
                form = mock.Mock()
                def __init__(self):
                    self.args.to_dict = mock.Mock(return_value={'args':'mock'})
                    self.form.to_dict = mock.Mock(return_value={'form':'mock'})

            response = load_original(FakeRequest())

            # check the params and data are passed properly to requests
            patched_put.assert_called_with('http://foo/baz',
                data={'form':'mock'},params={'args':'mock'})

            # check our response value
            self.assertEqual(response, 'foo bar')

    def test_should_raise_exception_on_put_non_200(self):
        with mock.patch('requests.put') as patched_put:
            # fudge a requests.Response object
            class FakeResponse(object):
                status_code = 500
                text = 'foo bar'
            patched_put.return_value = FakeResponse()

            # fudge the request
            class FakeRequest(object):
                url = 'http://foo/baz'
                method = 'PUT'
                args = mock.Mock()
                form = mock.Mock()
                def __init__(self):
                    self.args.to_dict = mock.Mock(return_value={'args':'mock'})
                    self.form.to_dict = mock.Mock(return_value={'form':'mock'})

            with self.assertRaises(IFuckedUpException):
                response = load_original(FakeRequest()) 


class TestSaveOriginal(unittest.TestCase):
    def test_should_write_file_to_disk(self):
        mock_open = mock.mock_open()

        # 'open' is technically in the namespace of the module
        # that you call it in (as a builtin)
        with mock.patch('hulk.utils.open', mock_open, create=True):
            save_original('foo/path', 'Some foo content.')
            mock_open.assert_called_once_with('foo/path', 'w')
            handle = mock_open()
            handle.write.assert_called_once_with('Some foo content.')

    def test_should_encode_unicode_content_to_utf8(self):
        mock_open = mock.mock_open()

        # 'open' is technically in the namespace of the module
        # that you call it in (as a builtin)
        with mock.patch('hulk.utils.open', mock_open, create=True):
            save_original('foo/path', u'y\u00f4')
            mock_open.assert_called_once_with('foo/path', 'w')
            handle = mock_open()
            handle.write.assert_called_once_with('y\xc3\xb4')


class TestServeFile(unittest.TestCase):

    def test_should_read_file_from_disk(self):
        with mock.patch('hulk.utils.open', mock.mock_open(read_data='bibble'), 
                create=True) as m:

            # set up a fake request to pass in
            class FakeRequest(object):
                mimetype = 'foo/bar'

            response = None
            with hulk.application.app.test_request_context('http://foo/bar'):
                # excercise the code
                response = serve_file(FakeRequest, 'some/path')

            # assert
            self.assertEqual(response.data, 'bibble')
            self.assertEqual(response.headers.get('Content-type'), 'foo/bar')


class TestRecordFile(unittest.TestCase):

    def test_should_create_dataset_file_when_missing(self):
        mock_open = mock.mock_open()
        with mock.patch('hulk.utils.open', mock_open, create=True):
            with mock.patch('os.path.exists') as exists:
                exists.return_value = False

                # excercise code
                record_file('foo-dataset', 'asdf', 'text/foo', 'http://foo')
                file_path = get_dataset_folder() + '/foo-dataset/dataset.json'

                # verify the test, would confirm the filename structure
                exists.assert_called_with(file_path)

                # yucky to bind to the inner functionality, but reliable
                mock_open.assert_any_call(file_path, 'w')
                mock_open.assert_any_call(file_path, 'r+')

                # prove that file.write() was called with the proper structure
                instance = mock_open()
                instance.write.assert_called_once_with(
                    '{"asdf": {"url": "http://foo", "content-type": "text/foo"}}')


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
