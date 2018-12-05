#!/usr/local/bin/python3.7
#
# DISCLAIMER: This script is not supported by Nutanix. Please contact
# Sandeep Cariapa (sandeep.cariapa@nutanix.com) if you have any questions.
# Last updated: 9/29/2018
# This script uses Python 3.7.
# NOTE:
# 1. You need a Python library called "requests" which is available from
# the url: http://docs.python-requests.org/en/latest/user/install/#install
# For reference look at:
# https://github.com/nutanix/Connection-viaREST/blob/master/nutanix-rest-api-v2-script.py
# https://github.com/nelsonad77/acropolis-api-examples

import sys
import json
import uuid
import requests
import clusterconfig as C
from urllib.parse import quote
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Print usage messages.
def PrintUsage():

    print ("<Usage>:",sys.argv[0],"<VM Name>")
    print ("Where <VM Name is the name of the VM to be cloned.")
    print ("If there are multiple VMs with the same name we will clone one of them randonly :-)")
    return

# Clone a VM with the given UUID.
def clonevm(mycluster,vmid,vm_name):

    vm_clone_proto = {
        "override_network_config": False,
        "name": vm_name + "_clone",
        "uuid": str(uuid.uuid4()),
    }
    specs = []
    specs.append(vm_clone_proto)

    vm_clone_spec = {}
    vm_clone_spec["spec_list"] = specs

    cloneuuid =  vm_clone_spec['spec_list'][0]["uuid"]
    print("Cloneuuid:",cloneuuid)
    cluster_url = mycluster.base_urlv2 + "vms/" + str(quote(vmid)) + "/clone"
    print("Cloning VM",cluster_url)
    try:
        server_response = mycluster.sessionv2.post(cluster_url, data=json.dumps(vm_clone_spec))
        return server_response.status_code, cloneuuid, json.loads(server_response.text)
    except Exception as ex:
        print(ex)
        return -1,0,cluster_url

if __name__ == "__main__":
    try:
        if (len(sys.argv) != 2):
            PrintUsage()
            sys.exit(1)
        
        vm_name = sys.argv[1]
        
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        mycluster = C.my_api(C.src_cluster_ip,C.src_cluster_admin,C.src_cluster_pwd)
        status, cluster = mycluster.get_cluster_information()
        if (status != 200):
            print ("Cannot connect to ",cluster)
            print ("Did you remember to update the config file?")
            sys.exit(1)

        # Get information about all VMs in the cluster.
        status,all_vms = mycluster.get_all_vm_info()
        all_vms_list = all_vms["entities"]
        # pprint(all_vms_list)
        for vm_dict in all_vms_list:
            # If you were looking for a VM with a particular UUID, you would be matching for it here.
            if (vm_name == vm_dict["name"]):
                vm_uuid = vm_dict["uuid"]
                break
        
        try:
            print ("UUID of your VM is:",vm_uuid)
        except NameError:
            print (">>> Cannot proceed because we cannot find",vm_name)
            sys.exit(1)

        status, cloneuuid, resp = clonevm(mycluster,vm_uuid,vm_name)
        if (status != 201):
            print ("Could not clone:",vm_name,status)
            pprint(resp)
            sys.exit(1)

        # If we are here then we were able to clone the VM, and received a task_uuid in response.
        # Now poll that task until it completes and power it on.
        print ("Successfully cloned:",vm_name)
        taskid = resp["task_uuid"]
        mycluster.poll_task(taskid)
        mycluster.power_on_vm(cloneuuid)

    except Exception as ex:
        print(ex)
        sys.exit(1)
