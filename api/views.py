import uuid
import re
import logging
import datetime
import pytz
import json
import requests
import time
from collections import Counter

from pyfcm import FCMNotification

from django.conf.urls import url
from django.utils import timezone
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, MultiPartParser


from api.models import (
    Device,
    Location,
    Event,
    Trip,
    Session
)
from .auth import DemoTokenAuthentication

from math import sin, cos, sqrt, atan2, radians

push_service = FCMNotification(api_key="AAAAwxOFtl0:APA91bFAEvVwO9ZPtZi2gczrXOl2VH72Nx_BeXFwr2jg44LPDiwTqaonjOguxTtAHNrTFSV9c84d2oNiq2Gm-Q0FDiNUlf24lY2eTfMnnQn8pQx3_Hk5L-4kvfHbgqVQk8M1zgNZiIgo")


def calculate_distance(p1,p2):
    # approximate radius of earth in km
    R = 6373.0


    lat1 = radians(p1[0])
    lon1 = radians(p1[1])
    lat2 = radians(p2[0])
    lon2 = radians(p2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance

class GetTokenApi(APIView):

    def post(self, request):
        device_id = request.data.get('device_id')
        device_type_id = request.data.get('device_type_id')

        device, created = Device.objects.get_or_create(device_id=device_id,device_registration_id=device_type_id,defaults={'created_at': timezone.now()})
        try:
            Session.objects.get(device=device).delete()
        except:
            pass
        session = Session.objects.create(device=device)
        print created
        # registration_ids = [i.device_registration_id for i in Device.objects.all()]
        # data_message = {
        #    "latitude" : "45455454",
        #    "longitude" : "55554554",
        #    }
        # message_title = "Rapido update"
        # message_body = "Police on your route!!"
        # result = push_service.notify_multiple_devices(registration_ids=registration_ids,
        #     message_title=message_title, message_body=message_body, data_message=data_message)
        return Response({
            "status": "OK",
            "token": session.token,
            "device": device.id,
        }, status=status.HTTP_200_OK
        )



class UpdateTokenApi(APIView):

    def post(self, request):
        device_id = request.data.get('device_id')
        device_type_id = request.data.get('device_type_id')

        print device_id, device_type_id
        device = Device.objects.get(device_id=device_id)
        device.device_registration_id = device_type_id
        device.save()

        # registration_ids = [i.device_registration_id for i in Device.objects.all()]
        # message_title = "Rapido update"
        # message_body = "Police on your route!!"
 
        # result = push_service.notify_multiple_devices(registration_ids=registration_ids,
        #     message_title=message_title, message_body=message_body)
        return Response({
            "status": "OK",
            "token": device_type_id,
        }, status=status.HTTP_200_OK
        )




class CreateEventApi(APIView):

    authentication_classes = (DemoTokenAuthentication,)
    def post(self, request):
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        location = Location.objects.create(latitude=latitude,longitude=longitude)
        image = request.data.get('image')
        if image:
            event = Event.objects.create(location=location,device=request.user,image=image)
        else:
            event = Event.objects.create(location=location,device=request.user)

        trips = Trip.objects.filter(finished=False)
        p2 = [float(latitude),float(longitude)]
        valid_trips = []
        for trip in trips:
            for p in trip.path.all():
                p1 = [float(p.latitude),float(p.longitude)]
                distance = calculate_distance(p1,p2)
                if distance <=0.01:
                    valid_trips.append(trip)
                    break 

        temp = {"image":"", "location":[float(event.location.latitude),float(event.location.longitude)],
                    "upvote":event.upvote,"downvote":event.downvote,
                    "percentage":(event.upvote/float(event.upvote+event.downvote))*100,
                    "eventKey":event.event_key}            
        registration_ids = [i.device.device_registration_id for i in valid_trips]
        data_message = {
           "event" : temp,
           }
        message_title = "Rapido update!"
        message_body = "Police on your route!!"
        result = push_service.notify_multiple_devices(registration_ids=registration_ids,
            message_title=message_title, message_body=message_body, data_message=data_message)
        return Response({
            "status": "OK"
        }, status=status.HTTP_200_OK
        )


class StartTripApi(APIView):

    authentication_classes = (DemoTokenAuthentication,)
    def post(self, request):
        pathlist = request.data.get('path')
        path_objects = []
        for sets in json.loads(pathlist):
            path_objects.append(Location(latitude=sets["latitude"], longitude=sets["longitude"]))
        Location.objects.bulk_create(path_objects)
        trip = Trip.objects.create(device=request.user)
        trip.path.add(*path_objects)
        return Response({
            "status": "OK",
            "tripKey": trip.trip_key
        }, status=status.HTTP_200_OK
        )


class StopTripApi(APIView):

    authentication_classes = (DemoTokenAuthentication,)
    def post(self, request):
        trip_key = request.data.get('tripKey')
        trip = Trip.objects.get(trip_key=trip_key)
        trip.finished = True
        trip.save()
        return Response({
            "status": "OK"
        }, status=status.HTTP_200_OK
        )


class CheckEventApi(APIView):

    authentication_classes = (DemoTokenAuthentication,)
    def post(self, request):
        trip_key = request.data.get('tripKey')
        events = Event.objects.select_related('location').all()
        trip = Trip.objects.prefetch_related('path').get(trip_key=trip_key)
        valid_events = []
        for p in trip.path.all():
            p1 = [float(p.latitude),float(p.longitude)]
            for e in events:
                p2 = [float(e.location.latitude),float(e.location.longitude)]
                distance = calculate_distance(p1,p2)
                if distance <=0.01:
                    valid_events.append(e)

        events = []
        for e in valid_events:
            if e.image:
                url = e.image.url
            else:
                url = ""
            temp = {"image":url, "location":[float(e.location.latitude),float(e.location.longitude)],
                    "upvote":e.upvote,"downvote":e.downvote,
                    "percentage":(e.upvote/float(e.upvote+e.downvote))*100,
                    "eventKey":e.event_key}
            events.append(temp)

        return Response({
            "status": "OK",
            "events": events
        }, status=status.HTTP_200_OK
        )


class UpvoteEventApi(APIView):

    authentication_classes = (DemoTokenAuthentication,)
    def post(self, request):
        event_key = request.data.get('eventKey')
        event = Event.objects.get(event_key=event_key)
        event.upvote += 1
        event.save()
        return Response({
            "status": "OK",
            "upvote":event.upvote,
            "downvote":event.downvote,
            "percentage":(event.upvote/float(event.upvote+event.downvote))*100
        }, status=status.HTTP_200_OK
        ) 

class DownvoteEventApi(APIView):

    authentication_classes = (DemoTokenAuthentication,)
    def post(self, request):
        event_key = request.data.get('eventKey')
        event = Event.objects.get(event_key=event_key)
        event.downvote += 1
        event.save()
        return Response({
            "status": "OK",
            "upvote":event.upvote,
            "downvote":event.downvote,
            "percentage":(event.upvote/float(event.upvote+event.downvote))*100
        }, status=status.HTTP_200_OK
        )  