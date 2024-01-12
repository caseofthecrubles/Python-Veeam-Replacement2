import requests
import json
import sys
from datetime import datetime

token=''

list_of_vmids = {}
list_of_vmids2 = {}
list_of_vmids3 = {}
list_of_new_cloned_vm_ids = {}
full_vm_list = {}
working_vm_id = ''
dict_of_vms_to_proccess = {}
dict_of_vms_to_delete = {}

# Pull the script runtime
current_time = datetime.now()
time_string_current = current_time.strftime("%y-%m-%d")
print("Current Time: ", time_string_current)

# Replace with your vCenter server IP or hostname
vcenter_server = 'xxxxxxxxxxx'
username = 'xxxxxxxxxxxxxxx'
password = 'xxxxxxxxxxxxxxxx'

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

def auth():
    # Construct the URL for login
    url = f'https://{vcenter_server}/rest/com/vmware/cis/session'

    # Perform the POST request to get the token
    response = requests.post(url, auth=(username, password), headers=headers, verify=False)

    # Check if the request was successful
    if response.status_code == 200:
        token = response.json()['value']
        print("Authentication token:", token)
        headers['vmware-api-session-id'] = token
        print(headers)
        return headers
    else:
        print("Failed to authenticate. Status code:", response.status_code)
        print(f"real error auth: {response.text}")
        sys.exit()

def list_vm(listttt):
    vms_url = f'https://{vcenter_server}/rest/vcenter/vm'
    # Get the list of VMs
    new_headers = auth()
    vm_response = requests.get(vms_url, headers=new_headers, verify=False)
    #print(str(new_headers) + 'headers 123')
    if vm_response.status_code == 200:
        json_data = vm_response.json()
        full_vm_list = json_data
        if listttt == "yes":
            print(json.dumps(json_data, indent=4))
            return full_vm_list
        else:
            return full_vm_list
    else:
        print(f"list_vm Failed to get data. Status code: {vm_response.status_code}")
        print(f"real error vm_response {vm_response.text}")
        sys.exit()

def pull_older_then_2_days(full_vm_list2):
    for item in full_vm_list2["value"]:
        vmname = item['name']
        vmid = item['vm']
        dict_of_vms_to_proccess[vmname] = vmid
    for vmname2 in dict_of_vms_to_proccess.keys():
        if "py-clone-" in vmname2:
            vmname2split = vmname2.split("-")
            date1combinedvmname2 = (vmname2split[2] + "-" + vmname2split[3] + "-" + vmname2split[4])
            date1combinedvmname2_split = date1combinedvmname2.split("-")
            time_string_current_split = time_string_current.split("-")

            #yy-mm-dd
            #24-01-07

            #if the vm is older in the current year add it to the deletion list - if the year is older that statifies 2 days
            if int(date1combinedvmname2_split[0]) < int(time_string_current_split[0]):
                print(str(date1combinedvmname2_split[0]) + " year is older then the current year "+str(time_string_current_split[0]))
                vmid_to_delete = dict_of_vms_to_proccess[vmname2]
                dict_of_vms_to_delete[vmname2] = vmid_to_delete

            #if the vm is older in the current month add it to the deletion list - if the month is older that statifies 2 days
            if int(date1combinedvmname2_split[1]) < int(time_string_current_split[1]):
                print(str(date1combinedvmname2_split[1]) + " month is older then the current month "+str(time_string_current_split[1]))
                vmid_to_delete = dict_of_vms_to_proccess[vmname2]
                dict_of_vms_to_delete[vmname2] = vmid_to_delete

            #if the vm is older then the 2 days from the current day add it to the deletion list
            if int(date1combinedvmname2_split[2]) <= (int(time_string_current_split[2]) - 2):
                print(str(date1combinedvmname2_split[2]) + " day is older then current day minus 2 " + str(time_string_current_split[2]))
                vmid_to_delete = dict_of_vms_to_proccess[vmname2]
                dict_of_vms_to_delete[vmname2] = vmid_to_delete
            else:
                continue

def delete_vm(dict_of_vms_to_delete):
    for vmname_to_deletefunct in dict_of_vms_to_delete.keys():
        vmid_to_delete_now = dict_of_vms_to_delete[vmname_to_deletefunct]
        vms_url = (f'https://{vcenter_server}/api/vcenter/vm/{vmid_to_delete_now}')
        # Get the list of VMs
        new_headers = auth()
        vm_response = requests.delete(vms_url, headers=new_headers, verify=False)
        
        if vm_response.status_code == 204:
            print(f"Succesfully deleted vm {str(vmname_to_deletefunct)} {str(vmid_to_delete_now)}")
        else:
            print(f"Failed to delete VM. Status code: {vm_response.status_code}")
            print(f"real error vm_response {vm_response.text}")
            sys.exit()

if __name__ == "__main__":
    listttt = "no"
    new_headers = auth()
    full_vm_list2 = list_vm(listttt)
    pull_older_then_2_days(full_vm_list2)
    print(dict_of_vms_to_delete)
    delete_vm(dict_of_vms_to_delete)
