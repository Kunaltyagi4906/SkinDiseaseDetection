# 🩺 Skin Disease Detection  

An AI-powered web application for detecting common skin diseases from images. Built with **Deep Learning (EfficientNet / CNN)** and **Flask**, this project allows users to upload an image of a skin condition and instantly receive predictions along with details about the disease and possible treatments.  

---

## 🚀 Features  
- Upload an image and get instant **disease prediction**  
- Detects **8 common skin diseases**:  
  - BA-cellulitis  
  - BA-impetigo  
  - FU-athlete-foot  
  - FU-nail-fungus  
  - FU-ringworm  
  - PA-cutaneous-larva-migrans  
  - VI-chickenpox  
  - VI-shingles  
- Displays disease name, **treatment**, and **cure options**  
- Simple and clean **Flask web app** interface  

---

## 📂 Project Structure  

SkinDiseaseDetection/
│── model/ # Pre-trained model files (EfficientNetB0)
│── skindisease/
│ ├── templates/ # HTML templates (home, result, login, register, etc.)
│ ├── static/uploads/ # Uploaded images
│ ├── routes.py # Flask routes
│ ├── models.py # Database models
│ ├── forms.py # Forms for login/register
│ ├── init.py # App initialization
│── instance/ # SQLite database
│── run.py # Entry point for Flask app
│── requirements.txt # Python dependencies

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/Kunaltyagi4906/SkinDiseaseDetection.git
cd SkinDiseaseDetection

2️⃣ Create a Virtual Environment
python -m venv venv
source venv/bin/activate   # On Mac/Linux
venv\Scripts\activate      # On Windows


3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run the Application
python run.py

🧠 Model Details

Architecture: EfficientNetB0 (transfer learning)

Dataset: Skin disease dataset with 8 classes

Training: Performed on Kaggle with early stopping & checkpoints

Saved model path: model/best_model_EfficientNetB0.keras
