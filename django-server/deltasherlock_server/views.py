"""
The "view" part of the "Model-View-Controller" pattern is defined here. Essentially,
these methods are the first to receive each client HTTP request (after the URL
dispatcher). Remember that these views are unreachable unless you route them
within "urls.py"
"""
import os
from django.conf import settings
from django.shortcuts import render
from deltasherlock_server.models import QueueItem
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
        # TODO Log all errors!

        # First connect to Redis
        try:
            q = Queue(connection=Redis())
        except:
            return Respone("Could not reach Redis", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Then submit the job to RQ
        rq_job = None
        try:
            django_params = {
                "proj_path": settings.BASE_DIR,
                "settings_module": os.environ.get("DJANGO_SETTINGS_MODULE"),
            }

            rq_job = q.enqueue('deltasherlock.server.worker.process_fingerprint',
                               request.data['fingerprint'],
                               request.data['endpoint_url'],
                               request.data['parameters'],
                               django_params)
        except:
            return Response("Rejected by job queue. Check submission data and try again.", status=status.HTTP_400_BAD_REQUEST)

        # Finally, create a record of the request in the QueueItem database
        queue_id = QueueItem().from_request(request=request, rq_id=rq_job.id)

        return Response(queue_id, status=status.HTTP_202_ACCEPTED)


class QueueInfo(APIView):
    """
    Fetch information about a RQ job
    """

    def get(self, request, format=None):
        q = Queue(connection=Redis())
        job = q.fetch_job(request.data['id'])
