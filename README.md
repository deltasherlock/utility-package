# DeltaSherlock Utility Package
BU PEACLab's implementation of System-Change-Discovery-as-a-Service

**After following the installation guide below, see the [wiki](https://github.com/deltasherlock/utility-package/wiki/) for tips for getting started**

## A Note on Repo Organization
This repository contains the DeltaSherlock **utility package**. If you're looking for the the DeltaSherlock **[Django](https://www.djangoproject.com) server**, head over to [django-server](https://github.com/deltasherlock/django-server/).
* `common` contains modules useful to all components of DeltaSherlock. Notably, this package contains the definitions of the `Changeset` and `Fingerprint` datatypes.
* `client` contains modules used strictly on the client-side, like the `DeltaSherlockWatchdog`
* `server` contains modules used strictly on the server-side, such as the actual machine learning model prediction code and the job queuing system's `worker.py` script. Note that this package *does not* contain any code defining the RESTful API, admin interface, or other Django related items; those can all be found in [django-server](https://github.com/deltasherlock/django-server/)

## Installation
1. Ensure your system's up to date: `sudo apt update && sudo apt upgrade`
2. Install PIP and ensure it's up to date: `sudo apt install python3-pip && sudo pip3 install --upgrade pip`
3. Install (or update) dependencies: `sudo pip3 install --upgrade watchdog numpy scipy gensim sklearn`
4. Clone this repo somewhere easy, like to your home directory: `git clone https://github.com/deltasherlock/utility-package.git`
5. Add the `deltasherlock` directory to somewhere in your **global*** PYTHONPATH. If, for example, the `deltasherlock` directory is located at `/home/ubuntu/utility-package/deltasherlock` and `/usr/lib/python3/dist-packages` is in your PYTHONPATH (it usually is), then the easiest way to make the link is by running: `sudo ln -s /home/ubuntu/utility-package/deltasherlock /usr/lib/python3/dist-packages/`
6. Test that you can import the package by running `python3 -c "import deltasherlock"`. If all is well, the command won't print anything (other than possibly a few warnings; as long as there are no exceptions/errors, the warnings can be safely ignored).

_Technically_, you're done, but if you're planning on using the `DeltaSherlockWatchdog` at any point (i.e. by running anything in `tests`) then you should take preemptive action by [raising your inotify watch limit](https://github.com/deltasherlock/utility-package/wiki/A-Note-About-inotify-Limits).

_*Ensuring that deltasherlock is in your system's global PYTHONPATH (as opposed to just your user's) will save you lots of trouble later on when you're testing the client code_
