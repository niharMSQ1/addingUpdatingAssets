import boto3
import copy

from django.conf import settings

from .models import *


def addOrUpdateAsset(org_id, orgObject):
    try:
        active_regions = get_regions_and_org_ids()

        allInstances = get_ec2_instances_in_regions(active_regions)

        for region, instances in allInstances.items():
            for instance in instances:
                ec2_instance, created = Ec2.objects.get_or_create(ec2_id=instance['id'])

                updated_fields = {
                    'instance_type': instance['type'],
                    'state': instance['status'],
                    'region': region,
                    'isActive': True if instance['status'] == 'running' else False,
                    'organisation_id': orgObject,
                    'awsStatus': AWSStatus.PRESENT.value
                }
                
                # Updating or creating instance
                for field, value in updated_fields.items():
                    setattr(ec2_instance, field, value)
                
                ec2_instance.save()
            
            
            allEc2Objs = list(Ec2.objects.all())
            db_instances = [i.ec2_id for i in allEc2Objs]
            
            aws_instances = [j['id'] for j in instances]

            deleted_instances = list(set(db_instances) - set(aws_instances))
            if len(deleted_instances) > 0:
                for i in deleted_instances:
                    ec2Obj = Ec2.objects.get(ec2_id=i)
                    if ec2Obj.awsStatus != AWSStatus.DELETED.value:
                        ec2Obj.instance_type = None
                        ec2Obj.state = None
                        ec2Obj.isActive = False
                        ec2Obj.region = None
                        ec2Obj.awsStatus = AWSStatus.DELETED.value
                        ec2Obj.save()

        allElasticIps = get_elastic_ips_with_instances(org_id)

        if not allElasticIps:
            if ElasticIp.objects.exists():
                ElasticIp.objects.update(ec2_id=None, current_status=Elastic_ip_Existence.DELETED_FROM_AWS.value)
        else:
            for ip, instance_id in allElasticIps.items():
                if instance_id is None:
                    elastic_ip, _ = ElasticIp.objects.get_or_create(ip=ip, defaults={'ec2_id': None, 
                                                                                        'organisation_id': orgObject
                                                                                        })
                    elastic_ip.ec2_id = None
                    elastic_ip.organisation_id = orgObject
                    elastic_ip.current_status = Elastic_ip_Existence.DISASSOCIATION.value
                    elastic_ip.save()
                else:
                    ec2_instance, _ = Ec2.objects.get_or_create(ec2_id=instance_id)
                    elastic_ip, _ = ElasticIp.objects.get_or_create(ip=ip, defaults={'ec2_id': ec2_instance if ec2_instance else None, 
                                                                                    'organisation_id': orgObject
                                                                                    })
                    elastic_ip.ec2_id = ec2_instance
                    elastic_ip.organisation_id = orgObject
                    elastic_ip.current_status = Elastic_ip_Existence.ASSOCIATION.value
                    elastic_ip.save()
        
        return True

    except Exception as e:
        return str(e)


def get_regions_and_org_ids():
    try:
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

        return {'regions': active_regions}
    
    except Exception as e:
        return str(e)


def get_ec2_instances_in_regions(active_regions):
    try:
        ec2_instances = {}
        for region in active_regions['regions']:
            ec2_client = boto3.client('ec2', 
                                      region_name=region,
                                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
            response = ec2_client.describe_instances()
            instances_data = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_id = instance['InstanceId']
                    instance_type = instance['InstanceType']
                    instance_status = instance['State']['Name']
                    instances_data.append({'id': instance_id, 'type': instance_type, 'status': instance_status})
            ec2_instances[region] = instances_data

        return ec2_instances
    
    except Exception as e:
        return str(e)


def get_elastic_ips_with_instances(org_id):
    try:
        elastic_ips_with_instances = {}

        ec2_client = boto3.client('ec2',
                                  region_name='ap-south-1',
                                  aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        response = ec2_client.describe_addresses()

        for address in response['Addresses']:
            elastic_ip = address['PublicIp']
            instance_id = address.get('InstanceId')
            if instance_id:
                elastic_ips_with_instances[elastic_ip] = instance_id
            else:
                elastic_ips_with_instances[elastic_ip] = None

        return elastic_ips_with_instances
    
    except Exception as e:
        return str(e)
