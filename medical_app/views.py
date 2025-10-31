from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json
import os
from django.conf import settings
from django.db import IntegrityError
from .models import Patient

def home(request):
    # 1. Подготовка файла
    data_file = os.path.join(settings.MEDIA_ROOT, 'peoples.json')
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    
    message = ""
    
    # 2. Загрузка данных из JSON
    patients_data = []
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                patients_data = json.load(f)
        except:
            patients_data = []
    
    # 3. Загрузка данных из БД
    db_patients = Patient.objects.all()
    
    # 4. Обработка СОХРАНЕНИЯ с ПРОВЕРКОЙ ДУБЛИКАТОВ
    if request.method == 'POST':
        if 'name' in request.POST:
            name = request.POST.get('name', '').strip()
            height = request.POST.get('height', '').strip()
            pressure = request.POST.get('pressure', '').strip()
            glucose = request.POST.get('glucose', '').strip()
            age = request.POST.get('age', '').strip()
            save_to = request.POST.get('save_to', 'json')
            
            if name and height and pressure and glucose and age:
                if save_to == 'json':
                    # ПРОВЕРКА ДУБЛИКАТОВ В JSON
                    is_duplicate = False
                    for patient in patients_data:
                        if (patient['name'] == name and 
                            patient['height'] == height and 
                            patient['pressure'] == pressure and 
                            patient['glucose'] == glucose and 
                            patient['age'] == age):
                            is_duplicate = True
                            break
                    
                    if not is_duplicate:
                        new_patient = {
                            'name': name,
                            'height': height,
                            'pressure': pressure,
                            'glucose': glucose,
                            'age': age
                        }
                        patients_data.append(new_patient)
                        
                        with open(data_file, 'w', encoding='utf-8') as f:
                            json.dump(patients_data, f, ensure_ascii=False, indent=2)
                        
                        message = "✅ Данные сохранены в JSON файл"
                    else:
                        message = "❌ Такая запись уже есть в JSON файле"
                
                else:
                    # Сохраняем в БД (проверка дубликатов через IntegrityError)
                    try:
                        patient = Patient(
                            name=name,
                            height=height,
                            pressure=pressure,
                            glucose=glucose,
                            age=age
                        )
                        patient.save()
                        message = "✅ Данные сохранены в базу данных"
                    except IntegrityError:
                        message = "❌ Такая запись уже есть в базе данных"
            
            else:
                message = "❌ Заполните все поля"
        
        # Загрузка файла
        elif 'json_file' in request.FILES:
            uploaded_file = request.FILES['json_file']
            if uploaded_file.name.endswith('.json'):
                try:
                    file_content = uploaded_file.read().decode('utf-8')
                    new_patients = json.loads(file_content)
                    
                    if isinstance(new_patients, list):
                        patients_data.extend(new_patients)
                        with open(data_file, 'w', encoding='utf-8') as f:
                            json.dump(patients_data, f, ensure_ascii=False, indent=2)
                        message = "✅ Файл загружен в JSON"
                except:
                    message = "❌ Ошибка в файле"
    
    # 5. Обработка УДАЛЕНИЯ (только для БД)
    if 'delete_id' in request.GET:
        try:
            patient_id = request.GET.get('delete_id')
            patient = Patient.objects.get(id=patient_id)
            patient.delete()
            message = "✅ Пациент удален из базы данных"
        except:
            message = "❌ Ошибка при удалении"
    
    # 6. Выбор данных для показа
    data_source = request.GET.get('source', 'json')
    
    if data_source == 'db':
        # Данные из БД
        patients_to_show = []
        for patient in db_patients:
            patients_to_show.append({
                'id': patient.id,
                'name': patient.name,
                'height': patient.height,
                'pressure': patient.pressure,
                'glucose': float(patient.glucose),
                'age': patient.age,
                'from_db': True
            })
    else:
        # Данные из JSON
        patients_to_show = patients_data
        for patient in patients_to_show:
            patient['from_db'] = False
    
    return render(request, 'home.html', {
        'message': message,
        'patients': patients_to_show,
        'data_source': data_source
    })

# 7. AJAX поиск (только по БД)
def search_patients(request):
    query = request.GET.get('q', '')
    if query:
        # Ищем по имени в БД
        patients = Patient.objects.filter(name__icontains=query)
        results = []
        for patient in patients:
            results.append({
                'id': patient.id,
                'name': patient.name,
                'height': patient.height,
                'pressure': patient.pressure,
                'glucose': float(patient.glucose),
                'age': patient.age
            })
        return JsonResponse({'patients': results})
    return JsonResponse({'patients': []})

# 8. Удаление пациента (AJAX - только для БД)
def delete_patient(request, patient_id):
    if request.method == 'POST':
        try:
            patient = get_object_or_404(Patient, id=patient_id)
            patient.delete()
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False})

# 9. Редактирование пациента (только для БД)
def update_patient(request, patient_id):
    if request.method == 'POST':
        try:
            patient = get_object_or_404(Patient, id=patient_id)
            patient.name = request.POST.get('name')
            patient.height = request.POST.get('height')
            patient.pressure = request.POST.get('pressure')
            patient.glucose = request.POST.get('glucose')
            patient.age = request.POST.get('age')
            patient.save()
            return JsonResponse({'success': True})
        except:
            return JsonResponse({'success': False})