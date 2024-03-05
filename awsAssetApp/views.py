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
        if request.method != "POST":
            return JsonResponse({
                "status": "Failed",
                "message": "Only POST requests are allowed"
            }, status=405)  # Method Not Allowed

        data = json.loads(request.body)

        org_id = data.get("organisation_id")
        
        checkOrg_Object = Organisation.objects.filter(org_id=org_id).exists()
        newObject = []
        if not checkOrg_Object:
            newOrgObject = Organisation(org_id=org_id)
            newOrgObject.save()
            newObject.append(newOrgObject)
        else:
            existingObject = Organisation.objects.get(org_id=org_id)

        type = data.get("type")

        if type == "new":
            response = addOrUpdateAsset(org_id, newObject[0])

            return JsonResponse({
                "status": "Success",
                "message": "New organisation data saved in the database"
            })
        elif type == "update":
            response = addOrUpdateAsset(org_id, existingObject)

            return JsonResponse({
                "status": "Success",
                "message": "Existing organisation data updated in the database"
            })
        else:
            return JsonResponse({
                "status": "Failed",
                "message": "Invalid 'type' parameter"
            }, status=400)  # Bad Request

    except Exception as ex:
        return JsonResponse({
            "status": "Failed",
            "message": str(ex)
        }, status=500)
