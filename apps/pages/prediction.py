import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
def get_key_from_value_gender(value):
    data = {"Gender-Neutral": 0, "Female-only": 1}
    
    # Loop through the dictionary to find the key for the input value
    for key, val in data.items():
        if val == value:
            return key
    return "Invalid input"  # Return an error message if the value is not 0 or 1

def get_key_from_value_institute(value):
    data = {"IIT Bhubaneswar": 0, "IIT Bombay": 1, "IIT Mandi": 2, "IIT Delhi": 3, "IIT Kharagpur": 4, "IIT Indore": 5, "IIT Hyderabad": 6, "IIT Jodhpur": 7, "IIT Kanpur": 8, "IIT Madras": 9, "IIT Gandhinagar": 10, "IIT Patna": 11, "IIT Roorkee": 12, "Indian School of Mines Dhanbad": 13, "IIT Ropar": 14, "IIT (BHU) Varanasi": 15, "IIT Guwahati": 16, "IIT Bhilai": 17, "IIT Goa": 18, "IIT Palakkad": 19, "IIT Jammu": 20, "IIT Tirupati": 21, "IIT Dharwad": 22, "IIT (ISM) Dhanbad": 23}
    
    # Loop through the dictionary to find the key for the input value
    for key, val in data.items():
        if val == value:
            return key
    return "Invalid input"  # Return an error message if the value is not 0 or 1


