from django.db import models

# Create your models here.


class Organisation(models.Model):
    org_id = models.CharField(max_length = 255)

class Ec2(models.Model):
    ec2_id = models.CharField(max_length = 255)
    instance_type = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    organisation_id = models.ForeignKey(Organisation, on_delete = models.CASCADE, null = True)

class ElasticIp(models.Model):
    ec2_id = models.ForeignKey(Ec2, on_delete = models.CASCADE, null = True)
    ip = models.CharField(max_length=45)
    organisation_id = models.ForeignKey(Organisation, on_delete = models.CASCADE, null = True)