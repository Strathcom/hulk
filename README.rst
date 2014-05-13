.. header:: **hulk**
.. sectnum::
.. |date| date:: %Y

.. contents:: Table of Contents
   :depth: 1
   :backlinks: None

Introduction
============
`hulk` is a big dummy proxy server for testing service-heavy applications. Designed for use with `requests` (and possibly `urllib`).

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
Just run `pip install hulk` to install the project.


Usage
=====
To get started, simply run:

    $ hulk

You'll want to set the environment variable `HTTP_PROXY` to the server where you're running `hulk`. This may be your local machine, a vagrant box, or otherwise.

The first time you run `hulk` you'll want to use the `--load-origin` flag to have the server proxy service requests to the real services.

    $ hulk --load-origin

Each request gets a hash assigned to it and is saved to the local file system in the original format. Subsequent requests will use the cached file.

Datasets
--------
`datasets` allow you to have different sets of data for different scenarios, possible test suites or even different applications. To get started with a new dataset, run:

    $ hulk --load-origin --dataset=my-new-dataset

The new dataset `my-new-dataset` will be created in the `datasets` folder. To run hulk with the dataset in the future, just run:

    $ hulk --dataset=my-new-dataset


For help:

    $ hulk -h

Tests
=====


Change Log
==========
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