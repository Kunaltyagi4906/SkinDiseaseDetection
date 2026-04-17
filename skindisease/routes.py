from flask import render_template, request, redirect, url_for, flash
from skindisease import app
from skindisease.models import User
from skindisease.forms import RegisterForm, LoginForm
from skindisease import db
from flask_login import login_user, logout_user, login_required
import os
import base64
import random
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.efficientnet import preprocess_input
from werkzeug.utils import secure_filename
from sqlalchemy import or_
from werkzeug.exceptions import RequestEntityTooLarge

# Allowed extensions for file upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

# Model and Labels
model_path = os.path.join('model', 'my_model.keras')
model = None
labels = [
    'BA-cellulitis',
    'BA-impetigo',
    'FU-athlete-foot',
    'FU-nail-fungus',
    'FU-ringworm',
    'PA-cutaneous-larva-migrans',
    'VI-chickenpox',
    'VI-shingles'
]

# Disease Information
disease_info = {
    'BA-cellulitis': {
        'treatment': 'Antibiotics (oral or intravenous) to treat the infection',
        'cure': 'Complete recovery usually takes a few weeks with proper medication.'
    },
    'BA-impetigo': {
        'treatment': 'Topical or oral antibiotics are used for impetigo.',
        'cure': 'Good hygiene and completing the antibiotic course can cure impetigo.'
    },
    'FU-athlete-foot': {
        'treatment': 'Antifungal creams and powders are common treatments.',
        'cure': 'Keep feet dry and clean to prevent recurrence.'
    },
    'FU-nail-fungus': {
        'treatment': 'Antifungal medications, either topical or oral.',
        'cure': 'Treatment may take weeks to months depending on severity.'
    },
    'FU-ringworm': {
        'treatment': 'Antifungal creams or oral antifungals for severe cases.',
        'cure': 'Avoid contact with infected areas to prevent spreading.'
    },
    'PA-cutaneous-larva-migrans': {
        'treatment': 'Antiparasitic medications like albendazole or ivermectin.',
        'cure': 'Most cases resolve with proper medication within days.'
    },
    'VI-chickenpox': {
        'treatment': 'Calamine lotion and antiviral drugs in severe cases.',
        'cure': 'Vaccination is key to prevention; most recover in 1-2 weeks.'
    },
    'VI-shingles': {
        'treatment': 'Antiviral drugs, pain relievers, and soothing lotions.',
        'cure': 'Vaccination helps reduce severity; symptoms typically subside in weeks.'
    }
}

# Upload folder for images
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def get_model():
    global model
    if model is None:
        model = load_model(model_path)
    return model


def predict_image(img):
    loaded_model = get_model()
    img = cv2.resize(img, (224, 224))
    img = preprocess_input(np.array([img]))
    prediction = loaded_model.predict(img)
    predicted_class = labels[np.argmax(prediction)]
    disease_details = disease_info.get(
        predicted_class,
        {"treatment": "General treatment advice.", "cure": "General cure information."}
    )
    return predicted_class, disease_details

@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/image', methods=['GET', 'POST'])
@login_required
def predict():
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Load image for prediction
                img = cv2.imread(filepath)
                if img is None:
                    flash("Could not read the uploaded image. Please try another file.", category="danger")
                    return redirect(url_for("predict"))

                predicted_class, disease_details = predict_image(img)

                return render_template('result.html', image_url=url_for('static', filename=f'uploads/{filename}'),
                                       prediction=predicted_class, details=disease_details)

        # Check if the form is for capturing an image from the webcam
        elif 'captured_image' in request.form:
            captured_image = request.form['captured_image']
            if not captured_image or ',' not in captured_image:
                flash("No webcam image was captured. Please start the webcam and capture again.", category="danger")
                return redirect(url_for("predict"))

            # Process captured image (base64 data)
            img_data = captured_image.split(',', 1)[1]  # Remove the "data:image/png;base64," part
            if not img_data.strip():
                flash("No webcam image was captured. Please start the webcam and capture again.", category="danger")
                return redirect(url_for("predict"))

            try:
                img_bytes = base64.b64decode(img_data)
            except Exception:
                flash("Captured webcam image was invalid. Please try again.", category="danger")
                return redirect(url_for("predict"))

            if not img_bytes:
                flash("Captured webcam image was empty. Please try again.", category="danger")
                return redirect(url_for("predict"))

            np_arr = np.frombuffer(img_bytes, np.uint8)
            if np_arr.size == 0:
                flash("Captured webcam image was empty. Please try again.", category="danger")
                return redirect(url_for("predict"))

            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            if img is None:
                flash("Captured webcam image could not be processed. Please try again.", category="danger")
                return redirect(url_for("predict"))

            predicted_class, disease_details = predict_image(img)

            return render_template('result.html', prediction=predicted_class, details=disease_details)

    return render_template('image.html')



@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data.strip(),
                              email_address=form.email_address.data.strip().lower(),
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are now logged in as {user_to_create.username}", category='success')
        return redirect(url_for('predict'))
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category='danger')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        login_value = form.username.data.strip()
        attempted_user = User.query.filter(
            or_(
                User.username == login_value,
                User.email_address == login_value.lower()
            )
        ).first()
        if attempted_user and attempted_user.check_password_correction(
                attempted_password=form.password.data
        ):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('predict'))
        else:
            flash('Username and password do not match! Please try again', category='danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))


@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(error):
    flash("Uploaded image is too large. Please choose an image smaller than 16 MB.", category="danger")
    return redirect(url_for("predict"))


