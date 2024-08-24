import datetime
import pandas as pd
import streamlit as st
import boto3
from io import StringIO

# Define the S3 key (file path in the bucket) for the CSV file.
S3_FILE_KEY = "head_of_state_data.csv"

# Load AWS credentials from Streamlit secrets
aws_access_key_id = st.secrets["aws"]["aws_access_key_id"]
aws_secret_access_key = st.secrets["aws"]["aws_secret_access_key"]
aws_region = st.secrets["aws"].get("aws_default_region", "us-east-1")
bucket_name = st.secrets["aws"]["s3_bucket_name"]

# Initialize the S3 client
s3 = boto3.client(
    's3',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region
)

# Function to load data from the S3 bucket.
def load_data():
    try:
        # Fetch the file from S3
        response = s3.get_object(Bucket=bucket_name, Key=S3_FILE_KEY)
        # Read the CSV content
        csv_content = response['Body'].read().decode('utf-8')
        return pd.read_csv(StringIO(csv_content))
    except s3.exceptions.NoSuchKey:
        # If the file doesn't exist in S3, return an empty DataFrame with the correct columns.
        return pd.DataFrame(columns=["Name", "Start Date", "End Date", "GDP Start", "GDP End", "GDP Growth"])

# Function to save data to the S3 bucket.
def save_data(df):
    # Convert the DataFrame to CSV format in memory
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    # Save the CSV to S3
    s3.put_object(Bucket=bucket_name, Key=S3_FILE_KEY, Body=csv_buffer.getvalue())

# Initialize the session state dataframe from the S3 bucket.
if "df" not in st.session_state:
    st.session_state.df = load_data()

# Show app title and description.
st.set_page_config(page_title="Head of State Rankings", page_icon="🏛️")
st.title("🏛️ Head of State Rankings")
st.write(
    """
    This app allows you to rank heads of state based on their tenure and GDP performance.
    You can view the rankings or add a new head of state.
    """
)

# Show the main table with the rankings.
st.header("Head of State Rankings")
st.write(f"Number of records: `{len(st.session_state.df)}`")

# Display the dataframe as a nice looking table.
st.dataframe(st.session_state.df.sort_values(by="GDP Growth", ascending=False), use_container_width=True, hide_index=True)

# Expander to show/hide the form for adding a new head of state.
with st.expander("Add a New Head of State", expanded=False):
    with st.form("add_head_of_state_form"):
        name = st.text_input("Name of Head of State")
        start_date = st.date_input("Start Date", value=None)
        end_date = st.date_input("End Date", value=None)
        gdp_start = st.number_input("GDP at Start (in billions)", min_value=0.0, format="%.2f", value=None)
        gdp_end = st.number_input("GDP at End (in billions)", min_value=0.0, format="%.2f", value=None)
        submitted = st.form_submit_button("Submit")

        # Guard for illogical date inputs
        if(start_date != None and end_date != None and end_date < start_date):
            st.warning("False Input: Start Date is bigger than End Date")
            st.stop()

        # Guard if form not completely filled out
        elif(submitted and None in (start_date, end_date, gdp_start, gdp_end)):
            st.warning("Form not filled out completely")
            st.stop()
    
    if submitted:
        # Calculate GDP Growth
        gdp_growth = gdp_end - gdp_start

        # Guard if input already exists in dataframe
        if(not(st.session_state.df[(st.session_state.df["Name"] == name) & (st.session_state.df["GDP Growth"] == gdp_growth)].empty)):
            st.warning("Input already in Rankings")
            st.stop()

        # Create a dataframe for the new head of state and append it to the session state dataframe.
        df_new = pd.DataFrame(
            [
                {
                    "Name": name,
                    "Start Date": start_date,
                    "End Date": end_date,
                    "GDP Start": gdp_start,
                    "GDP End": gdp_end,
                    "GDP Growth": gdp_growth,
                }
            ]
        )

        # Show a success message.
        st.write("Head of State added! Here are the details:")
        st.dataframe(df_new, use_container_width=True, hide_index=True)

        # Update the session state dataframe and save it to S3.
        st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)
        save_data(st.session_state.df)

# Expander to show/hide the form for removing a head of state.
with st.expander("Remove a Head of State", expanded=False):
    with st.form("remove_head_of_state_form"):
        name = st.text_input("Name of Head of State")
        gdp_growth = st.number_input("GDP Growth", value = None)
        removed = st.form_submit_button("Remove")

    if removed:
        # Guard if head of state is in table
        if(len(st.session_state.df.loc[st.session_state.df["Name"] == name]) == 0):
            st.warning("Head of State not found")
            st.stop()

        # Guard if two head of state have the same name
        elif(len(st.session_state.df.loc[st.session_state.df["Name"] == name]) > 1):
            # Guard if start date not specified
            if(gdp_growth == None):
                st.warning("Multiple Heads of State found. Please input the GDP Growth")
                st.stop()

            # Find index with both name and start date
            index = st.session_state.df[(st.session_state.df["Name"] == name) & (st.session_state.df["GDP Growth"] == gdp_growth)].index
        
        else:
            # Find index with only name
            index = st.session_state.df[st.session_state.df["Name"] == name].index

        # Show a success message.
        st.write("Head of State removed! Here are the details:")
        st.dataframe(st.session_state.df.iloc[index], use_container_width=True, hide_index=True)

        # Remove head of state
        st.session_state.df = st.session_state.df.drop(index)
        save_data(st.session_state.df)