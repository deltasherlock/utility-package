from datetime import date
from django.db import models
from deltasherlock.common.io import DSEncoder, DSDecoder
from deltasherlock.common.changesets import Changeset, ChangesetRecord
from deltasherlock.common.fingerprinting import Fingerprint, FingerprintingMethod

# Create your models here.

class EventLabel(models.Model):
    """
    Used to hold "event" (usually an app installation) labels
    """
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class QueueItem(models.Model):
    client_ip = models.GenericIPAddressField(verbose_name="Submitting Client IP")
    submission_time = models.DateTimeField()
    endpoint_url = models.URLField()
    parameters = models.CharField(max_length=255, blank=True)
    request_text = models.TextField(verbose_name="Full HTTP Resquest Text")
    rq_id = models.CharField(max_length=50, verbose_name="RQ Job ID")
    result_labels = models.ManyToManyField(EventLabel, verbose_name="Predicted Labels", blank=True)
    delivery_time = models.DateTimeField(null=True, blank=True)

class DeltaSherlockWrapper(models.Model):
    labels = models.ManyToManyField(EventLabel, blank=True)
    predicted_quantity = models.IntegerField()
    json_data = models.TextField()

    def wrap(self, object_to_wrap):
        self.predicted_quantity = object_to_wrap.predicted_quantity
        self.json_data = DSEncoder().encode(object_to_wrap)
        self.save()
        #Now that we have an ID, we can add labels

        #Loop through each label in the raw object
        for label in object_to_wrap.labels:
            #See if there's already an EventLabel in the DB for that
            label_qset = EventLabel.objects.filter(name=label)
            event_label = None

            if not label_qset.exists():
                #Create one if it doesn't exist
                event_label = EventLabel.objects.create(name=label)
            else:
                #Use the existing one if it does
                event_label = label_qset[0]

            # Add the relationship
            self.labels.add(event_label)

        self.save()

    def unwrap(self):
        return DSDecoder().decode(self.json_data)

    class Meta:
        abstract = True

class ChangesetWrapper(DeltaSherlockWrapper):
    open_time = models.DateTimeField()
    close_time = models.DateTimeField()

    def wrap(self, object_to_wrap):
        super().wrap(object_to_wrap)
        self.open_time = date.fromtimestamp(object_to_wrap.open_time)
        self.close_time = date.fromtimestamp(object_to_wrap.close_time)
        self.save()

    def __str__(self):
        return "CS" + str(self.id) + ": PQ="+str(self.predicted_quantity)+" OT=" + str(self.open_time) + " CT=" + str(self.close_time)

class FingerprintWrapper(DeltaSherlockWrapper):
    method = models.IntegerField()
    origin_changeset = models.ManyToManyField(ChangesetWrapper, blank=True)

    def wrap(self, object_to_wrap):
        super().wrap(object_to_wrap)
        self.method = object_to_wrap.method
        self.save()
