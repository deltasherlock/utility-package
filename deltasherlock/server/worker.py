"""
Contains methods to be executed via an RQ queue
"""


def process_fingerprint(fingerprint_json_str: str, endpoint_url: str, client_ip: str, parameters: dict, django_params: dict = None) -> list:
    import pickle
    from deltasherlock.common.io import DSDecoder
    from deltasherlock.common.fingerprinting import Fingerprint
    from deltasherlock.server.learning import MLModel, MLAlgorithm

    # Basically, we have to load the model from file and predict against it
    fingerprint = DSDecoder().decode(fingerprint_json_str)
    model_path = "/tmp/DS_MLModel"  # + str(int(fingerprint.method))
    model = pickle.load(open(model_path, "rb"))

    # TODO notify the endpoint IP!
    if endpoint_url is not None:
        import re
        # Borrowed from Django's URLValidator
        urlregex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        #If url is valid
        if urlregex.fullmatch(endpoint_url) is not None:
            from time import time
            from requests import post
            post_data = {'done_time' : time(),
                         'client_ip' : client_ip,
                         'prediction' : prediction}
            post(endpoint_url, json = post_data)

    prediction = model.predict(fingerprint)

    print(str(prediction))

    # Now we have to dial back into Django to update the database
    if django_params is not None:
        import os
        import sys
        import django
        from rq import get_current_job
        os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                              django_params['settings_module'])
        sys.path.append(django_params['proj_path'])
        os.chdir(django_params['proj_path'])
        django.setup()
        from deltasherlock_server.models import QueueItem

        # Now we have access to the database, so get the QueueItem
        q = QueueItem.objects.get(rq_id=get_current_job().id)
        q.rq_complete(prediction)

    return(prediction)
