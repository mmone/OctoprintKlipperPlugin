# coding=utf-8

plugin_identifier = "klipper"

plugin_package = "octoprint_klipper"

plugin_name = "OctoKlipper"

plugin_version = "0.2.4"

plugin_description = """A plugin for OctoPrint to configure,control and monitor the Klipper 3D printer software."""

plugin_author = "Martin Muehlhaeuser"

plugin_author_email = "github@mmone.de"

plugin_url = "http://blog.mmone.de/2018/02/05/octoprint-plugin-for-klipper/"

plugin_license = "AGPLv3"

plugin_requires = []

plugin_additional_data = []

plugin_additional_packages = []

plugin_ignored_packages = []

additional_setup_parameters = {}

########################################################################################################################

from setuptools import setup

try:
	import octoprint_setuptools
except:
	print("Could not import OctoPrint's setuptools, are you sure you are running that under "
	      "the same python installation that OctoPrint is installed under?")
	import sys
	sys.exit(-1)

setup_parameters = octoprint_setuptools.create_plugin_setup_parameters(
	identifier=plugin_identifier,
	package=plugin_package,
	name=plugin_name,
	version=plugin_version,
	description=plugin_description,
	author=plugin_author,
	mail=plugin_author_email,
	url=plugin_url,
	license=plugin_license,
	requires=plugin_requires,
	additional_packages=plugin_additional_packages,
	ignored_packages=plugin_ignored_packages,
	additional_data=plugin_additional_data
)

if len(additional_setup_parameters):
	from octoprint.util import dict_merge
	setup_parameters = dict_merge(setup_parameters, additional_setup_parameters)

setup(**setup_parameters)
