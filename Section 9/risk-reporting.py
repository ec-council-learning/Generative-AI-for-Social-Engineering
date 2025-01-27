"""
Program: Cybersecurity Training and Gap Analysis Application
Description: This application allows organizations to analyze cybersecurity training needs and identify security gaps among employees.

The program processes employee data from three uploaded Excel files:
1. Incident History
2. Mock Tests
3. User Behavior

Outputs: Generates two reports:
   - Employee-specific training needs in Excel format.
   - Organizational security loopholes in Excel format.
"""

import os
import pandas as pd
import streamlit as st
import openai
import json

# Set OpenAI API Key (ensure not to hard-code in production)
openai.api_key = "<my-openai-API-key"

# ---------------------------------------------------------------------
# Function to interact with OpenAI for training needs
def get_training_needs(employee_data):
    prompt = f"""
For the following employee data, provide their training needs in the json format:
- "Employee_ID": {employee_data['Employee_ID']}
- "Training Needs": A string contains detailed and structured sentence that describe of training recommendations. If no training is needed, state "No specific training needs identified." without any reasoning.

Employee Data:
- Login Attempts: {employee_data['Login_Attempts']}
- Suspicious Access Flags: {employee_data['Suspicious_Access_Flags']}
- Severity: {employee_data['Severity']}
- Resolution Time Days: {employee_data['Resolution_Time_Days']}
- Score Percentage: {employee_data['Score_Percentage']}
- Device Sharing Instances: {employee_data['Device_Sharing_Instances']}

Guidelines:
1. If Login Attempts > 5 or Suspicious Access Flags > 0, recommend training on secure login and unauthorized access prevention.
2. If Severity >= 3 or Resolution Time > 7 days, recommend training on incident reporting and faster resolution strategies.
3. If Score Percentage < 60, recommend refresher training on phishing awareness and secure login practices.
4. If Device Sharing Instances > 2, recommend training on secure device management and data protection.
"""
    response = openai.chat.completions.create(
        model="gpt-4o",  # Specify the model you're using
        messages=[
            {"role": "system", "content": "You are an expert in cybersecurity training needs assessment."},
            {"role": "user", "content": prompt}
        ]
    )
    # print(response['choices'][0]['message']['content'] )
    return response.choices[0].message.content  # Adjust this for the correct response format

# Function to interact with OpenAI for security gaps and controls
def get_security_gaps(employee_data):
    prompt = f"""
Based on the following employee data, identify security gaps, controls needed, criticality, and specific steps in a structured json format:
Employee Data:
- Login Attempts: {employee_data['Login_Attempts']}
- Suspicious Access Flags: {employee_data['Suspicious_Access_Flags']}
- Severity: {employee_data['Severity']}
- Resolution Time Days: {employee_data['Resolution_Time_Days']}
- Score Percentage: {employee_data['Score_Percentage']}
- Device Sharing Instances: {employee_data['Device_Sharing_Instances']}

Guidelines:
1. If Login Attempts > 5 or Suspicious Access Flags > 0, identify gaps like potential unauthorized access risks. Suggest controls like stronger authentication policies and monitoring.
2. If Severity >= 3 or Resolution Time > 7 days, identify gaps in incident management. Suggest faster resolution processes and training.
3. If Score Percentage < 60, highlight low security awareness. Suggest training and phishing simulations.
4. If Device Sharing Instances > 2, flag policy violations. Suggest stricter device management policies.


Return the result in this structured json format:
- "Security Gaps": A String Description of gaps. If No significant security gaps identified based on employee data, state "No significant security gaps identified based on employee data".
- "Controls Needed": A String that describe Specific controls for addressing the gaps. If No significant security gaps identified based on employee data, state "None".
- "Criticality": Levels (L, M, H). If No significant security gaps identified based on employee data, state "L".
- "Steps Needed": A string that describe Detailed actions to resolve the gaps. If No significant security gaps identified based on employee data, state "None".
"""
    response = openai.chat.completions.create(
        model="gpt-4o",  # Specify the model you're using
        messages=[
            {"role": "system", "content": "You are an expert in organizational security gap analysis."},
            {"role": "user", "content": prompt}
        ]
    )
    # print(response['choices'][0]['message']['content'] )
    return response.choices[0].message.content  # Adjust this for the correct response format

