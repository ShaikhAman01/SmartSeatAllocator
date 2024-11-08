import streamlit as st
import numpy as np
import joblib
import json
import os
from streamlit_echarts import st_echarts

# Paths for the data and model
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
model_path = os.path.join(BASE_DIR, 'random_forest_model.pkl')

# Check if the file exists before loading
if os.path.exists(model_path):
    model = joblib.load(model_path)
else:
    print("Model file not found:", model_path)

# Load mapping files
def load_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Load mappings
institute_mapping = load_json(os.path.join(BASE_DIR, 'data/maps/Institute_map.json'))
gender_mapping = load_json(os.path.join(BASE_DIR, 'data/maps/Gender_map.json'))
academic_program_mapping = load_json(os.path.join(BASE_DIR, 'data/maps/Academic_Program_Name.json'))
quota_mapping = load_json(os.path.join(BASE_DIR, 'data/maps/Quota_map.json'))
seat_mapping = load_json(os.path.join(BASE_DIR, 'data/maps/Seat_map.json'))

# Streamlit UI Setup
st.title("College Seat Allocation Predictor")
st.write("Enter your details to get your predicted college seat allocation!")

# Sidebar for user inputs
st.sidebar.header("Filters")

# Input selections
institute = st.sidebar.selectbox("Institute", list(institute_mapping.keys()))
gender = st.sidebar.radio("Gender", list(gender_mapping.keys()))
year = st.sidebar.slider("Year", min_value=2016, max_value=2028, value=2025)
program = st.sidebar.selectbox("Academic Program", list(academic_program_mapping.keys()))
quota = st.sidebar.radio("Quota", list(quota_mapping.keys()))
seat = st.sidebar.radio("Seat Type", list(seat_mapping.keys()))
disability = st.sidebar.radio("PWD (Disability)", ["Yes", "No"])

# Encode the selected inputs
institute_encoded = institute_mapping[institute]
gender_encoded = gender_mapping[gender]
program_encoded = academic_program_mapping[program]
quota_encoded = quota_mapping[quota]
seat_encoded = seat_mapping[seat]
disability_encoded = 1 if disability == "Yes" else 0

# Define input array for prediction
X_new = np.array([[institute_encoded, gender_encoded, year, program_encoded, seat_encoded, disability_encoded]])

if st.sidebar.button("Check"):
    # Make predictions for both Closing and Opening Rank for the selected year
    prediction = model.predict(X_new)
    closing_rank, opening_rank = prediction[0]  # Unpack both ranks from the prediction

    # Display the prediction result
    st.write(f"Predicted Closing Rank for your selection: {closing_rank:.2f}")
    st.write(f"Predicted Opening Rank for your selection: {opening_rank:.2f}")

    # Prepare data for the line chart for all years from 2016 to 2026
    years = list(range(2016, 2027))
    opening_ranks = []
    closing_ranks = []

    # Generate predictions for each year in the range
    for year in years:
        X_yearly = np.array([[institute_encoded, gender_encoded, year, program_encoded, seat_encoded, disability_encoded]])
        prediction = model.predict(X_yearly)
        closing_rank, opening_rank = prediction[0]
        closing_ranks.append(closing_rank)
        opening_ranks.append(opening_rank)

    # Define options for the line chart
    option = {
        "title": {"text": "Predicted Opening and Closing Ranks (2016-2026)"},
        "tooltip": {"trigger": "axis"},
        "legend": {"data": ["Opening Rank", "Closing Rank"]},
        "xAxis": {
            "type": "category",
            "data": [str(year) for year in years],  # X-axis labels as years
        },
        "yAxis": {"type": "value"},
        "series": [
            {
                "name": "Opening Rank",
                "data": opening_ranks,
                "type": "line",
                "smooth": True,
                "label": {"show": True, "position": "top"},
            },
            {
                "name": "Closing Rank",
                "data": closing_ranks,
                "type": "line",
                "smooth": True,
                "label": {"show": True, "position": "top"},
            },
        ],
    }

    vert_space = '<div style="padding: 180px 5px;"></div>'
    st.markdown(vert_space, unsafe_allow_html=True)

    # Display the line chart
    st_echarts(options=option, height="400px")
