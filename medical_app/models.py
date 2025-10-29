from django.db import models

class Patient(models.Model):
    name = models.CharField(max_length=100)
    height = models.IntegerField()
    pressure = models.CharField(max_length=20)
    glucose = models.DecimalField(max_digits=4, decimal_places=1)
    age = models.IntegerField()
    
    class Meta:
        unique_together = ['name', 'age']  # ← имя + возраст
    
    def __str__(self):
        return self.name