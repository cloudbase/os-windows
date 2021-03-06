# Copyright 2015 Cloudbase Solutions Srl
#
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
Base Utility class for operations on Hyper-V.
"""

import sys
import time

if sys.platform == 'win32':
    import wmi

from oslo_log import log as logging

from os_windows._i18n import _
from os_windows import exceptions
from os_windows.utils import constants

LOG = logging.getLogger(__name__)


class JobUtils(object):

    _WMI_NAMESPACE = '//%s/root/virtualization'

    def __init__(self, host='.'):
        if sys.platform == 'win32':
            self._init_hyperv_wmi_conn(host)

    def _init_hyperv_wmi_conn(self, host):
        self._conn = wmi.WMI(moniker=self._WMI_NAMESPACE % host)

    def check_ret_val(self, ret_val, job_path, success_values=[0]):
        if ret_val in [constants.WMI_JOB_STATUS_STARTED,
                       constants.WMI_JOB_STATE_RUNNING]:
            return self._wait_for_job(job_path)
        elif ret_val not in success_values:
            raise exceptions.HyperVException(
                _('Operation failed with return value: %s') % ret_val)

    def _wait_for_job(self, job_path):
        """Poll WMI job state and wait for completion."""

        job_wmi_path = job_path.replace('\\', '/')
        job = wmi.WMI(moniker=job_wmi_path)

        while job.JobState == constants.WMI_JOB_STATE_RUNNING:
            time.sleep(0.1)
            job = wmi.WMI(moniker=job_wmi_path)
        if job.JobState != constants.WMI_JOB_STATE_COMPLETED:
            job_state = job.JobState
            if job.path().Class == "Msvm_ConcreteJob":
                err_sum_desc = job.ErrorSummaryDescription
                err_desc = job.ErrorDescription
                err_code = job.ErrorCode
                data = {'job_state': job_state,
                        'err_sum_desc': err_sum_desc,
                        'err_desc': err_desc,
                        'err_code': err_code}
                raise exceptions.HyperVException(
                    _("WMI job failed with status %(job_state)d. "
                      "Error details: %(err_sum_desc)s - %(err_desc)s - "
                      "Error code: %(err_code)d") % data)
            else:
                (error, ret_val) = job.GetError()
                if not ret_val and error:
                    data = {'job_state': job_state,
                            'error': error}
                    raise exceptions.HyperVException(
                        _("WMI job failed with status %(job_state)d. "
                          "Error details: %(error)s") % data)
                else:
                    raise exceptions.HyperVException(
                        _("WMI job failed with status %d. No error "
                          "description available") % job_state)
        desc = job.Description
        elap = job.ElapsedTime
        LOG.debug("WMI job succeeded: %(desc)s, Elapsed=%(elap)s",
                  {'desc': desc, 'elap': elap})
        return job

    def add_virt_resource(self, virt_resource, parent):
        """Adds a new resource to the VM."""
        vs_man_svc = self._conn.Msvm_VirtualSystemManagementService()[0]
        res_xml = [virt_resource.GetText_(1)]
        (job_path,
         new_resources,
         ret_val) = vs_man_svc.AddVirtualSystemResources(res_xml,
                                                         parent.path_())
        self.check_ret_val(ret_val, job_path)
        return new_resources

    def modify_virt_resource(self, virt_resource, parent):
        """Updates a VM resource."""
        vs_man_svc = self._conn.Msvm_VirtualSystemManagementService()[0]
        (job_path, ret_val) = vs_man_svc.ModifyVirtualSystemResources(
            ResourceSettingData=[virt_resource.GetText_(1)],
            ComputerSystem=parent.path_())
        self.check_ret_val(ret_val, job_path)

    def remove_virt_resource(self, virt_resource, parent):
        """Removes a VM resource."""
        vs_man_svc = self._conn.Msvm_VirtualSystemManagementService()[0]
        res_path = [virt_resource.path_()]
        (job_path, ret_val) = vs_man_svc.RemoveVirtualSystemResources(
            res_path, parent.path_())
        self.check_ret_val(ret_val, job_path)


class JobUtilsV2(JobUtils):

    _WMI_NAMESPACE = '//%s/root/virtualization/v2'

    def add_virt_resource(self, virt_resource, parent):
        vs_man_svc = self._conn.Msvm_VirtualSystemManagementService()[0]
        (job_path, new_resources, ret_val) = vs_man_svc.AddResourceSettings(
            parent.path_(), [virt_resource.GetText_(1)])
        self.check_ret_val(ret_val, job_path)
        return new_resources

    def modify_virt_resource(self, virt_resource, parent=None):
        vs_man_svc = self._conn.Msvm_VirtualSystemManagementService()[0]
        (job_path, out_set_data, ret_val) = vs_man_svc.ModifyResourceSettings(
            ResourceSettings=[virt_resource.GetText_(1)])
        self.check_ret_val(ret_val, job_path)

    def remove_virt_resource(self, virt_resource, parent=None):
        vs_man_svc = self._conn.Msvm_VirtualSystemManagementService()[0]
        (job, ret_val) = vs_man_svc.RemoveResourceSettings(
            ResourceSettings=[virt_resource.path_()])
        self.check_ret_val(ret_val, job)

    def add_virt_feature(self, virt_feature, parent):
        self.add_multiple_virt_features([virt_feature], parent)

    def add_multiple_virt_features(self, virt_features, parent):
        vs_man_svc = self._conn.Msvm_VirtualSystemManagementService()[0]
        (job_path, out_set_data, ret_val) = vs_man_svc.AddFeatureSettings(
            parent.path_(), [f.GetText_(1) for f in virt_features])
        self.check_ret_val(ret_val, job_path)

    def remove_virt_feature(self, virt_feature):
        self.remove_multiple_virt_features([virt_feature])

    def remove_multiple_virt_features(self, virt_features):
        vs_man_svc = self._conn.Msvm_VirtualSystemManagementService()[0]
        (job_path, ret_val) = vs_man_svc.RemoveFeatureSettings(
            FeatureSettings=[f.path_() for f in virt_features])
        self.check_ret_val(ret_val, job_path)
