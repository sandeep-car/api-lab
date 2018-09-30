# DISCLAIMER: This script is not supported by Nutanix. Please contact
# Sandeep Cariapa (sandeep.cariapa@nutanix.com) if you have any questions.
import json
import requests
from urllib.parse import quote
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# AHV cluster details. We need these in order to log into the REST API.
src_cluster_ip = "10.21.79.37"
src_cluster_admin = "restapiuser"
src_cluster_pwd = "nx2Tech071!"

# ========== DO NOT CHANGE ANYTHING UNDER THIS LINE =====
class my_api():
    def __init__(self,ip,username,password):

        # Cluster IP, username, password.
        self.ip_addr = ip
        self.username = username
        self.password = password
        # Base URL at which v1 REST services are hosted in Prism Gateway.
        base_urlv1 = 'https://%s:9440/PrismGateway/services/rest/v1/'
        self.base_urlv1 = base_urlv1 % self.ip_addr
        self.sessionv1 = self.get_server_session(self.username, self.password)
        # Base URL at which v2 REST services are hosted in Prism Gateway.
        base_urlv2 = 'https://%s:9440/PrismGateway/services/rest/v2.0/'
        self.base_urlv2 = base_urlv2 % self.ip_addr
        self.sessionv2 = self.get_server_session(self.username, self.password)
        
    def get_server_session(self, username, password):
          
        # Creating REST client session for server connection, after globally
        # setting authorization, content type, and character set.
        session = requests.Session()
        session.auth = (username, password)
        session.verify = False
        session.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        return session
       
    # Get cluster information.
    def get_cluster_information(self):
        
        cluster_url = self.base_urlv2 + "cluster/"
        print("Getting cluster information for cluster %s." % self.ip_addr)
        try:
            server_response = self.sessionv2.get(cluster_url)
            return server_response.status_code ,json.loads(server_response.text)
        except Exception as ex:
            print(ex)
            return -1,cluster_url

    # Get network info.
    def get_network_info(self):

        cluster_url = self.base_urlv2 + "/networks/"
        print("Getting network info")
        server_response = self.sessionv2.get(cluster_url)
        print("Response code:",server_response.status_code)
        # Uncomment the following line to see what the cluster returned.
        # print("Response text:",server_response.text)
        return server_response.status_code ,json.loads(server_response.text)

    # Get all images in the cluster.
    def get_images(self):

        cluster_url = self.base_urlv2 + "/images/"
        print("Getting image info")
        server_response = self.sessionv2.get(cluster_url)
        print("Response code:",server_response.status_code)
        # Uncomment the following line to see what the cluster returned.
        # print("Response text:",server_response.text)
        return server_response.status_code ,json.loads(server_response.text)

    # Get all VMs in the cluster.
    def get_all_vm_info(self):

        cluster_url = self.base_urlv2 + "vms/?include_vm_disk_config=true&include_vm_nic_config=true"
        server_response = self.sessionv2.get(cluster_url)
        # print("Response code: %s" % server_response.status_code)
        return server_response.status_code ,json.loads(server_response.text)

    # Power on VM with this UUID.
    def power_on_vm(self, vmid):
        
        print("Powering on VM:",vmid)
        cluster_url = self.base_urlv2 + "vms/" + str(quote(vmid)) + "/set_power_state/"
        vm_power_post = {"transition":"ON"}
        server_response = self.sessionv2.post(cluster_url, data=json.dumps(vm_power_post))
        # print("Response code: %s" % server_response.status_code)
        return server_response.status_code ,json.loads(server_response.text)
