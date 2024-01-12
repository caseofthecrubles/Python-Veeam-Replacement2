import requests
import json
import sys
import datetime

token=''

#These are the vms that will backed up
list_of_vms_to_clone = ['VM1','VM2']
list_of_vmids = {}
list_of_vmids2 = {}
list_of_vmids3 = {}
list_of_new_cloned_vm_ids = {}
full_vm_list = {}
working_vm_id = ''

# Replace with your vCenter server IP or hostname
vcenter_server = 'xxxxxxxxxxxxxxxxxx'
username = 'xxxxxxxxxxxxxxxxxx'
password = 'xxxxxxxxxxxxxxxxxx'

#base headers 
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}

#Clone required fields - you have to pull this info through the vsphere api
clone_vms_body = {
    "name": "xxxxxx",
    "source": "xxxxx",
    "placement": {
        "datastore": "xxxxxxxxxxxxxxxxxx",
        "host": "xxxxxxxxxxxxxxxxxx",
        "folder": "xxxxxxxxxxxxxxxxxx"
     },
    "power_on": "false"
}

#move required fields - you have to pull this info through the vsphere api
move_vm_body = {
"placement": {
    "datastore": "xxxxxxxxxxxxxxxxxx",
    "host": "xxxxxxxxxxxxxxxxxx",
    "folder": "xxxxxxxxxxxxxxxxxx"
    }
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

def clone_vmsid_list_funct(list_of_vmids3):
    for vmid_1 in list_of_vmids3:
        new_headers = auth()
        current_vm_name = list_of_vmids3[vmid_1]
        current_time = datetime.datetime.now()
        time_string = current_time.strftime("%y-%m-%d-%H-%M")
        vm_name_time = "py-clone-"+ time_string + "-" + current_vm_name
        #print(vm_name_time)
        clone_vms_body['name'] = vm_name_time
        clone_vms_body['source'] = vmid_1

        #print(clone_vms_body)
        clone_vms_url = f'https://{vcenter_server}/api/vcenter/vm?action=clone'
        ## Get the list of VMs
        vm_clone = requests.post(clone_vms_url, json=clone_vms_body, headers=new_headers, verify=False)
    #
        if vm_clone.status_code == 200:
            json_data = vm_clone.json()
            #print(json.dumps(json_data, indent=4))
            new_vm_id = json.dumps(json_data, indent=4)
            list_of_new_cloned_vm_ids[str(new_vm_id)] = vm_name_time
            print(f"heres the new_vm_id "+ str(new_vm_id) + " new vm_name_time {vm_name_time} " +  str(list_of_new_cloned_vm_ids))
        else:
            print(f"clone_vms_funct Failed to get data. Status code: {vm_clone.status_code}")
            print(f"vm_clone real error {vm_clone.text}")
    return list_of_new_cloned_vm_ids

def move_vmid(dict_of_new_cloned_vm_ids):
    new_vm_id = dict_of_new_cloned_vm_ids.keys()
    for new_new_vm_id in new_vm_id:
        #new API token before we move
        new_headers = auth()
        #Continue on to the migrations
        new_new_new_vm_id = new_new_vm_id.replace('"','')
        print(f'moving the vm {new_new_new_vm_id}')
        move_vm_url = f'https://{vcenter_server}/api/vcenter/vm/{new_new_new_vm_id}?action=relocate'
        print(str(move_vm_url))
        vm_move = requests.post(move_vm_url, json=move_vm_body, headers=new_headers, verify=False)
        if vm_move.status_code == 204:
            print('status code is 204') 
            print(str(vm_move))
        else:
            print(f"move_vmid Failed to get data. Status code: {vm_move.status_code}")
            print(f"real error from vsphere: {vm_move.text}")
            continue

def convert_to_vmid(full_vm_list2):
    #list_of_vms_to_clone
    for vm_name in list_of_vms_to_clone:
        #print(str(vm_name))
        #print(type(full_vm_list2))
        for item in full_vm_list2["value"]:
            if item["name"] == vm_name:
                working_vm_id = item['vm']
                #print(str(working_vm_id))
                list_of_vmids[str(working_vm_id)] = vm_name
                #print(list_of_vmids)
    if len(list_of_vmids) >= 1:
        return list_of_vmids
    else:
        print("not enough vms to continue")
        sys.exit()

if __name__ == "__main__":
    listttt = "no"
    new_headers = auth()
    full_vm_list2 = list_vm(listttt)
    list_of_vmids3 = convert_to_vmid(full_vm_list2)
    dict_of_new_cloned_vm_ids = clone_vmsid_list_funct(list_of_vmids3)
    print(dict_of_new_cloned_vm_ids)
    move_vmid(dict_of_new_cloned_vm_ids)
    listttt = "yes"
    list_vm(listttt)
