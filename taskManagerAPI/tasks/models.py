from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Task(models.Model):

    class Meta:
        ordering = ['-created_at']
        indexes = [
        models.Index(fields=['owner']),
        models.Index(fields=['status']),
        models.Index(fields=['priority']),
        models.Index(fields=['due_date']),
        models.Index(fields=['owner', 'status']),  # composite index
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="medium")
    due_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
