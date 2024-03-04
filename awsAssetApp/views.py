from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt 
from django.http import JsonResponse

import json

from .awsUtils import addOrUpdateAsset
from .models import *

# Create your views here.
@csrf_exempt
def getAssets(request):
    try:
        request.method!="POST"

        data = json.loads(request.body)

        org_id = data.get("organisation_id")
        
        checkOrg_Object = (Organisation.objects.filter(org_id = org_id)).exists()
        newObject = []
        if checkOrg_Object!=True:
            newOrgObject = (Organisation(org_id=org_id))
            newOrgObject.save()
            newObject.append(newOrgObject)
        else:
            existingObject = Organisation.objects.get(org_id = org_id)

        type = data.get("type")

        if type == "new":
            response = addOrUpdateAsset(org_id,newObject[0])

            return JsonResponse({
                "status":"Success",
                "message":"new organisation data saved on db"
            })
        else:
            response = addOrUpdateAsset(org_id,existingObject)

            return JsonResponse({
                "status":"Success",
                "message":"existing organisation data updated on db"
            })


    except Exception as ex:
        return JsonResponse({
            "status":"Failed",
            "message":f"{request.method} not allowed"
        })

