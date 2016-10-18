#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Import flow cell through the Flowcelltool API"""

import argparse
import getpass
import os
import sys
import urllib
import xml.etree.ElementTree as ET

import coreapi
from coreapi.compat import b64encode
import coreapi.codecs

#: File name for run parameters
RUN_PARAMETERS_XML = 'runParameters.xml'
#: File name for run infos
RUN_INFO_XML = 'RunInfo.xml'
#: File name for RTA Configuration
RTA_CONFIGURATION_XML = 'RTAConfiguration.xml'

#: Name of environment variable for username
ENV_USER = 'FLOWCELLTOOL_USER'
#: Name of environment variable for password
ENV_PASSWORD = 'FLOWCELLTOOL_PASSWORD'
#: URL to API
ENV_APIURL = 'FLOWCELLTOOL_APIURL'


class BaseImporter:
    """Base class for importing"""

    def __init__(self, args):
        #: Program arguments
        self.args = args
        self._load_xml()
        self._get_auth_info()

    def _load_xml(self):
        #: ETree for runParameters.xml
        self.run_parameters = ET.parse(os.path.join(
            self.args.flowcell_dir, RUN_PARAMETERS_XML))
        #: ETree for RTAConfiguration.xml
        self.rta_configuration = ET.parse(os.path.join(
            self.args.flowcell_dir, RUN_PARAMETERS_XML))
        #: ETree for runInfo.xml
        self.run_info = ET.parse(os.path.join(
            self.args.flowcell_dir, RUN_INFO_XML))

    def _get_auth_info(self):
        #: URL for API
        self.api_url = self.args.api_url or os.getenv(ENV_APIURL)
        if not self.api_url:
            raise Exception('Empty API URL (env: {})'.format(ENV_APIURL))
        #: User name for login
        self.user = self.args.user or os.getenv(ENV_USER)
        if not self.user:
            raise Exception('Empty user (env: {})'.format(ENV_USER))
        #: Password for login
        self.password = self.args.password or os.getenv(ENV_PASSWORD)
        if not self.password:
            raise Exception('Empty password (env: {})'.format(ENV_PASSWORD))

    def run(self):
        params = self._build_flowcell_info()
        params['libraries'] = []
        decoders = [coreapi.codecs.CoreJSONCodec(), coreapi.codecs.JSONCodec()]
        client = coreapi.Client(
            decoders=decoders,
            transports=[self._build_auth_transport()])
        schema = client.get(self.api_url)
        print(schema)
        lst = client.action(schema, ['flow_cells', 'list'])#, params=params)
        print(lst)

    def _build_auth_transport(self):
        credentials_string = '{}:{}'.format(self.user, self.password)
        header = 'Basic ' + b64encode(credentials_string)
        parsed = urllib.parse.urlparse(self.api_url)
        domain = parsed.netloc.split(':', 1)[0]
        return coreapi.transports.HTTPTransport(credentials={domain: header})

    def _build_flowcell_info(self):
        return {
            'name': self._get_name(),
            'num_lanes': self._get_num_lanes(),
            'status': 'initial',
            'operator': self.args.operator,
            'is_paired': self._get_is_paired(),
            'index_read_count': self._get_index_read_count(),
            'rta_version': self._get_rta_version(),
            'read_length': self._get_read_length(),
        }

    def _get_name(self):
        """Return flow cell name"""
        return self.rta_configuration.find('.//RunID').text

    def _get_num_lanes(self):
        """Return number of lanes"""
        return int(self.run_info.find('.//FlowcellLayout').attrib['LaneCount'])

    def _get_is_paired(self):
        """Return whether is paired-end sequencing or not"""
        return self.run_parameters.find('.//Read2').text != '0'

    def _get_index_read_count(self):
        """Return number of index reads"""
        if self.run_parameters.find('.//IndexRead2').text != '0':
            return 2
        elif self.run_parameters.find('.//IndexRead1').text != '0':
            return 1
        else:
            return 0

    def _get_rta_version(self):
        """Return RTA version"""
        return int(self.run_parameters.find(
            './/RTAVersion').text.split('.', 1)[0])

    def _get_read_length(self):
        """Return read length"""
        return int(self.run_parameters.find('.//Read1').text)


class V1Importer(BaseImporter):
    """Importer for RTA v1 flow cells"""



class V2Importer(BaseImporter):
    """Importer for RTA v2 flow cells"""


def create_importer(args):
    """Instantiate correct BaseImporter sub class for flowcell dir"""
    path_xml = os.path.join(args.flowcell_dir, RUN_PARAMETERS_XML)
    tree = ET.parse(path_xml)
    rta_version = tree.find('.//RTAVersion').text
    if rta_version.startswith('1.'):
        return V1Importer(args)
    else:
        return V2Importer(args)


def run(args):
    """Entry point after command line parsing"""
    importer = create_importer(args)
    import pprint; pprint.pprint(importer.run(), indent=2)


def main(argv=None):
    """Entry point for command line parsing"""
    parser = argparse.ArgumentParser()

    parser.add_argument('--flowcell-dir', required=True, type=str,
                        help='Path to flowcell machine directory')
    parser.add_argument('--operator', required=True, type=str,
                        help='Name of the operator')
    parser.add_argument('--api-url', required=False, type=str,
                        help='URL to API')
    parser.add_argument('--user', required=False, type=str,
                        help='User name')
    parser.add_argument('--password-prompt', required=False, default=False,
                        action='store_true', help='Prompt for password')

    args = parser.parse_args(argv)

    args.password = None
    if args.password_prompt:
        args.password = getpass.getpass()

    return run(args)


if __name__ == '__main__':
    sys.exit(main())
