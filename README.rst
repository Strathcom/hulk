.. header:: **hulk**
.. sectnum::
.. |date| date:: %Y

.. contents:: Table of Contents
   :depth: 1
   :backlinks: None

Introduction
============
`hulk` is a big dumb proxy server for testing service-heavy applications. Designed for use with `requests` (and possibly `urllib`). `hulk` caches request data behind the scenes for later use in application testing.

Author
------
Aaron Fay

Status
------
Development

Documentation
-------------
See *Usage*.


Installation
============
Either pull down this repository or use the `Vagrantfile` provided in the repo.


Usage
=====

Vagrant
~~~~~~~
You're going to need [Vagrant](http://vagrantup.com) if you want to use the included `Vagrantfile`.

Quickstart:

    $ vagrant up
    $ vagrant ssh

The login should give you something that looks like this:

    Welcome to Ubuntu 12.04.1 LTS (GNU/Linux 3.2.0-32-generic x86_64)

     * Documentation:  https://help.ubuntu.com/

      System information as of Tue Jun 10 14:23:19 BRT 2014

      System load:  0.07              Processes:           71
      Usage of /:   13.0% of 7.87GB   Users logged in:     0
      Memory usage: 1%                IP address for eth0: 192.168.88.15
      Swap usage:   0%                IP address for eth1: 192.168.0.166

      Graph this data and manage this system at https://landscape.canonical.com/

    Last login: Wed Jun  4 18:42:19 2014 from 192.168.88.2

    To get started with hulk, run:
        $ workon hulk
        $ hulk -h

Follow the instructions (the last couple lines) to get started. Note that you'll
want the second IP address listed above to set as your `HTTP_PROXY` later. 


Hulk command line reference
---------------------------

    (hulk)vagrant@vagrant-ubuntu:~$ hulk -h
    Big dumb proxy server for testing service-heavy applications.

    Usage:
      hulk [--dataset=testing] [--load-origin] [--base-folder] [--debug]
      hulk (--help | -h)

    Options:
      --dataset=testing   The set of cached data to use [default: testing]
      --load-origin       Use this flag to populate new datasets
      --debug             Run hulk with debugging info
      --help -h           Show this screen.

The first time you run `hulk` you'll want to use the `--load-origin` flag to 
have `hulk` load the original service call data and cache it to disk.

    $ hulk --load-origin

Each request gets a hash assigned to it and is saved to the local file system 
in the original format under the `dataset` folder you've specified. Subsequent 
requests will use the cached file.

Datasets
--------
`datasets` allow you to have different sets of data for different scenarios, 
possible test suites or even different applications. To get started with a 
new dataset, run:

    $ hulk --load-origin --dataset=my-new-dataset

The new dataset `my-new-dataset` will be created in the `datasets` folder. To 
run hulk with the dataset in the future, just run:

    $ hulk --dataset=my-new-dataset

`HULK_DATASET_BASE_DIR`
~~~~~~~~~~~~~~~~~~~~~~~
By default, hulk creates a `datasets` folder relative to the hulk installation.
If you would like to change the location where the datasets get stored, you 
can set the `HULK_DATASET_BASE_DIR` environment variable. This should be an 
absolute path to where you want the datasets to be saved, for example:

    $ export HULK_DATASET_BASE_DIR=/tmp/datasets


Using `HTTP_PROXY`
------------------
Following the tradition of it's predecessors, the fantastic `requests` library
honors the `HTTP_PROXY` environment variable and will use the value specified
as the proxy server for all requests. For example, if you run your application 
like so:

    $ export HTTP_PROXY=http://192.168.0.166:6000 && run_my_application

There are a couple important things to note here:

 - you must specify the protocol (eg `http://`)
 - `hulk` runs on port `6000` by default

Now, you should be able to navigate your app and watch the hulk server load and
serve your service data.


Using the datasets without `hulk`
---------------------------------
There is also a decorator available to patch `requests` so you can utilize 
datasets in your test suite without running hulk: `hulk.monkey.with_dataset`.

This decorator can be used on a per-method or per-class basis. For example:

    from hulk.monkey import with_dataset
    import unittest
    import requests


    @with_dataset('my-ticket-1234')
    class SuperTestCase(unittest.TestCase)
        def setUp(self):
            pass

        def test_should_pass(self):
            """This service request will actually look for the data in your
            `datasets/my-ticket-1234/my-service.com/...` folder. If the folder
            or file for this specific response doesn't exist, you'll get a 404
            response code.
            """
            response = requests.get('http://my-service.com/some-data')
            self.assertEqual(response.status_code, 200)

*Note*: The class- and method-level decorators cannot be currently used together
in a stack-like fashion, meaning that if you use a class-level decorator, then
use a method-level decorator, `with_dataset` will not fall back to the 
class-level decorator. Currently it is recommended to use the decorator at the 
class level.

Tests
=====
To run the tests:

    $ nosetests --with-spec --spec-color --with-coverage --cover-package=hulk


Change Log
==========
 * 0.2.0: adds `with_dataset` decorator, class decorator support, and updated docs.
 * 0.1.0: initial version


Dev Notes
=========


Design Decisions
================


Roadmap
=======
 * load/save datasets in S3
 * test with urllib[1|2|3]
 * specify base_url
 * test decorators
 

.. footer:: Copyright |date| Strathcom Media