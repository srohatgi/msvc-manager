#!/usr/bin/env python

import logging
import getopt
import sys
import boto3

class EB:

    def __init__(self, app, env):
        self.eb = boto3.client('elasticbeanstalk')
        self.app = app
        self.env = env
        self.app_env = self.build_app_env(app, env)

    def build_app_env(self, app, env):
        if app == 'dcp-360':
            app = 'dcp360'

        return '{}-{}'.format('dcp360', env)

    def list_configuration(self):
        response = self.eb.describe_configuration_options(EnvironmentName=self.app_env)

        for option in response.get('Options'):
            if option.get('UserDefined') == True:
                logging.info("name: {}".format(option.get('Name')))

    def list_values(self):
        d = {}
        response = self.eb.describe_configuration_settings(ApplicationName=self.app, EnvironmentName=self.app_env)

        for setting in response.get('ConfigurationSettings')[0].get('OptionSettings'):
            if setting.get('Namespace') == 'aws:elasticbeanstalk:application:environment':
                name = setting.get('OptionName')
                value = setting.get('Value')
                logging.info("setting: {} value: {}".format(name, value))
                d[name] = value

        return d


class MicroService:

    def __init__(self, name, env):
        self.name = name
        self.env = env
        self.props = {}

    def sync(self):
        eb = EB(self.name, self.env)
        self.props = eb.list_values()

        logging.info("service props: {}".format(self.props))

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

def usage(message):
    code = 0

    if message:
        logging.error(message)
        code = 1

    logging.info("usage: login.py [-h] -env=<dit|sit> -layer=<ui|pfm>")
    sys.exit(code)

def main():
    opts = None
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "he:s:",
                                   ["help", "service=", "env="])
    except getopt.GetoptError as err:
        usage(err)

    service = None
    env = 'dit'
    for option, argument in opts:
        if option in ('-s', '--service'):
        	service = argument
        elif option in ('-e', '--env'):
        	env = argument
        elif option == '-h':
            usage(None)
        else:
            assert False, "unhandled option"

    if service is None:
        logging.error("--service option required!")
        sys.exit(1)

    msvc = MicroService(service, env)
    msvc.sync()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    main()
