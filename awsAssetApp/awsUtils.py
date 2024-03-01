import boto3
import json

from django.conf import settings

from .models import *

def saveNewAsset(org_id,orgObject):
    active_regions = get_regions_and_org_ids()

    allInstances = get_ec2_instances_in_regions(active_regions)

    for region, instances in allInstances.items():
        for instance in instances:
            ec2_instance = Ec2(
                ec2_id=instance['id'],
                instance_type=instance['type'],
                state=instance['status'],
                region=region,
                organisation_id = orgObject
            )
            ec2_instance.save()

    allElasticIps = get_elastic_ips_with_instances(org_id)
    for ip, instance_ids in allElasticIps.items():
        for instance_id in instance_ids:
            elastic_ip = ElasticIp(ip=ip, ec2_id=Ec2.objects.get(ec2_id=instance_id),organisation_id = orgObject)
            elastic_ip.save()


    
def updateAsset(org_id,existingObject):
    active_regions = get_regions_and_org_ids()


def get_regions_and_org_ids():

    session = boto3.session.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name='us-east-1' 
    )

    all_regions = [region['RegionName'] for region in session.client('ec2').describe_regions()['Regions']]

    active_regions = []
    for region in all_regions:
        ec2 = session.resource('ec2', region_name=region)
        instances = list(ec2.instances.all())
        if instances:
            active_regions.append(region)

    org_client = session.client('organizations')

    return ({
        'regions': active_regions,
    })


def get_ec2_instances_in_regions(active_regions):
    ec2_instances = {}
    for region in active_regions['regions']:
        try:
            ec2_client = boto3.client(
                'ec2', 
                region_name=region,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            response = ec2_client.describe_instances()
            instances_data = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']
                    instance_status = instance['State']['Name']
                    instances_data.append({'id': instance_id, 'type': instance_type, 'status': instance_status})
            ec2_instances[region] = instances_data
        except Exception as e:
            print(f"Error in region {region}: {e}")
    return ec2_instances

def get_elastic_ips_with_instances(org_id):
    elastic_ips_with_instances = {}

    # Connect to the AWS EC2 service
    ec2_client = boto3.client('ec2',
                              region_name='ap-south-1',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

    # Describe all Elastic IPs
    response = ec2_client.describe_addresses()

    # Extract Elastic IPs and their associations
    for address in response['Addresses']:
        elastic_ip = address['PublicIp']
        instance_id = ((response['Addresses'])[0])['InstanceId']
        
        if instance_id:
            if elastic_ip in elastic_ips_with_instances:
                elastic_ips_with_instances[elastic_ip].append(instance_id)
            else:
                elastic_ips_with_instances[elastic_ip] = [instance_id]

    return elastic_ips_with_instances