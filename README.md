# api-lab
If there are any questions regarding the REST API, a good place to start is the REST API explorer (accessed via Prism Element), or from perusing https://developer.nutanix.com/reference/prism_element/v2/. 

REST API v1 docs are available at:
https://portal.nutanix.com/#/page/docs/details?targetId=API-Ref-AOS-v58:API-Ref-AOS-v58

Here is a description of the files in this repo:
* HOWTO.txt describes how to set up a dev environment so one can get started.


* clusterconfig.py contains variables and common functions used in the code. It is a Python module. You will need to update the variables above the line in order to get the programs to work. In particular please create a separate admin user on your cluster called "restapiuser", so the real admin password is not passed around.


* create_vm_from_image.py creates a VM using a vdisk cloned from an existing image. With a "--image" option it ouputs all images in the Image Repo. An exercise is to similarly create a VM however by cloning a vdisk from a file which exists in a storage container.This involves some additional steps:
1. Get the UUID of the container using the container name. Use GET /storage_containers instead of GET /images as in get_images().
2. Get a list of all vdisks in that container. Use GET /storage_containers/{uuid}/vdisks. Where {uuid} is the UUID of the storage container that you obtained from step 1. This involves a new function.
3. Get the nfs_file_name associated with the vdisk you want to clone. You would need to walk through the output from step 2 and look for the appropriate key in the dictionary.
4. In create_vm(), use this information to update vm_dict["ndfs_filepath"] instead of vm_dict["vmdisk_uuid"]. There are 2 places where you will need to do so. One in the boot drive section, and the other in the VM disk clone section. So first you want to tell the VM where it is booting from, and next you want to tell it where the drive is located. Please see the comments in the code for help.

* delete_vm_by_name.py takes the name of a VM as an argument and deletes it. Multiple VMs can have the same name. VM UUIDs however are unique. You can observe the UUID of a VM by logging into Prism -> Home -> VM -> Table, highlighting the VM. The VM UUID appears in a panel in the lower left side of the screen. The VM UUID is also a value returned by GET /vms.

An exercise is to take the UUID of a VM and delete it that way instead. Please see comments in the code for help.

* clone_vm_by_name.py takes the name of a VM as an argument and clones it. The clone is named "vmname_clone". Again, multiple VMs can have the same name, so you could modify this script to take a VM UUID as an argument instead.

Another interesting exercise would be to take an additional numeric argument in order to create multiple clones of the same VM.


