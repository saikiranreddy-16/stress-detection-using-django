# 🧠 Stress Detection — Django Version

Converted from Flask to Django. All features preserved.

---

## 📁 Project Structure

```
stress_project/
├── manage.py
├── requirements.txt
├── model.h5                        ← Place your model.h5 HERE
├── static/
│   └── style.css
├── media/
│   └── uploads/                    ← Auto-created, stores analyzed images
├── stress_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── stress_app/
    ├── views.py                    ← All logic (converted from app.py)
    ├── urls.py
    ├── apps.py
    └── templates/stress_app/
        ├── index.html
        ├── result.html
        └── webcam.html
```

---

## ⚙️ Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Place model.h5
Copy your `model.h5` file into the `stress_project/` folder (same level as `manage.py`).

### 3. Run migrations
```bash
python manage.py migrate
```

### 4. Start the server
```bash
python manage.py runserver
```

### 5. Open browser
```
http://127.0.0.1:8000/
```

---

## 🔄 Flask → Django Changes Summary

| Flask                          | Django                              |
|-------------------------------|-------------------------------------|
| `app = Flask(__name__)`        | `settings.py` + `urls.py`          |
| `@app.route('/')`              | `path('', views.home)`              |
| `render_template('x.html')`    | `render(request, 'app/x.html')`     |
| `request.files['file']`        | `request.FILES['file']`             |
| `request.form['image']`        | `request.POST.get('image')`         |
| `url_for('static', ...)`       | `{% static 'file.css' %}`           |
| `/predict` (no CSRF)           | `{% csrf_token %}` required in forms|
| `url_for('predict')`           | `{% url 'predict' %}`               |
| `src="/{{ image }}"`           | `src="{{ image_url }}"` (media URL) |

---

## 🌐 URL Routes

| URL               | View             | Description              |
|------------------|-----------------|--------------------------|
| `/`               | `home`           | Upload page              |
| `/predict/`       | `predict`        | Image upload prediction  |
| `/webcam/`        | `webcam`         | Webcam capture page      |
| `/predict_webcam/`| `predict_webcam` | Webcam base64 prediction |
