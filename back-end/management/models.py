from django.db import models

# Create your models here.
class Customer(models.Model):
    ID=models.CharField(max_length=10,primary_key=True)
    name=models.CharField(max_length=50)
    Contact=models.CharField(max_length=15)

class Vehicle(models.Model):
    Brand=models.CharField(max_length=50,primary_key=True)
    Model=models.CharField(max_length=50,primary_key=True)
    Price=models.IntegerField()

class Repository(models.Model):
    Car_ID=models.CharField(max_length=10,primary_key=True)
    Is_leased=models.BooleanField(default=False)

class Info(models.Model):
    Car_ID=models.CharField(max_length=10,foreign_key=Repository)
    Brand=models.CharField(max_length=50,foreign_key=Vehicle)
    Model=models.CharField(max_length=50,foreign_key=Vehicle)

class Lease(models.Model):
    Car_ID=models.CharField(max_length=10,foreign_key=Repository)
    ID=models.CharField(max_length=10,foreign_key=Customer)
