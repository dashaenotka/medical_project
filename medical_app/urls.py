from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_patients, name='search_patients'),
    path('patient/<int:patient_id>/update/', views.update_patient, name='update_patient'),
    path('patient/<int:patient_id>/delete/', views.delete_patient, name='delete_patient'),
]