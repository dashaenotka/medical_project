from django import forms

class MedicalForm(forms.Form):
    name = forms.CharField(label='ФИО пациента', max_length=100)
    height = forms.IntegerField(label='Рост (см)', min_value=50, max_value=250)
    pressure = forms.CharField(label='Давление', max_value=20)
    glucose = forms.DecimalField(label='Глюкоза', max_digits=4, decimal_places=1)
    age = forms.DecimalField(label='Возраст', min_value=0,max_value=100)