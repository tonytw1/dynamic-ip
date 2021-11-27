import requests
import sys
import boto3

# Mananged hostnames; remember to include the DNS style trailing dot!
# ie ['hostname.eelpieconsulting.co.uk.']
managed_host_names = []

def get_current_ip():
	# Determine our current public using the ipify API
	url = 'https://api.ipify.org?format=json'
	r = requests.get(url)
	if (r.status_code == 200): 
		ip = r.json()['ip']
		return ip
	return None

current_ip = get_current_ip()
if (current_ip is None):
	print("Could not determine current ip; exiting")
	sys.exit(0)

print("Current ip is: " + current_ip)

# Foreach of our route 53 hosted zones fetch the record sets and look for one of our managed host names
client = boto3.client('route53')
response = client.list_hosted_zones()
hosted_zones = response['HostedZones']
for hosted_zone in hosted_zones:
	zoneId = hosted_zone['Id']
	zoneName = hosted_zone['Name']
	print("Checking hosted zone " + zoneId + ": " + zoneName)
	response = client.list_resource_record_sets(HostedZoneId = zoneId)
	resource_record_sets = response['ResourceRecordSets']
	for resource_record_set in resource_record_sets:
		if resource_record_set['Type'] == 'A':
			name = resource_record_set['Name']
			if name in managed_host_names: 
				print("Found managed A record: " + name)
				print(resource_record_set)
				resource_records = resource_record_set['ResourceRecords']
				value = resource_records[0]['Value']
				if (value != current_ip):
					print("A record value does not match current ip (" + value + " / " + current_ip + ")")
					print("Updating record: ")
					resource_records[0]['Value'] = current_ip
					response = client.change_resource_record_sets(
						HostedZoneId = zoneId,
						ChangeBatch = {	
							'Changes': [
								{
						        	        'Action': 'UPSERT',
									 'ResourceRecordSet': resource_record_set
								}	
							]
						}

					)
					print(response)
			
print("Done")
