# Generated by Django 5.0.2 on 2024-03-04 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('awsAssetApp', '0005_alter_ec2_instance_type_alter_ec2_region_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ec2',
            name='awsStatus',
            field=models.CharField(default=None, max_length=255),
        ),
    ]
