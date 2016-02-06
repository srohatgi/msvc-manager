#!/usr/bin/env python

import logging
import getopt
import sys
import boto3

class EB:

    def __init__(self):
        self.eb = boto3.client('elasticbeanstalk')

    def list_applications(self, env):
        for apps in self.eb.describe_applications().get('Applications'):
            app = apps.get('ApplicationName')
            app_env = self.app_env(app, env)
            logging.info("app_env: {}".format(app_env))

            self.list_configuration(app_env)
            self.list_values(app, app_env)

    def app_env(self, app, env):
        if app == 'dcp-360':
            app = 'dcp360'

        return '{}-{}'.format('dcp360', env)

    def list_configuration(self, app_env):
        response = self.eb.describe_configuration_options(EnvironmentName=app_env)

        for option in response.get('Options'):
            if option.get('UserDefined') == True:
                logging.info("name: {}".format(option.get('Name')))

    def list_values(self, app, app_env):
        response = self.eb.describe_configuration_settings(ApplicationName=app, EnvironmentName=app_env)

        for setting in response.get('ConfigurationSettings')[0].get('OptionSettings'):
            logging.info("setting: {}".format(setting))



class Q:

    def __init__(self):
        self.sqs = boto3.resource('sqs')

    def test(self):
        self.qinfo()
        self.qwrite('test')
        self.qread('test')

    def storage(env, layer):
        s3 = boto3.resource('s3')
        for bucket in s3.buckets.all():
            logging.info("bucket found: {name}".format(name=bucket.name))

    def qinfo(self):
        for q in self.sqs.queues.all():
            logging.info("queue {name} {url}".format(name=q.attributes['QueueArn'].split(':')[-1], url=q.url))

    def qwrite(self, qname):
        q = self.sqs.get_queue_by_name(QueueName=qname)
        response = q.send_message(MessageBody='boto3', MessageAttributes={
            'Author': {
                'StringValue': 'Daniel',
                'DataType': 'String'
            }
        })

        logging.info("message id: {id}".format(id=response.get('MessageId')))

    def qread(self, qname):
        q = self.sqs.get_queue_by_name(QueueName='test')

        for message in q.receive_messages(MessageAttributeNames=['Author']):
            if message.message_attributes is not None:
                author_name = message.message_attributes.get('Author').get('StringValue')
                logging.info("author name = {}".format(author_name))


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
                                   "he:l:",
                                   ["help", "env=", "layer="])
    except getopt.GetoptError as err:
        usage(err)

    env = 'dit'
    layer = 'pfm'

    for option, argument in opts:
        if option in ('-e', '--env'):
        	env = argument
        elif option in ('-l', '--layer'):
        	layer = argument
        elif option == '-h':
            usage(None)
        else:
            assert False, "unhandled option"

    eb = EB()

    eb.list_applications('dit')

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    main()
