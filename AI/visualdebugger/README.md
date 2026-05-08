# 🧠 CNN Based AI Visual Debugging Agent for Web UI Testing

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-orange.svg)](https://tensorflow.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue.svg)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

> An intelligent, automated visual bug detection system powered by Convolutional Neural Networks (CNN) and computer vision. It captures screenshots of web interfaces, analyzes them through a fine-tuned MobileNetV2 model, generates GradCAM heatmaps, and stores all findings in a structured SQLite database with a rich web dashboard.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔬 **CNN Inference** | MobileNetV2 (transfer learning) classifies 6 types of visual bugs |
| 📸 **Screenshot Capture** | Selenium/headless Chrome captures full-page screenshots |
| 🌡️ **GradCAM Heatmaps** | Gradient-based attention maps highlight anomalous regions |
| 📊 **Rich Dashboard** | Charts, stat cards, session history, alert feed |
| 📄 **PDF Reports** | ReportLab generates downloadable bug reports |
| 🔐 **Auth System** | Session-based login/signup with Werkzeug password hashing |
| 🗄️ **SQLite** | Lightweight embedded DB — no external server needed |
| 📈 **Model Metrics** | Epoch-level accuracy/loss tracking with interactive charts |

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/your-username/cnn-visual-debugger.git
cd cnn-visual-debugger
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
copy .env.example .env
# Edit .env if needed
```

### 3. Run the App
```bash
python run.py
```
The app starts at **http://localhost:5000**

### 4. Seed Demo Data (optional)
```bash
flask seed-db
```

---

## 👤 Demo Credentials

| Role  | Email                   | Password     |
|-------|-------------------------|--------------|
| Admin | admin@debugger.ai       | Admin@123    |
| User  | dhanush@debugger.ai     | Dhanush@123  |
| Guest | guest@debugger.ai       | Guest@123    |

---

## 🧠 ML Pipeline

### Training the Model
```bash
# 1. Generate synthetic dataset
python -m app.ml.dataset_gen --n 300 --out ml_experiments/data/raw

# 2. Train the CNN
python app/ml/train.py --data ml_experiments/data/processed --epochs 30

# 3. Evaluate
python app/ml/evaluate.py --model app/static/models/ui_bug_detector.keras
```

### Bug Categories
| Category | WCAG Issue | Severity |
|----------|------------|----------|
| `layout` | Mispositioned elements | High |
| `color` | Color contrast ratio < 4.5:1 | Medium |
| `overlap` | Overlapping UI elements | High |
| `missing` | Element not rendered | Critical |
| `alignment` | Grid baseline mismatch | Low |
| `contrast` | Insufficient visual distinction | Medium |

---

## 🗂️ Project Structure

```
cnn-visual-debugger/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models/              # User, BugReport, TestSession
│   ├── routes/              # auth, dashboard, analyzer, reports, sessions, settings, pages
│   ├── ml/                  # model, preprocess, train, dataset_gen, evaluate
│   ├── services/            # bug_detector, screenshot, report_generator
│   ├── database/            # db.py, schema.sql, seed.py
│   ├── static/              # css/, js/, uploads/, heatmaps/, models/
│   └── templates/           # base.html + all page templates
├── ml_experiments/          # Jupyter notebooks, training data
├── tests/                   # pytest test suite
├── instance/debugger.db     # SQLite DB (auto-created)
├── config.py
├── run.py
└── requirements.txt
```

---

## 🌐 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| GET/POST | `/auth/login` | User login |
| GET/POST | `/auth/signup` | Create account |
| GET | `/auth/logout` | Log out |
| GET | `/dashboard` | Main dashboard |
| GET | `/dashboard/overview` | Stats overview |
| GET | `/dashboard/model-metrics` | CNN metrics |
| GET/POST | `/analyzer/` | Run new analysis |
| GET | `/analyzer/progress/<id>` | Progress page |
| GET | `/analyzer/api/progress/<id>` | Progress JSON API |
| GET | `/analyzer/result/<id>` | Analysis results |
| GET | `/sessions/` | All test sessions |
| GET | `/sessions/<id>` | Session detail |
| GET | `/reports/` | All bug reports |
| GET | `/reports/<id>` | Report detail |
| GET | `/reports/export/pdf/<id>` | Download PDF |
| GET/POST | `/settings/` | Account settings |
| GET | `/about` | About page |
| GET/POST | `/contact` | Contact form |

---

## 🧪 Running Tests

```bash
pytest tests/ -v --tb=short
pytest tests/ --cov=app --cov-report=html
```

---

## ⚙️ Configuration

Edit `config.py` or set environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | auto | Flask session key |
| `FLASK_ENV` | development | Environment |
| `MODEL_PATH` | `app/static/models/ui_bug_detector.keras` | CNN model path |
| `CONFIDENCE_THRESHOLD` | 0.5 | Min prediction confidence |

---

## 📦 Tech Stack

- **Backend**: Flask 3.0, Python 3.10+
- **ML**: TensorFlow 2.16, Keras, MobileNetV2, OpenCV, Pillow
- **Database**: SQLite3
- **Screenshot**: Selenium + ChromeDriver
- **PDF**: ReportLab
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript, Chart.js
- **Auth**: Werkzeug, Flask sessions

---

## 📝 License

MIT License © 2026 CNN Visual Debugger
