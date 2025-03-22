#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser

config = configparser.ConfigParser()
config.read('config.ini')

site_name = config['site']['name']
base_url = "https://" + site_name
cache_dir = ".cache/"

db_name = config['database']['name']
