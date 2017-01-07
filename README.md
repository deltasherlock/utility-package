# DeltaSherlock
BU PEACLab's implementation of System-Change-Discovery-as-a-Service

**After following the installation guide below, see the Wiki (on GitHub) for tips for getting started**

## Repo Organization
This repository contains two _separate_ Python applications (although one depends on the other): the DeltaSherlock **utility package**, and the DeltaSherlock **Django server**

client contains all client code

common contains code required by all packages

server contains code implementing the server's learning functionality (in pure Python)

django-server contains the django implementation of the server (like the API, queuing, etc)