# ---------------------------------------------------------------------
# Streamlit App
st.title("Cybersecurity Training and Gap Analysis")

if "employee_training_file" not in st.session_state:
    st.session_state.employee_training_file = None
if "org_security_file" not in st.session_state:
    st.session_state.org_security_file = None

# File uploads
st.sidebar.header("Upload Data")
incident_history_file = st.sidebar.file_uploader("Upload Incident History (Excel)", type=["xlsx"])
mock_tests_file = st.sidebar.file_uploader("Upload Mock Tests (Excel)", type=["xlsx"])
user_behavior_file = st.sidebar.file_uploader("Upload User Behavior (Excel)", type=["xlsx"])

if st.sidebar.button("Process and Generate Reports"):
    st.session_state.org_security_file = None
    st.session_state.employee_training_file = None
    if incident_history_file and mock_tests_file and user_behavior_file:
        # Load datasets
        incident_history = pd.read_excel(incident_history_file)
        mock_tests = pd.read_excel(mock_tests_file)
        user_behavior = pd.read_excel(user_behavior_file)

        # Merge datasets
        merged_data = pd.merge(user_behavior, mock_tests, on="Employee_ID", how="outer")
        merged_data = pd.merge(merged_data, incident_history, on="Employee_ID", how="outer")

        # Ensure numeric data is correctly cast
        numeric_columns = [
            "Severity", 
            "Resolution_Time_Days", 
            "Score_Percentage", 
            "Login_Attempts", 
            "Suspicious_Access_Flags", 
            "Device_Sharing_Instances"
        ]
        for column in numeric_columns:
            merged_data[column] = pd.to_numeric(merged_data[column], errors="coerce")

        # Lists to store results
        employee_training_results = []
        org_security_results = []

        # Process each Merged record
        for _, row in merged_data.iterrows():
            employee_data = row.to_dict()

            # Get training needs
            training_needs = get_training_needs(employee_data)
            training_needs = training_needs.replace("```", '')
            training_needs = training_needs.replace("json", '')
            print(training_needs)
            employee_training_results.append(json.loads(training_needs))

            # Get security gaps and controls
            security_gaps = get_security_gaps(employee_data)
            security_gaps = security_gaps.replace("```","")
            security_gaps = security_gaps.replace("json", "")
            print(security_gaps)
            org_security_results.append(json.loads(security_gaps))

        # Convert results to DataFrames
        employee_training_df = pd.DataFrame(employee_training_results)
        org_security_df = pd.DataFrame(org_security_results)

        # Ensure the 'reports' directory exists
        if not os.path.exists("reports"):
            os.makedirs("reports")

        # Save reports in 'reports' directory
        st.session_state.employee_training_file = os.path.join("reports", "employee_specific_training_needs.xlsx")
        st.session_state.org_security_file = os.path.join("reports", "organizational_security_loopholes.xlsx")
        with pd.ExcelWriter(st.session_state.employee_training_file) as writer:
            employee_training_df.to_excel(writer, sheet_name="Training Needs", index=False)

        with pd.ExcelWriter(st.session_state.org_security_file) as writer:
            org_security_df.to_excel(writer, sheet_name="Security Gaps & Controls", index=False)

        st.success("Reports generated successfully!")
        
    else:
        st.error("Please upload all required files.")

# Display download buttons if files are generated
if st.session_state.employee_training_file and st.session_state.org_security_file:
    with open(st.session_state.employee_training_file, "rb") as f:
        st.download_button(
            label="Download Employee Training Needs",
            data=f,
            file_name="employee_specific_training_needs.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with open(st.session_state.org_security_file, "rb") as f:
        st.download_button(
            label="Download Security Gaps Report",
            data=f,
            file_name="organizational_security_loopholes.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )