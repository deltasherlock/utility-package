# DeltaSherlock Utility Package
BU PEACLab's implementation of System-Change-Discovery-as-a-Service

**After following the installation guide below, see the Wiki (on GitHub) for tips for getting started**

## A Note on Repo Organization
This repository contains the DeltaSherlock **utility package**. If you're looking for the the DeltaSherlock **[Django](https://www.djangoproject.com) server**, head over to [django-server](https://github.com/deltasherlock/django-server/).
* `common` contains modules useful to all components of DeltaSherlock. Notably, this package contains the definitions of the `Changeset` and `Fingerprint` datatypes.
* `client` contains modules used strictly on the client-side, like the `DeltaSherlockWatchdog`
* `server` contains modules used strictly on the server-side, such as the actual machine learning model prediction code and the job queuing system's `worker.py` script. Note that this package *does not* contain any code defining the RESTful API, admin interface, or other Django related items; those can all be found in [django-server](https://github.com/deltasherlock/django-server/)

