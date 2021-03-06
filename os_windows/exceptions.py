# Copyright 2015 Cloudbase Solutions Srl
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Utility class for VM related operations on Hyper-V.
"""


class HyperVException(Exception):
    def __init__(self, message=None):
        super(HyperVException, self).__init__(message)


# TODO(alexpilotti): Add a storage exception base class
class VHDResizeException(HyperVException):
    def __init__(self, message=None):
        super(HyperVException, self).__init__(message)


class HyperVAuthorizationException(HyperVException):
    def __init__(self, message=None):
        super(HyperVException, self).__init__(message)


class UnsupportedConfigDriveFormatException(HyperVException):
    def __init__(self, message=None):
        super(HyperVException, self).__init__(message)


class HyperVVMNotFoundException(HyperVException):
    def __init__(self, message=None):
        super(HyperVVMNotFoundException, self).__init__(message)
