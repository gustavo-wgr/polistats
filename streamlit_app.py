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
    # Fetch the file from S3
    response = s3.get_object(Bucket=bucket_name, Key=S3_FILE_KEY)
    # Read the CSV content
    csv_content = response['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(csv_content))

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
    This app allows you to rank heads of state based on economic indicators.
    
    """
)


# Function to apply conditional formatting based on the value
def color_text(val, positive_is_good=True):
    if positive_is_good:
        color = '#66CDAA' if val > 0 else '#FF9999'
    else:
        color = '#FF9999' if val > 0 else '#66CDAA'
    return f'color: {color}'

# Drop unnecessary columns before applying styling
df_display = st.session_state.df.drop(columns=["GDP Start", "GDP End"])

# Format the numerical columns to 2 decimal places
df_display = df_display.round(2)

# Apply the formatting to the relevant columns
styled_df = df_display.style.applymap(lambda x: color_text(x, positive_is_good=True), subset=["GDP Growth", "Population"])
styled_df = styled_df.applymap(lambda x: color_text(x, positive_is_good=False), subset=["Unemployment", "Inequality"])

# Format the numerical columns to show 2 decimal places in the display
styled_df = styled_df.format({"GDP Growth": "{:.2f}", "Unemployment": "{:.2f}", "Population": "{:.2f}", "Inequality": "{:.2f}"})

# Display the styled dataframe as a table.
st.dataframe(styled_df, use_container_width=True, hide_index=True)

# Expander to show/hide the form for adding a new head of state.
with st.expander("Add a New Head of State", expanded=False):
    with st.form("add_head_of_state_form"):
        name = st.text_input("Name of Head of State")
        start_date = st.date_input("Start Date", value=None)
        end_date = st.date_input("End Date", value=None)
        gdp_start = st.number_input("GDP at Start (in millions)", min_value=0.0, format="%.2f", value=None)
        gdp_end = st.number_input("GDP at End (in millions)", min_value=0.0, format="%.2f", value=None)
        unemployment = st.number_input("Unemployment Rate Change", min_value=0.0, max_value=100.0, format="%.2f",
                                       value=None)
        population = st.number_input("Population Change (in millions)", min_value=0.0, format="%.2f", value=None)
        inequality = st.number_input("Inequality Change (Share of the top 1%)", min_value=0.0, format="%.2f",
                                     value=None)
        submitted = st.form_submit_button("Submit")

        # Guard for illogical date inputs
        if start_date != None and end_date != None and end_date < start_date:
            st.warning("False Input: Start Date is bigger than End Date")
            st.stop()

        # Guard if form not completely filled out
        elif submitted and None in (start_date, end_date, gdp_start, gdp_end, unemployment, population, inequality):
            st.warning("Form not filled out completely")
            st.stop()

    if submitted:
        # Calculate GDP Growth
        gdp_growth = (gdp_end - gdp_start) / gdp_start

        # Guard if input already exists in dataframe
        if not st.session_state.df[
            (st.session_state.df["Name"] == name) & (st.session_state.df["GDP Growth"] == gdp_growth)].empty:
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
                    ## HAVE TO SAY UNEMPLOYMENT RATE DECREASE ETC
                    "Unemployment": unemployment,
                    "Population": population,
                    "Inequality": inequality,
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
        removed = st.form_submit_button("Remove")

    if removed:
        # Guard if head of state is in table
        if st.session_state.df.loc[st.session_state.df["Name"] == name].empty:
            st.warning("Head of State not found")
            st.stop()

        else:
            # Find index with only name
            index = st.session_state.df[st.session_state.df["Name"] == name].index

        # Show a success message.
        st.write("Head of State removed! Here are the details:")
        st.dataframe(st.session_state.df.iloc[index], use_container_width=True, hide_index=True)

        # Remove head of state
        st.session_state.df = st.session_state.df.drop(index)
        save_data(st.session_state.df)

# Show a Tag with custom CSS
st.markdown(
    """
        <footer>
            <p style="color: grey; margin: 2px 0;">Inspired by Ousama Ranking</p>
            <p style="color: grey; font-size: 12px; margin: 2px 0;">Unemployment from multiple sources compiled by World Bank (2024)</p>
            <p style="color: grey; font-size: 12px; margin: 2px 0;">UN, World Population Prospects (2024)</p>
            <p style="color: grey; font-size: 12px; margin: 2px 0;">Income share of the richest 1% (before tax) (World Inequality Database)</p>
            <p style="color: grey; font-size: 12px; margin: 2px 0;">Penn World Table: Output-side real GDP at current PPPs (in mil. 2017US$)</p>
        </footer>
        <style>
            footer {
                position: relative;
                width: 100%;
                color: white;
                text-align: center;
            }
        </style>

    """
    , unsafe_allow_html=True)
