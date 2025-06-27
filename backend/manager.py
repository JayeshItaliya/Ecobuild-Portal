from django.db import models


class SoftDeletionManager(models.Manager):
    def all_with_deleted(self):
        return super().get_queryset()

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def only_deleted(self):
        return super().get_queryset().exclude(deleted_at__isnull=True)
