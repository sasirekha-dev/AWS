from django.db import models

# Create your models here.


class Employee(models.Model):
    workerID = models.IntegerField(primary_key=True, null=False)
    firstName = models.CharField(max_length=30, null=False)
    lastName = models.CharField(max_length=30, null=False)
    managerID = models.ForeignKey("Employee", null=True,
                                  on_delete=models.SET_NULL)


class LeaveHistory(models.Model):
    leaveID = models.BigAutoField(primary_key=True, null=False)
    workerID = models.ForeignKey(
        Employee, null=True, on_delete=models.PROTECT, related_name='FK1')
    status = models.CharField(max_length=10, null=False)
    managerID = models.ForeignKey(
        Employee, null=True, on_delete=models.PROTECT, related_name='FK2')
    request_created_at = models.DateTimeField(auto_now_add=True)
    vacation_start_date = models.DateTimeField(null=False)
    vacation_end_date = models.DateTimeField(null=False)
