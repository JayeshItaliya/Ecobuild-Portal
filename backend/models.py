import uuid

from django.db import models
from django.utils import timezone

from backend import settings
from backend.manager import SoftDeletionManager


class SoftDeleteBaseModel(models.Model):
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="%(class)s_deleted_by",
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    def delete(self, deleted_by_user=None, soft=True):
        """Delete: soft by default, or hard if soft=False"""
        if soft:
            self.deleted_at = timezone.now()
            if deleted_by_user and deleted_by_user.is_authenticated:
                self.deleted_by = deleted_by_user
            self.save(update_fields=["deleted_at", "deleted_by"])
            self._cascade_soft_delete(deleted_by_user)
        else:
            self.hard_delete()

    def _cascade_soft_delete(self, deleted_by_user=None):
        """Soft delete related objects that also support soft delete"""
        for related in self._meta.related_objects:
            accessor = related.get_accessor_name()
            related_manager = getattr(self, accessor, None)

            if related_manager:
                # For OneToOne or ForeignKey
                related_objects = (
                    related_manager.all()
                    if hasattr(related_manager, "all")
                    else [related_manager]
                )

                for obj in related_objects:
                    if isinstance(obj, SoftDeleteBaseModel) and not obj.deleted_at:
                        obj.delete(deleted_by_user=deleted_by_user, soft=True)

    def restore(self):
        self.deleted_at = None
        self.deleted_by = None
        self.save(update_fields=["deleted_at", "deleted_by"])
        self._cascade_restore()

    def _cascade_restore(self):
        """Restore related soft-deleted models"""

        for related in self._meta.related_objects:
            accessor = related.get_accessor_name()
            related_manager = getattr(self, accessor, None)

            if related_manager:
                related_objects = (
                    related_manager.all()
                    if hasattr(related_manager, "all")
                    else [related_manager]
                )

                for obj in related_objects:
                    if isinstance(obj, SoftDeleteBaseModel) and obj.deleted_at:
                        obj.restore()

    def hard_delete(self):
        """Permanently delete the object and related models"""

        for related in self._meta.related_objects:
            accessor = related.get_accessor_name()
            related_manager = getattr(self, accessor, None)

            if related_manager:
                related_objects = (
                    related_manager.all()
                    if hasattr(related_manager, "all")
                    else [related_manager]
                )

                for obj in related_objects:
                    if isinstance(obj, SoftDeleteBaseModel):
                        obj.hard_delete()
                    else:
                        obj.delete()
        super().delete()


class BaseModel(SoftDeleteBaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by",
    )
    objects = SoftDeletionManager()

    class Meta:
        abstract = True
