from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from redis import Redis
from rq import Queue

class FingerprintSubmit(APIView):
    """
    Submit a fingerprint to the queue
    """
    def post(self, request, format=None):
        q = Queue(connection=Redis())
        print(request.data)
        job = q.enqueue('deltasherlock.server.worker.process_fingerprint', request.data['fingerprint'], request.data['endpoint_url'], request.data['parameters'])
        return Response(job.id, status=status.HTTP_202_ACCEPTED)
