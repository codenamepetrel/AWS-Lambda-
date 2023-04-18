#!/usr/bin/env python

import os
import logging
import traceback
import boto3
import json
import re

LOG_LEVELS = {"CRITICAL" : 50, "ERROR" : 40, "WARNING" : 30, "INFO" : 20, "DEBUG" : 10}

cw = boto3.client('cloudwatch')

def init_logging():
    #setup logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("botocore").setLevel(logging.WARNING)
    logging.getLogger("nose").setLevel(logging.WARNING)

    return logger

def setup_local_logging(logger):
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'

    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger

def set_log_level(logger, log_level = 'INFO'):
    if log_level in LOG_LEVELS:
        logger.setLevel(LOG_LEVELS[log_level])
    else:
        logger.setLevel(LOG_LEVELS['INFO'])

    return logger

def lambda_handler(event, context):
    try:
        global logger
        logger = init_logging()
        logger = set_log_level(logger, os.environ.get('log_level', 'INFO'))
        logger.debug("Running function lambda handler")
        logger.debug(json.dumps(event))
        detail_type = event['detail']['type']
        timestamp = event['time]']

        finding_type = 'unknown'
        resource = 'unknown'

        #create a capture groupe that masteches the finding type.
        #exapmle "UnauthorizedAccess" and resource, EC2

        matched = re.match('(?P<finding_type>[^:]+)(?P<resource>[^/]+)/', detail_type)
        if not matched:
            logger.debug('Unknown error matching detail type')
            exit(1)

            finding_type = matched.group(1)
            resource = matched.group(2)

            cw.put_metric_data(

                Namespace='PetrelAccount'
                MetricData=[ {
                    'MetricName': 'FindingsCount',
                    'Dimensions': [
                        {
                            'Name' : 'type'
                            'Value': finding_type
                        },
                        {
                            'Name': 'resource',
                            'Value': resource
                        }
                    ],
                    'Timestamp': timestamp,
                    'Value':1.0,
                    'Unit': 'None',
                    'StorageResolution': 60

                }]
            )
    except SystemExit:
        logger.error("Exiting")
        sys.exit(1)
    except ValueError:
        exit(1)
    except:
        print("Unexpected error!\n Stack Trace:", traceback.format_exc())
    exit

if __name__ == "__main__":
    logger = init_logging()
    logger = setup_local_logging(logger)
