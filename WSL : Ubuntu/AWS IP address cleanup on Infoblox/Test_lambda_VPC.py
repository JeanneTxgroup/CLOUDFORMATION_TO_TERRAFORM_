import json, os, hashlib, requests, logging, urllib3

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# AJOUTEZ CE BLOC POUR VOIR LES LOGS DANS LA CONSOLE
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# Désactive les avertissements SSL car apiVerifySsl est False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Region to VPC size to supernet mapping - tells the script in which range to crate containers and networks for a requested VPC
# for sandbox purposes, use region 4 as eu-west-1
dictRegionSupernet = {
	'eu-west-1':    {'M': '10.128.0.0/15', 'S': '10.130.0.0/16', 'L': '10.131.0.0/17', 'XL': '10.131.128.0/17'},
	'undefRegion2': {'M': '10.132.0.0/15', 'S': '10.134.0.0/16', 'L': '10.135.0.0/17', 'XL': '10.135.128.0/17'},
	'eu-central-1': {'M': '10.136.0.0/15', 'S': '10.138.0.0/16', 'L': '10.139.0.0/17', 'XL': '10.139.128.0/17'},
	'undefRegion4': {'M': '10.140.0.0/15', 'S': '10.142.0.0/16', 'L': '10.143.0.0/17', 'XL': '10.143.128.0/17'}
}
# VPC size to CIDR prefix mapping
dictVpcCidrBlockSize = {
	'M': '22',
	'S': '24',
	'L': '20',
	'XL': '18'
}

# Subnet sizes relative to VPC size (how many bits to add to the VPC CIDR prefix)
sizes = (
	# IP address distrubution for S, M, L and XL (16:4:1)
	{
		"IntraVpcSupernet": 4,
		"IntraVpc": 6,
		"PublicIntraVpcSupernet": 2,
		"Public": 4,
		"Private": 2
	},
	# IP address distrubution for S2, M2, L2 and XL2 (8:8:2)
	{
		"IntraVpcSupernet": 4,
		"IntraVpc": 6,
		"PublicIntraVpcSupernet": 1,
		"Public": 3,
		"Private": 3
	}
)

# Get environment variables
apiAddress = "10.192.0.10"
apiVersion = "v2.7"
apiUser = "awsapiuser"
apiPass = "c7e116f813502ebd834cbbdc78c67a31836a82e4948f25f4ec0c3eaa8b7e4945"
apiUniqueExtattr = "Network ID"
apiCloud = True
apiVerifySsl = False

# apiVerifySsl must be of type boolean
if apiVerifySsl in ['false', 'False']:
	apiVerifySsl = False

def createNetwork(netParent, netSize, netComment, awsAccount):
	try:
		# If request is sent to Infoblox Cloud API, extensible attributes Tenant ID, Cloud API Owned and CMP Type are required
		if apiCloud :
			jsondata = json.dumps({'network':'func:nextavailablenetwork:'+netParent+','+netSize, 'comment':netComment, 'extattrs':{'Tenant ID':{'value': awsAccount}, 'Cloud API Owned':{'value':'True'}, 'CMP Type':{'value':'AWS VpcCustomResource'}}})
		else:
			jsondata = json.dumps({'network':'func:nextavailablenetwork:'+netParent+','+netSize, 'comment':netComment})
		url = 'https://'+apiAddress+'/wapi/'+apiVersion+'/network?_return_as_object=1&_return_fields=network'
		logger.debug(f"{netComment}: POST Request with contents, url: {url}, json: {jsondata}")
		response = requests.post(url, data=jsondata, auth=(apiUser,apiPass), verify=apiVerifySsl, timeout=30)
		return response
	except:
		return f'EXCEPTION: failed to create Network with params: {netParent}, {netComment}, {netSize}, {netComment}, {awsAccount}'


