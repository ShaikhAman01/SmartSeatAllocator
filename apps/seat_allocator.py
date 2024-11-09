import streamlit as st
import numpy as np
import joblib
import json
import os
from streamlit_echarts import st_echarts
from typing import Dict, Any


# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        height: 3rem;
        font-weight: bold;
    }
    .stSelectbox {
        margin-bottom: 1rem;
    }
    .prediction-card {
        padding: 1.5rem;
        border-radius: 10px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        
    }
    </style>
""", unsafe_allow_html=True)

# Cache data loading
@st.cache_data
def load_json(file_path: str) -> Dict[str, Any]:
    """Load and cache JSON data."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        st.error(f"Required mapping file not found: {file_path}")
        return {}
    except json.JSONDecodeError:
        st.error(f"Invalid JSON format in file: {file_path}")
        return {}

@st.cache_resource
def load_model(model_path: str):
    """Load and cache the prediction model."""
    try:
        return joblib.load(model_path)
    except FileNotFoundError:
        st.error("Model file not found. Please check the model path.")
        return None
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

class CollegeSeatPredictor:
    def __init__(self):
        self.BASE_DIR = os.path.dirname(os.path.dirname(__file__))
        self.load_resources()

    def load_resources(self):
        """Load all required resources."""
        # Load model
        model_path = os.path.join(self.BASE_DIR, 'random_forest_model.pkl')
        self.model = load_model(model_path)

        # Load mappings
        self.mappings = {
            'institute': load_json(os.path.join(self.BASE_DIR, 'data/maps/Institute_map.json')),
            'gender': load_json(os.path.join(self.BASE_DIR, 'data/maps/Gender_map.json')),
            'academic_program': load_json(os.path.join(self.BASE_DIR, 'data/maps/Academic_Program_Name.json')),
            'quota': load_json(os.path.join(self.BASE_DIR, 'data/maps/Quota_map.json')),
            'seat': load_json(os.path.join(self.BASE_DIR, 'data/maps/Seat_map.json'))
        }

    def create_ui(self):
        # Main content area
        st.title("College Seat Allocation Predictor")
        
        # Create two columns for the layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Input Parameters")
            with st.form("prediction_form"):
                institute = st.selectbox(
                    "Select Institute",
                    options=list(self.mappings['institute'].keys()),
                    help="Choose the institute you're interested in"
                )
                
                program = st.selectbox(
                    "Select Academic Program",
                    options=list(self.mappings['academic_program'].keys()),
                    help="Choose your preferred academic program"
                )
                
                gender = st.radio(
                    "Select Gender",
                    options=list(self.mappings['gender'].keys())
                )
                
                year = st.slider(
                    "Select Year",
                    min_value=2016,
                    max_value=2028,
                    value=2025,
                    help="Choose the year for prediction"
                )
                
                quota = st.radio(
                    "Select Quota",
                    options=list(self.mappings['quota'].keys())
                )
                
                seat = st.radio(
                    "Select Seat Type",
                    options=list(self.mappings['seat'].keys())
                )
                
                disability = st.radio(
                    "Person with Disability (PWD)",
                    options=["No", "Yes"]
                )
                
                submitted = st.form_submit_button("Predict Ranks")

            if submitted:
                self.make_prediction(
                    institute, gender, year, program,
                    quota, seat, disability, col2
                )

    def make_prediction(self, institute, gender, year, program, quota, seat, disability, output_col):
        with output_col:
            with st.spinner("Calculating predictions..."):
                # Encode inputs
                X_new = np.array([[
                    self.mappings['institute'][institute],
                    self.mappings['gender'][gender],
                    year,
                    self.mappings['academic_program'][program],
                    self.mappings['seat'][seat],
                    1 if disability == "Yes" else 0
                ]])

                # Make prediction
                prediction = self.model.predict(X_new)
                closing_rank, opening_rank = map(int, prediction[0])

                # Display current prediction
                st.markdown("### Prediction Results")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        label="Opening Rank",
                        value=f"{opening_rank:,}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        label="Closing Rank",
                        value=f"{closing_rank:,}",
                        delta=None
                    )

                # Generate historical predictions
                self.show_historical_trend(X_new)

    def show_historical_trend(self, X_base):
        """Display historical trend chart."""
        years = list(range(2016, 2027))
        predictions = []

        for year in years:
            X_yearly = X_base.copy()
            X_yearly[0, 2] = year  # Update year
            pred = self.model.predict(X_yearly)[0]
            predictions.append({"year": year, "closing": pred[0], "opening": pred[1]})

        # Configure chart
        option = {
            "title": {
                "text": "Historical Rank Trends",
                "subtext": "Predicted Opening and Closing Ranks",
                "left": "center"
            },
            "tooltip": {
                "trigger": "axis",
                "formatter": """
                    Year: {b}<br/>
                    Opening Rank: {c0}<br/>
                    Closing Rank: {c1}
                """
            },
            "legend": {
                "data": ["Opening Rank", "Closing Rank"],
                "top": "bottom"
            },
            "xAxis": {
                "type": "category",
                "data": [str(p["year"]) for p in predictions],
                "name": "Year",
                "nameLocation": "middle",
                "nameGap": 35
            },
            "yAxis": {
                "type": "value",
                "name": "Rank",
                "nameLocation": "middle",
                "nameGap": 50
            },
            "series": [
                {
                    "name": "Opening Rank",
                    "type": "line",
                    "data": [p["opening"] for p in predictions],
                    "smooth": True,
                    "label": {"show": True, "position": "top"},
                    "lineStyle": {"width": 4},
                    "itemStyle": {"color": "#ffbdaf"}  },
                {
                    "name": "Closing Rank",
                    "type": "line",
                    "data": [p["closing"] for p in predictions],
                    "smooth": True,
                    "label": {"show": True, "position": "top"},
                    "lineStyle": {"width": 4},
                   "itemStyle": {"color": "#81e7e9"}
                }
            ]
        }

        # Display chart
        st.markdown("### Historical Trend Analysis")
        st_echarts(
            options=option,
            height="400px",
            key="historical_chart"
        )

def main():
    predictor = CollegeSeatPredictor()
    predictor.create_ui()

if __name__ == "__main__":
    main()