import pickle
import numpy as np
import os

# ==============================
# PATH SETUP (SAFE & RELATIVE)
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "model", "diabetes_model.pkl")
SCALER_PATH = os.path.join(BASE_DIR, "model", "scaler.pkl")

# ==============================
# LOAD MODEL & SCALER
# ==============================

try:
    model = pickle.load(open(MODEL_PATH, "rb"))
    scaler = pickle.load(open(SCALER_PATH, "rb"))
    print("✅ Model & Scaler Loaded Successfully")
    print("📊 Model expects features:", scaler.n_features_in_)
except Exception as e:
    print("❌ Error loading model:", e)
    raise

# ==============================
# PREDICTION FUNCTION
# ==============================

def predict_diabetes(input_data):
    """
    Expected input_data (10 features in this exact order):

    [
        Pregnancies,
        Glucose,
        BloodPressure,
        SkinThickness,
        Insulin,
        BMI,
        DiabetesPedigreeFunction,
        Age,
        FamilyHistory,
        PhysicalActivity
    ]
    """

    try:
        # Ensure correct number of features
        if len(input_data) != scaler.n_features_in_:
            raise ValueError(
                f"Expected {scaler.n_features_in_} features but got {len(input_data)}"
            )

        # Convert to numpy array
        input_array = np.array(input_data).reshape(1, -1)

        # Scale input
        scaled_input = scaler.transform(input_array)

        # Prediction
        prediction = model.predict(scaled_input)[0]

        # Probability
        probability = model.predict_proba(scaled_input)[0][1]

        if prediction == 1:
            result = "Diabetic"
        else:
            result = "Non-Diabetic"

        return result, probability

    except Exception as e:
        print("❌ Prediction Error:", e)
        return "Error", 0.0