def createNetworkcontainer(netParent, netSize, netComment, awsAccount, rootContainer = 0, uniqueId = ''):
	try:
		# Limit size of comment to 255 chars (Infoblox limit)
		netComment = (netComment[:253] + '..') if len(netComment) > 255 else netComment
		# Get next available network
		# If request is sent to Infoblox Cloud API, extensible attributes Tenant ID, Cloud API Owned and CMP Type are required
		if apiCloud :
			jsondata = json.dumps({'network':'func:nextavailablenetwork:'+netParent+','+netSize, 'comment':netComment, 'extattrs':{'Tenant ID':{'value': awsAccount}, 'Cloud API Owned':{'value':'True'}, 'CMP Type':{'value':'AWS VpcCustomResource'}}})
		else:
			jsondata = json.dumps({'network':'func:nextavailablenetwork:'+netParent+','+netSize, 'comment':netComment})
		url = 'https://'+apiAddress+'/wapi/'+apiVersion+'/networkcontainer?_return_as_object=1&_return_fields=network'
		logger.debug(f"{netComment}: POST Request with contents, url: {url}, json: {jsondata}")
		response = requests.post(url, data=jsondata, auth=(apiUser,apiPass), verify=apiVerifySsl, timeout=30)
		logger.debug(f"POST request response: {response}")
		# If it's the root container, set extensible attribute defined in variable apiUniqueExtattr to uniqueId
		if rootContainer == 1 and response.status_code == 201:
			logger.debug(f"rootContainer == 1 and response.status_code == 201")
			if apiCloud :
				jsondata = json.dumps({'extattrs':{apiUniqueExtattr:{'value':uniqueId}, 'Tenant ID':{'value': awsAccount}, 'Cloud API Owned':{'value':'True'}, 'CMP Type':{'value':'AWS VpcCustomResource'}}})
				logger.debug(f"apiCloud == True -> json.dumps: {jsondata}")
			else:
				jsondata = json.dumps({'extattrs':{apiUniqueExtattr:{'value':uniqueId}}})
				logger.debug(f"apiCloud == False -> json.dumps: {jsondata}")
			url = 'https://'+apiAddress+'/wapi/'+apiVersion+'/'+response.json()['result']['_ref']+'?_return_as_object=1'
			logger.debug(f"{netComment}: POST Request with contents, url: {url}, json: {jsondata}")
			response2 = requests.put(url, data=jsondata, auth=(apiUser,apiPass), verify=apiVerifySsl, timeout=30)
			logger.debug(f"PUT request response: {response2}")
		return response

	except:
		return f"EXCEPTION: failed to create Network Container with params: {netParent}, {netComment}, {netSize}, {netComment}, {awsAccount}, {rootContainer}, {uniqueId}"


def deleteNetwork(physicalResourceId):
	try:
		response = requests.delete('https://'+apiAddress+'/wapi/'+apiVersion+'/'+physicalResourceId+'?_return_as_object=1', auth=(apiUser,apiPass), verify=apiVerifySsl, timeout=30)
		return response
	except:
		return f'EXCEPTION: failed to delete network with physicalResourceId: {physicalResourceId}'


def searchNetworkcontainer(uniqueId):
	try:
		response = requests.get('https://'+apiAddress+'/wapi/'+apiVersion+'/networkcontainer?_return_as_object=1&*'+apiUniqueExtattr+'='+uniqueId, auth=(apiUser,apiPass), verify=apiVerifySsl, timeout=30)
		if len(response.json()['result']) == 0:
			return 'INEXISTENT', ''
		else:
			return 'EXISTS', response.json()['result']
	except:
		print(response.text)
		return 'FAILED', ''


