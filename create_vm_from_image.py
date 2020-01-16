#!/usr/local/bin/python3.8
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
from pprint import pprint
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Print usage messages.
def PrintUsage():

    print ("<Usage>: <{}> --image".format(sys.argv[0]))
    print ("Will list the available images in the Image Repo.\n")
    print ("<{}> <Image Name> <VM Name>".format(sys.argv[0]))
    print ("Will create a VM using a vDisk cloned from <Image Name>.")
    return

# Construct a proper POST specification and create a VM.
def create_vm(mycluster,vmdisk_uuid,vm_name,storage_container_uuid,network_uuid):

    print ("Entering Create_VM")
    vm_dict = {}
    vm_dict["vm_features"] = {}
    vm_dict["vm_features"]["VGA_CONSOLE"] = True
    vm_dict["vm_features"]["AGENT_VM"]= False
    
    vm_dict["uuid"] = str(uuid.uuid4())
    vm_dict["name"] = vm_name
    vm_dict["description"] = "Demo VM"
    
    vm_dict["boot"] = {}
    vm_dict["boot"]["boot_device_type"] = "DISK"
    vm_dict["boot"]["disk_address"] = {}
    # If you were cloning from a file in a storage container, you would instead update:
    # vm_dict["boot"]["disk_address"]["ndfs_filepath"] with "/storage_container/nfs_file_name"
    # where nfs_file_name is associated with the vdisk you want to clone.
    vm_dict["boot"]["disk_address"]["vmdisk_uuid"] = vmdisk_uuid
    vm_dict["boot"]["disk_address"]["device_index"] = "0"
    vm_dict["boot"]["disk_address"]["device_bus"] = "SCSI"
    
    vm_dict["num_cores_per_vcpu"] = 1
    vm_dict["num_vcpus"] = 4
    vm_dict["memory_mb"] = 8192
    
    vm_dict["vm_nics"] = []
    vm_dict["vm_nics"].append({"network_uuid": network_uuid})
    
    vm_dict["ha_priority"] = 0
    vm_dict["vm_disks"] = []
    vm_dict["vm_disks"].append(
        {
            "is_cdrom": False,
            "vm_disk_clone": {
                "storage_container_uuid": storage_container_uuid,
                "disk_address": {
                    # If you were cloning from a file in a storage container, you would instead update:
                    # "ndfs_filepath" to "/storage_container/nfs_file_name"
                    # where nfs_file_name is associated with the vdisk you want to clone.
                    "vmdisk_uuid": vmdisk_uuid,
                    "device_index": "0",
                    "device_bus": "scsi"
                }
            }
        }
    )
    vm_dict["timezone"] = "UTC"
    # pprint(vm_dict)
    vm_json = json.dumps(vm_dict)
    # print("VM_JSON RIGHT BEFORE CREATE:",vm_json)
    cluster_url = mycluster.base_urlv2 + "/vms/"
    print("Creating VM:",vm_dict["name"])
    server_response = mycluster.sessionv2.post(cluster_url, data=json.dumps(vm_dict))
    pprint(server_response)
    return vm_dict["uuid"]

if __name__ == "__main__":
    try:
        if ((len(sys.argv) != 2) and (len(sys.argv) != 3)):
            PrintUsage()
            sys.exit(1)

        if (len(sys.argv) == 2) and (sys.argv[1] != "--image"):
            PrintUsage()
            sys.exit(1)

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        mycluster = C.my_api(C.src_cluster_ip,C.src_cluster_admin,C.src_cluster_pwd)
        status, cluster = mycluster.get_cluster_information()
        if (status != 200):
            print("Cannot connect to ",cluster)
            print("Did you remember to update the config file?")
            sys.exit(1)
        
        # If we going to clone from a file in a container, you would do the following:
        # 1. Get the UUID of the container using the container name. Use GET /storage_containers instead of GET /images.
        # 2. Get a list of all vdisks in that container. Use GET /storage_containers/{uuid}/vdisks.
        # 3. Get the nfs_file_name associated with the vdisk you want to clone.
        # 4. In create_vm, use this to update vm_dict["ndfs_filepath"] instead of vm_dict["vmdisk_uuid"]
        status,resp = mycluster.get_images()
        all_images_list = resp["entities"]
        if (sys.argv[1] == "--image"):
            print ("Here are the available images that may be cloned:")
            for image in all_images_list:
                print (image["name"])
            sys.exit(0)

        # We're here to create a VM.
        image_name = sys.argv[1]
        vm_name = sys.argv[2]
        found = False
        for image in all_images_list:
            if (image["name"] == image_name):
                vmdisk_uuid = image["vm_disk_id"]
                storage_container_uuid = image["storage_container_uuid"]
                found = True
                break

        if (found == False):
            print ("Could not find", image_name, "in Image Repo.")
            print ("Please run", sys.argv[0], "--image to get a list of all images.")
            sys.exit(1)

        status,resp = mycluster.get_network_info()
        all_networks_list = resp["entities"]
        # We're just going to grab the first network UUID we see.
        # If we wanted to assign a VM to a particular network, we'd match for names instead.
        for network in all_networks_list:
            network_uuid = network["uuid"]
            break

        vm_uuid = create_vm(mycluster,vmdisk_uuid,vm_name,storage_container_uuid,network_uuid)
        # Power on the VM.
        status,resp = mycluster.power_on_vm(vm_uuid)
        
    except Exception as ex:
        print(ex)
        sys.exit(1)
