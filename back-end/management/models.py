from django.db import models

# Create your models here.
class Customer(models.Model):
    ID=models.CharField(max_length=10,primary_key=True)
    name=models.CharField(max_length=50)
    Contact=models.CharField(max_length=15)

class Vehicle(models.Model):
    # Brand=models.CharField(max_length=50,primary_key=True)
    Model=models.CharField(max_length=50,primary_key=True)
    Price=models.IntegerField()

class Repository(models.Model):
    Car_ID=models.CharField(max_length=10,primary_key=True)
    Is_leased=models.BooleanField(default=False)

class Info(models.Model):
    Car_ID = models.ForeignKey('Repository', on_delete=models.CASCADE)
    # Brand = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='info_brand')
    Model = models.ForeignKey('Vehicle', on_delete=models.CASCADE, related_name='info_model')

class Lease(models.Model):
    Car_ID = models.ForeignKey('Repository', on_delete=models.CASCADE)
    ID = models.ForeignKey('Customer', on_delete=models.CASCADE)