def create(stackId, vpcSize, uniqueId, stackInfo):
    awsRegion=stackId.split(':')[3]
    awsAccount=stackId.split(':')[4]
    netParent = dictRegionSupernet[awsRegion][vpcSize[0]]
    netSize = dictVpcCidrBlockSize[vpcSize[0]]

    if vpcSize[-1] == '2':
        netSize_IntraVpcSupernet = str(int(netSize)+sizes[1]["IntraVpcSupernet"])
        netSize_IntraVpc = str(int(netSize)+sizes[1]["IntraVpc"])
        netSize_PublicIntraVpcSupernet = str(int(netSize)+sizes[1]["PublicIntraVpcSupernet"])
        netSize_Public = str(int(netSize)+sizes[1]["Public"])
        netSize_Private = str(int(netSize)+sizes[1]["Private"])
    else:
        netSize_IntraVpcSupernet = str(int(netSize)+sizes[0]["IntraVpcSupernet"])
        netSize_IntraVpc = str(int(netSize)+sizes[0]["IntraVpc"])
        netSize_PublicIntraVpcSupernet = str(int(netSize)+sizes[0]["PublicIntraVpcSupernet"])
        netSize_Public = str(int(netSize)+sizes[0]["Public"])
        netSize_Private = str(int(netSize)+sizes[0]["Private"])

    logger.debug(f"netSize_IntraVpcSupernet: {netSize_IntraVpcSupernet} netSize_IntraVpc: {netSize_IntraVpc} netSize_PublicIntraVpcSupernet: {netSize_PublicIntraVpcSupernet} netSize_Public: {netSize_Public} netSize_Private: {netSize_Private}")
    logger.debug(f"createNetworkcontainer({netParent}, {netSize}, {stackInfo}, {awsAccount}, 1, {uniqueId}")
    response = createNetworkcontainer(netParent, netSize, stackInfo, awsAccount, 1, uniqueId)
    
    if response != 'FAILED':
        if response.status_code == 201:
            physicalResourceId = response.json()['result']['_ref']
            outputVpcCidrBlock = response.json()['result']['network']

            response = createNetwork(outputVpcCidrBlock, netSize_Private, 'Private1', awsAccount)
            outputAz1Private = response.json()['result']['network']
            
            response = createNetwork(outputVpcCidrBlock, netSize_Private, 'Private2', awsAccount)
            outputAz2Private = response.json()['result']['network']
            
            response = createNetwork(outputVpcCidrBlock, netSize_Private, 'Private3', awsAccount)
            outputAz3Private = response.json()['result']['network']

            response = createNetworkcontainer(outputVpcCidrBlock, netSize_PublicIntraVpcSupernet, 'Public and Intra VPC subnets', awsAccount)
            outputPublicIntraVpcSubnets = response.json()['result']['network']

            response = createNetwork(outputPublicIntraVpcSubnets, netSize_Public, 'Public1', awsAccount)
            outputAz1Public = response.json()['result']['network']

            response = createNetwork(outputPublicIntraVpcSubnets, netSize_Public, 'Public2', awsAccount)
            outputAz2Public = response.json()['result']['network']

            response = createNetwork(outputPublicIntraVpcSubnets, netSize_Public, 'Public3', awsAccount)
            outputAz3Public = response.json()['result']['network']

            response = createNetworkcontainer(outputPublicIntraVpcSubnets, netSize_IntraVpcSupernet, 'IntraVpc subnets', awsAccount)
            outputIntraVpcSubnets = response.json()['result']['network']

            response = createNetwork(outputIntraVpcSubnets, netSize_IntraVpc, 'IntraVpc1', awsAccount)
            outputAz1IntraVpc = response.json()['result']['network']

            response = createNetwork(outputIntraVpcSubnets, netSize_IntraVpc, 'IntraVpc2', awsAccount)
            outputAz2IntraVpc = response.json()['result']['network']
            
            response = createNetwork(outputIntraVpcSubnets, netSize_IntraVpc, 'IntraVpc3', awsAccount)
            outputAz3IntraVpc = response.json()['result']['network']

            response = createNetwork(outputIntraVpcSubnets, netSize_IntraVpc, 'Spare', awsAccount)
            outputSpare = response.json()['result']['network']

            responseData = {
                "PhysicalResourceId": physicalResourceId,
                "outputVpcCidrBlock": outputVpcCidrBlock,
                "outputPublicIntraVpcSubnets": outputPublicIntraVpcSubnets,
                "outputAz1Public": outputAz1Public,
                "outputAz2Public": outputAz2Public,
                "outputAz3Public": outputAz3Public,
                "outputIntraVpcSubnets": outputIntraVpcSubnets,
                "outputAz1IntraVpc": outputAz1IntraVpc,
                "outputAz2IntraVpc": outputAz2IntraVpc,
                "outputAz3IntraVpc": outputAz3IntraVpc,
                "outputSpare": outputSpare,
                "outputAz1Private": outputAz1Private,
                "outputAz2Private": outputAz2Private,
                "outputAz3Private": outputAz3Private
            }

            print('Created networkcontainers and subnets in range', outputVpcCidrBlock, 'for', vpcSize, 'sized VPC')
            return 'SUCCESS', responseData, ''

        elif response.status_code == 400 and 'Can not find requested number of networks' in response.text:
            errMsg = 'No space left in range ' + netParent
            print(errMsg)
            return 'FAILED', {"PhysicalResourceId": "none"}, errMsg
            
        else:
            try:
                error_details = response.json().get('text', response.reason)
            except json.JSONDecodeError:
                error_details = response.text
            
            errMsg = f"API Error ({response.status_code}): {error_details}"
            print(errMsg)
            return 'FAILED', {"PhysicalResourceId": "none"}, errMsg
    
    else:
        errMsg = 'API request raised exception on create call!'
        print(errMsg)
        return 'FAILED', {"PhysicalResourceId": "none"}, errMsg


