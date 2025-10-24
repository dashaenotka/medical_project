from django.shortcuts import render
import json
import os
from django.conf import settings

def home(request):
    data_file = os.path.join(settings.MEDIA_ROOT, 'peoples.json')
    
    message = ""
    
    # Загрузка существующих данных
    patients_data = []
    if os.path.exists(data_file) and os.path.getsize(data_file) > 0:
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                patients_data = json.load(f)
        except json.JSONDecodeError:
            patients_data = []
    
    # Обработка POST запросов
    if request.method == 'POST':
        # 1. Сохранение через форму
        if 'name' in request.POST:
            name = request.POST.get('name', '').strip()
            height = request.POST.get('height', '').strip()
            pressure = request.POST.get('pressure', '').strip()
            glucose = request.POST.get('glucose', '').strip()
            age = request.POST.get('age', '').strip()
            
            if name and height and pressure and glucose and age:
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
                
                message = "✅ Данные сохранены"
            else:
                message = "❌ Заполните все поля"
        
        # 2. Загрузка файла
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
                        
                        message = "✅ Файл загружен"
                    else:
                        message = "❌ Файл должен содержать список"
                        
                except json.JSONDecodeError:
                    message = "❌ Ошибка в формате JSON"
            else:
                message = "❌ Можно загружать только JSON файлы"
    
    return render(request, 'home.html', {
        'message': message,
        'patients': patients_data
    })