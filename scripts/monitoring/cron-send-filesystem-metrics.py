#!/usr/bin/env python
'''
  Command to send dynamic filesystem information to Zagg
'''
# vim: expandtab:tabstop=4:shiftwidth=4
#
#   Copyright 2015 Red Hat Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#This is not a module, but pylint thinks it is.  This is a command.
#pylint: disable=invalid-name,import-error

import argparse
import re

from openshift_tools.monitoring.metric_sender import MetricSender
from openshift_tools.monitoring import pminfo

def parse_args():
    """ parse the args from the cli """

    parser = argparse.ArgumentParser(description='Disk metric sender')
    parser.add_argument('-v', '--verbose', action='store_true', default=None, help='Verbose?')
    parser.add_argument('--debug', action='store_true', default=None, help='Debug?')
    parser.add_argument('--filter-pod-pv', action='store_true', default=None,
                        help="Filter out OpenShift Pod PV mounts")
    parser.add_argument('--force-send-zeros', action='store_true', default=None,
                        help="Send 0% full for mounts, useful for clearing existing bad alerts")
    return parser.parse_args()

def filter_out_key_name_chars(metric_dict, filesystem_filter):
    """ Simple filter to elimate unnecessary characters in the key name """
    filtered_dict = {k.replace(filesystem_filter, ''):v
                     for (k, v) in metric_dict.iteritems()
                    }
    return filtered_dict

def filter_out_container_root(metric_dict):
    """ Simple filter to remove the container root FS info """
    container_root_regex = r'^/dev/mapper/docker-\d+:\d+-\d+-[0-9a-f]+$'
    filtered_dict = {k: v
                     for (k, v) in metric_dict.iteritems()
                     if not re.match(container_root_regex, k)
                    }

    return filtered_dict

def filter_out_customer_pv_filesystems(metric_dict):
    """ Remove customer PVs from list """
    r = re.compile("^/dev/(?:xvd[a-z]{2}|nvme[2-9].*)$")
    # filter out xvda{2} (???) and nvme devices past 2

    return {
        k:v for (k, v) in metric_dict.iteritems() if not r.match(k)
    }

def zero_mount_percentages(metric_dict):
    """ Make all mounts report 0% used """
    return {
        k:0 for (k, v) in metric_dict.iteritems()
    }

def main():
    """  Main function to run the check """

    args = parse_args()
    metric_sender = MetricSender(verbose=args.verbose, debug=args.debug)

    filesys_full_metric = ['filesys.full']
    filesys_inode_derived_metrics = {'filesys.inodes.pused' :
                                     'filesys.usedfiles / (filesys.usedfiles + filesys.freefiles) * 100'
                                    }

    discovery_key_fs = 'disc.filesys'
    item_prototype_macro_fs = '#OSO_FILESYS'
    item_prototype_key_full = 'disc.filesys.full'
    item_prototype_key_inode = 'disc.filesys.inodes.pused'

    # Get the disk space
    filesys_full_metrics = pminfo.get_metrics(filesys_full_metric)

    filtered_filesys_metrics = filter_out_key_name_chars(filesys_full_metrics, 'filesys.full.')
    filtered_filesys_metrics = filter_out_container_root(filtered_filesys_metrics)

    if args.filter_pod_pv:
        filtered_filesys_metrics = filter_out_customer_pv_filesystems(filtered_filesys_metrics)

    if args.force_send_zeros:
        filtered_filesys_metrics = zero_mount_percentages(filtered_filesys_metrics)

    metric_sender.add_dynamic_metric(discovery_key_fs, item_prototype_macro_fs, filtered_filesys_metrics.keys())
    for filesys_name, filesys_full in filtered_filesys_metrics.iteritems():
        metric_sender.add_metric({'%s[%s]' % (item_prototype_key_full, filesys_name): filesys_full})

    # Get filesytem inode metrics
    filesys_inode_metrics = pminfo.get_metrics(derived_metrics=filesys_inode_derived_metrics)

    filtered_filesys_inode_metrics = filter_out_key_name_chars(filesys_inode_metrics, 'filesys.inodes.pused.')
    filtered_filesys_inode_metrics = filter_out_container_root(filtered_filesys_inode_metrics)

    if args.filter_pod_pv:
        filtered_filesys_inode_metrics = filter_out_customer_pv_filesystems(filtered_filesys_inode_metrics)

    if args.force_send_zeros:
        filtered_filesys_inode_metrics = zero_mount_percentages(filtered_filesys_inode_metrics)

    for filesys_name, filesys_inodes in filtered_filesys_inode_metrics.iteritems():
        metric_sender.add_metric({'%s[%s]' % (item_prototype_key_inode, filesys_name): filesys_inodes})

    metric_sender.send_metrics()

if __name__ == '__main__':
    main()
