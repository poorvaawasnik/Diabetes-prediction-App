# 🩺 DiabetesCare AI

A web-based intelligent system for **diabetes prediction and health monitoring** using Machine Learning.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------

## 🚀 Features

- 🔍 Diabetes Prediction using ML Model
- 📊 Risk Score Calculation
- 🩸 Blood Sugar Tracker with Graph
- 💙 Health Score Calculator
- 🤖 AI Health Assistant (Chatbot)
- 🍽 AI Diet Recommendation
- 🏥 Nearby Healthcare Services (Google Maps)
- 📈 Prediction History Tracking
- 👤 User Profile Management

---

## 🧠 Machine Learning

- Model trained using **Scikit-learn**
- Input features:
  - Pregnancies
  - Glucose
  - Blood Pressure
  - Skin Thickness
  - Insulin
  - BMI
  - Diabetes Pedigree Function
  - Age
  - Family History
  - Physical Activity

- Output:
  - Prediction → Diabetic / Non-Diabetic
  - Risk Score (%)

---

## 🏗 System Architecture

User → Frontend → Backend → ML Model → Result → Database → User

---

## 🛠 Tech Stack

### 🔹 Frontend
- HTML
- CSS
- JavaScript
- Bootstrap

### 🔹 Backend
- Python
- Flask

### 🔹 Database
- SQLite

### 🔹 Machine Learning
- Scikit-learn
- NumPy
- Pandas

### 🔹 AI Integration
- Groq API (LLM-based chatbot & diet plan)

---

## 📂 Project Structure
DiabetesCare-AI/
│
├── app.py
├── predict.py
├── model/
│ ├── diabetes_model.pkl
│ ├── scaler.pkl
│
├── templates/
│ ├── index.html
│ ├── login.html
│ ├── register.html
│ ├── dashboard.html
│ ├── profile.html
│ ├── history.html
│ ├── sugar_tracker.html
│ ├── health_score.html
│ ├── chat.html
│ ├── ai_diet.html
│ ├── nearby_services.html
│
├── static/
│ ├── css/
│ ├── js/
│ ├── profile_pics/
│
└── diabetes.db


---

## ⚙️ Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/your-username/diabetescare-ai.git
cd diabetescare-ai
2. Install Dependencies
pip install flask numpy pandas scikit-learn werkzeug groq
3. Run Application
python app.py
4. Open in Browser
http://127.0.0.1:5000
🔐 Authentication
User Registration & Login
Password hashing using Werkzeug
Session-based authentication
📊 Modules
Prediction Module
Health Score Module
Sugar Tracker Module
AI Chatbot Module
Diet Recommendation Module
Nearby Services Module
History & Profile Module
🎯 Advantages
Early diabetes detection
User-friendly interface
Real-time monitoring
Centralized data storage
AI-powered recommendations
📌 Future Enhancements
Mobile app integration
Real-time wearable device data
Advanced deep learning models
Doctor dashboard
Cloud deployment
👨‍💻 Author
Your Name
📜 License