# Custom CSS
st.markdown("""
    <style>
        .block-container {padding: 2rem;}
        .main > div {
            padding: 1.5rem;
            border-radius: 0.5rem;
            background-color: #ffffff;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
        }
        .stMetric {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    project_root = os.getcwd()
    pages_dir = os.path.join(project_root, 'apps', 'pages')
    
    institute_df = pd.read_csv(os.path.join(pages_dir, 'combined_institute_predictions.csv'))
    gender_df = pd.read_csv(os.path.join(pages_dir, 'combined_Gender_predictions.csv'))
    program_df = pd.read_csv(os.path.join(pages_dir, 'combined_Academic_Program_Name_predictions.csv'))
    
    # Convert Year to numeric and sort
    for df in [institute_df, gender_df, program_df]:
        df['Year'] = pd.to_numeric(df['Year'])
        df = df.sort_values('Year')
    
    return institute_df, gender_df, program_df

try:
    # Load data
    institute_df, gender_df, program_df = load_data()
    
    st.title("🎓 College Rank Analysis Dashboard")
    
    # Add year range filter
    years = sorted(institute_df['Year'].unique())
    min_year, max_year = min(years), max(years)
    
    selected_years = st.slider(
            "Select Year Range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year)
        )
    
    # Filter data based on selected years
    mask = (institute_df['Year'] >= selected_years[0]) & (institute_df['Year'] <= selected_years[1])
    filtered_institute_df = institute_df[mask]
    
    mask = (gender_df['Year'] >= selected_years[0]) & (gender_df['Year'] <= selected_years[1])
    filtered_gender_df = gender_df[mask]
    
    mask = (program_df['Year'] >= selected_years[0]) & (program_df['Year'] <= selected_years[1])
    filtered_program_df = program_df[mask]
    
    # Create three columns for charts
    col1, col2, col3 = st.columns(3)
    
    st.subheader("Institute-wise Rank Trends")
    fig1 = go.Figure()
        
        # Plot for each unique institute
    for institute in filtered_institute_df['Institute'].unique():
            inst_data = filtered_institute_df[filtered_institute_df['Institute'] == institute]
            fig1.add_trace(go.Scatter(
                x=inst_data['Year'],
                y=inst_data['min_opening_rank'],
                name=f'{get_key_from_value_institute(institute)} (Opening)',
                line=dict(width=2, dash='solid'),
                mode='lines+markers'
            ))
            fig1.add_trace(go.Scatter(
                x=inst_data['Year'],
                y=inst_data['max_closing_rank'],
                name=f'{get_key_from_value_institute(institute)} (Closing)',
                line=dict(width=2, dash='dot'),
                mode='lines+markers'
            ))
        
    fig1.update_layout(
            height=500,
            template='plotly_white',
            title="Opening vs Closing Ranks by Institute",
            xaxis_title="Year",
            yaxis_title="Rank",
            hovermode='x unified',
            yaxis=dict(autorange="reversed"),  # Reverse y-axis as lower rank is better
            showlegend=True
        )
    st.plotly_chart(fig1, use_container_width=True)
    
    st.subheader("Gender-wise Rank Distribution")
    fig2 = go.Figure()
        
    for gender in filtered_gender_df['Gender'].unique():
            gender_data = filtered_gender_df[filtered_gender_df['Gender'] == gender]
            fig2.add_trace(go.Scatter(
                x=gender_data['Year'],
                y=gender_data['min_opening_rank'],
                name=f'{get_key_from_value_gender(gender)} (Opening)',
                mode='lines+markers'
            ))
            fig2.add_trace(go.Scatter(
                x=gender_data['Year'],
                y=gender_data['max_closing_rank'],
                name=f'{get_key_from_value_gender(gender)} (Closing)',
                mode='lines+markers'
            ))
        
    fig2.update_layout(
            height=500,
            template='plotly_white',
            title="Opening vs Closing Ranks by Gender",
            xaxis_title="Year",
            yaxis_title="Rank",
            hovermode='x unified',
            yaxis=dict(autorange="reversed"),
            showlegend=True
        )
    st.plotly_chart(fig2, use_container_width=True)
    
    st.subheader("Program-wise Rank Analysis")
    fig3 = go.Figure()
        
    for program in filtered_program_df['Academic_Program_Name'].unique():
            program_data = filtered_program_df[filtered_program_df['Academic_Program_Name'] == program]
            fig3.add_trace(go.Scatter(
                x=program_data['Year'],
                y=program_data['min_opening_rank'],
                name=f'{program} (Opening)',
                mode='lines+markers'
            ))
            fig3.add_trace(go.Scatter(
                x=program_data['Year'],
                y=program_data['max_closing_rank'],
                name=f'{program} (Closing)',
                mode='lines+markers'
            ))
        
    fig3.update_layout(
            height=500,
            template='plotly_white',
            title="Opening vs Closing Ranks by Program",
            xaxis_title="Year",
            yaxis_title="Rank",
            hovermode='x unified',
            yaxis=dict(autorange="reversed"),
            showlegend=True
        )
    st.plotly_chart(fig3, use_container_width=True)
    
    # Summary Statistics
    st.markdown("---")
    st.subheader("📊 Summary Statistics")

    
    st.metric(
            "Average Opening Rank",
            f"{filtered_institute_df['min_opening_rank'].mean():.0f}",
            delta=f"Range: {filtered_institute_df['min_opening_rank'].max() - filtered_institute_df['min_opening_rank'].min():.0f}"
        )
    
    st.metric(
            "Average Closing Rank",
            f"{filtered_institute_df['max_closing_rank'].mean():.0f}",
            delta=f"Range: {filtered_institute_df['max_closing_rank'].max() - filtered_institute_df['max_closing_rank'].min():.0f}"
        )
    
    st.metric(
            "Number of Years",
            len(filtered_institute_df['Year'].unique())
        )
    
    # Data Tables
    st.markdown("---")
    st.subheader("Raw Data")
    
    tab1, tab2, tab3 = st.tabs(["Institute Data", "Gender Data", "Program Data"])
    
    with tab1:
        st.dataframe(filtered_institute_df)
    with tab2:
        st.dataframe(filtered_gender_df)
    with tab3:
        st.dataframe(filtered_program_df)

except Exception as e:
    st.error(f"Error: {str(e)}")
    st.info("Please check if all required CSV files are present in the correct location")
    
    # Debug information
    st.write("Current directory:", os.getcwd())
    st.write("Files in current directory:", os.listdir())



