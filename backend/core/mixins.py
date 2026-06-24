"""
Reusable Django model mixins for the UAV Digital Twin Platform.

These abstract base classes provide common fields and behaviour that can be
composed into any concrete model via multiple inheritance.
"""

from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    """
    Adds ``created_at`` and ``updated_at`` fields to any model.

    ``created_at`` is set once on first save; ``updated_at`` is refreshed
    on every subsequent save.
    """

    created_at = models.DateTimeField(
        "created at",
        auto_now_add=True,
        db_index=True,
        help_text="Timestamp when the record was created.",
    )
    updated_at = models.DateTimeField(
        "updated at",
        auto_now=True,
        help_text="Timestamp when the record was last modified.",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteMixin(models.Model):
    """
    Implements soft-delete semantics via an ``is_deleted`` flag.

    Records marked as deleted remain in the database for audit purposes
    but are excluded from default querysets via the custom manager.

    Usage::

        class Drone(SoftDeleteMixin, TimestampMixin, models.Model):
            ...

        Drone.objects.all()         # excludes soft-deleted
        Drone.all_objects.all()     # includes soft-deleted
    """

    is_deleted = models.BooleanField(
        "soft deleted",
        default=False,
        db_index=True,
        help_text="If True, the record is considered deleted.",
    )
    deleted_at = models.DateTimeField(
        "deleted at",
        null=True,
        blank=True,
        help_text="Timestamp when the record was soft-deleted.",
    )

    class Meta:
        abstract = True

    # ------------------------------------------------------------------
    # Managers
    # ------------------------------------------------------------------
    class ActiveManager(models.Manager):
        """Default manager that filters out soft-deleted records."""

        def get_queryset(self):
            return super().get_queryset().filter(is_deleted=False)

    objects = ActiveManager()
    all_objects = models.Manager()

    # ------------------------------------------------------------------
    # Soft-delete helpers
    # ------------------------------------------------------------------
    def soft_delete(self) -> None:
        """Mark the record as deleted without removing it from the DB."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])

    def restore(self) -> None:
        """Restore a previously soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
