from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
    ]
    
    RECURRENCE_CHOICES = [
    ('None', 'One Time'),
    ('Daily', 'Everyday'),
    ('Weekdays', 'Weekdays'),
    ('Weekend', 'Weekend'),
    ('Custom', 'Custom'),
]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    

    recurrence = models.CharField(
        max_length=20,
        choices=RECURRENCE_CHOICES,
        default='None'
    )
    
    days = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.title   
    