def delete(physicalResourceId):
	response = deleteNetwork(physicalResourceId)
	if response != 'FAILED':
		if response.status_code == 200:
			print('Deleted networkcontainer with ref', physicalResourceId, 'as well as all its child objects')
			return 'SUCCESS', ''
		elif response.status_code == 404:
			print('Networkcontainer with ref', physicalResourceId, "was not found, so it's already deleted")
			return 'SUCCESS', ''
		else:
			errMsg = 'Received status code ' + str(response.status_code) + ' ' + response.reason + ' from API on delete call, request failed!'
			print(errMsg)
			return 'FAILED', errMsg
	else:
		errMsg = 'API request raised exception on delete call!'
		print(errMsg)
		return 'FAILED', errMsg

if __name__ == "__main__":
    
    # --- Script Configuration ---
    ACTION          = 'CREATE'  
    DEPLOYMENT_NAME = "Test-Debug_Vpc_CIDR_IpAddresses"
    VPC_SIZE        = 'S'
    REGION          = 'eu-west-1'
    AWS_ACCOUNT_ID  = "000000000000"
    
# Generate a unique ID to track the deployment
    uniqueId = hashlib.sha256(DEPLOYMENT_NAME.encode()).hexdigest()

    # Simulate metadata required by the core functions
    mock_stackId = f"arn:aws:ec2:{REGION}:{AWS_ACCOUNT_ID}:vpc/local-execution"
    stackInfo = f"Local execution for deployment: {DEPLOYMENT_NAME}"

    # --- Initial tracking information ---
    print("-" * 65)
    print("To find this deployment in Infoblox, use the following identifier:")
    print(f"   Attribute '{apiUniqueExtattr}': {uniqueId}")
    print("-" * 65)

    print(f"--- Action: {ACTION} for deployment: {DEPLOYMENT_NAME} ---")

    if ACTION.upper() == 'CREATE':
        exists, _ = searchNetworkcontainer(uniqueId)
        if exists == 'EXISTS':
            print(f"Warning: A deployment named '{DEPLOYMENT_NAME}' already exists. Please delete it first.")
        elif exists == 'FAILED':
            print("Error: Failed to search for an existing container.")
        else:
            print("Initiating network provisioning...")
            
            # Capture the return values from the create function
            result, responseData, reason = create(mock_stackId, VPC_SIZE, uniqueId, stackInfo)
            
            # --- Detailed post-creation report ---
            if result == 'SUCCESS':
                print("\n" + "="*25 + " PROVISIONING REPORT " + "="*25)
                print("Operation completed successfully.")
                print(f"   - Primary network block allocated: {responseData.get('outputVpcCidrBlock', 'N/A')}")
                print(f"   - Root container's Infoblox reference (_ref):")
                print(f"     {responseData.get('PhysicalResourceId', 'N/A')}")
                print("="*71 + "\n")
            else:
                print(f"Error: Provisioning failed. Reason: {reason}")

    elif ACTION.upper() == 'DELETE':
        print(f"Searching for the container associated with '{DEPLOYMENT_NAME}'...")
        exists, netRef = searchNetworkcontainer(uniqueId)

        if exists == 'EXISTS':
            physicalResourceId = netRef[0]['_ref']
            network_cidr = netRef[0]['network']
            
            # --- Pre-deletion confirmation ---
            print(f"  -> Container found: {network_cidr} (_ref: {physicalResourceId})")
            print("Initiating deletion...")
            
            result, reason = delete(physicalResourceId)
            
            # --- Post-deletion confirmation ---
            if result == 'SUCCESS':
                print("Deletion completed successfully.")
            else:
                print(f"Error: Deletion failed. Reason: {reason}")
                
        elif exists == 'INEXISTENT':
            print(f"Info: No deployment named '{DEPLOYMENT_NAME}' was found. No action taken.")
        else:
            print("Error: Failed to search for the container to be deleted.")

    else:
        print(f"Error: Unrecognized action '{ACTION}'. Please use 'CREATE' or 'DELETE'.")

    print("--- Script execution finished ---")