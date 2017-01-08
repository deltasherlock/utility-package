# DeltaSherlock
BU PEACLab's implementation of System-Change-Discovery-as-a-Service

**After following the installation guide below, see the Wiki (on GitHub) for tips for getting started**

## Repo Organization
This repository contains two _separate_ Python applications: the DeltaSherlock **utility package**, and the DeltaSherlock **[Django](https://www.djangoproject.com) server**. The entirety of the Django server can be found in the `django-server` directory, and that directory is structured in [typical Django project fashion](https://docs.djangoproject.com/en/1.10/intro/tutorial01/#creating-a-project). The remaining directories make up the utility package, and are organized as follows:
* `common` contains modules useful to all components of DeltaSherlock. Notably, this package contains the definitions of the `Changeset` and `Fingerprint` datatypes.
* `client` contains modules used strictly on the client-side, like the `DeltaSherlockWatchdog`
* `server` contains modules used strictly on the server-side, such as the actual machine learning model prediction code and the job queuing system's `worker.py` script. Note that this package *does not* contain any code defining the RESTful API, admin interface, or other Django related items; those can all be found in `django-server`

