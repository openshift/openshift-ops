#!/bin/env python
# vim: expandtab:tabstop=4:shiftwidth=4

#   Copyright 2016 Red Hat Inc.
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

"""
 This script can be used to reset the passwords for your AWS IAM user accounts.
 It can be used for individual accounts or for all your accounts at once.

 This assumes that the AWS credentials for the account(s) are present in "~/.aws/credentials"
 The credentials entry must also be labeled with a name:

 [account-name-or-number]
 aws_access_key_id=xxxx
 aws_secret_access_key=xxxx

 Usage:

 For individual accounts:
 change_iam_password.py -p ded-stage-aws -p ded-int-aws -p <some-other-account>


 For all accounts found in ~/.aws/credentials:
 change_iam_password.py --all
"""

from __future__ import print_function

import argparse
import getpass
import os
import re
import sys

# pylint: disable=import-error
import boto3
import botocore.exceptions


class ChangePassword(object):
    """ Class to change IAM user account passwords. """


    def __init__(self):
        """ constructor """
        self.response = None


    @staticmethod
    def check_arguments():
        """ Ensure that an argument was passed in from the command line.

        Returns:
            Parsed argument(s), if provided
        """

        parser = argparse.ArgumentParser(description='Change the password for IAM accounts.')
        parser.add_argument('-a', '--all',
                            help='Change your password for every profile in ~/.aws/credentials.',
                            action='store_true')
        parser.add_argument('-p', '--profile',
                            help='Change your password for the specified profile.',
                            action='append')
        args = parser.parse_args()

        if not args.all and not args.profile:
            print('Specify an account profile name.\n'
                  'To change the password for all accounts on file, use "--all"\n'
                  'Usage:\n'
                  'example: {0} -p <account-name>\n'
                  'example: {0} --all'.format(parser.prog))
            sys.exit(10)
        return args


    @staticmethod
    def get_all_profiles():
        """ If -a is specified, generate a list of all profiles found in ~/.aws/credentials. """

        path = os.path.join(os.path.expanduser('~'), '.aws/credentials')
        profile_list = []

        if os.path.isfile(path):
            with open(path) as open_file:
                stripped_line = list([line.rstrip() for line in open_file.readlines()])
                for line in stripped_line:
                    account = re.match(r"^\[([A-Za-z0-9_\-]+)\]", line)
                    if account is not None:
                        profile_list.append(account.group(1))
                return profile_list
        else:
            raise ValueError(path + ' does not exist')


    def change_password(self, aws_account, user_name, new_password):
        """ Change the password for the specified account. """

        try:
            session = boto3.Session(profile_name=aws_account)
        except botocore.exceptions.ProfileNotFound:
            print('Error: ProfileNotFound. AWS credentials must be generated first using')
            print('       the command: aws_api_key_manager -p', aws_account)
            return False
        client = session.client('iam')

        try:
            self.response = client.update_login_profile(
                UserName=user_name,
                Password=new_password
                )

        except botocore.exceptions.ClientError as client_exception:
            if client_exception.response['Error']['Code'] == 'NoSuchEntity':
                client.create_login_profile(
                    UserName=user_name,
                    Password=new_password
                    )
            elif client_exception.response['Error']['Code'] == 'InvalidClientTokenId':
                print('Error: InvalidClientTokenId. Your API key may have expired or may have been replaced.')
                print('       Generate new credentials using this command: aws_api_key_manager -p', aws_account)
                return False
            elif client_exception.response['Error']['Code'] == 'SignatureDoesNotMatch':
                print('Error: SignatureDoesNotMatch. Credentials for this account may have been corrupted. You may')
                print('       need to generate new credentials using this command: aws_api_key_manager -p', aws_account)
                return False
            else:
                raise # re-raise for any other flavor of botocore.exceptions.ClientError

        print('Password successfully changed for:', aws_account)
        return self.response


    def main(self):
        """ Main function. """

        args = self.check_arguments()

        user_name = raw_input('Username: ')
        new_password = getpass.getpass('New Password:')
        confirm_password = getpass.getpass('Confirm New Password:')

        if new_password != confirm_password:
            raise ValueError('New password does not match confirmation.')

        else:
            if args.profile:
                for aws_account in args.profile:
                    self.change_password(aws_account, user_name, confirm_password)

            elif args.all:
                for aws_account in self.get_all_profiles():
                    self.change_password(aws_account, user_name, confirm_password)

            else:
                raise ValueError('No suitable arguments provided.')


if __name__ == '__main__':
    CHANGE = ChangePassword()
    CHANGE.main()
