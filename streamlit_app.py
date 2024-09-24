import streamlit as st
import pandas as pd
st.set_page_config(page_title="Polistats", page_icon="🏛️")
st.title("🏛️ Polistats")

# Dictionary holding the statistics for each president
president_data = {
    'Obama': pd.DataFrame({
        'Metric': ['GDP Growth', 'Unemployment Rate', 'Inflation Rate'],
        'Value': [2.3, 5.0, 1.6]
    }),
    'Trump': pd.DataFrame({
        'Metric': ['GDP Growth', 'Unemployment Rate', 'Inflation Rate', 'Tariff Rates'],
        'Value': [2.5, 3.9, 1.8, 12.0]
    }),
    'Biden': pd.DataFrame({
        'Metric': ['GDP Growth', 'Unemployment Rate', 'COVID-19 Recovery'],
        'Value': [3.0, 4.5, 70.0]
    })
}

# Let users select two presidents to compare
presidents = st.multiselect("Select two presidents to compare", list(president_data.keys()), default=["Obama", "Trump"])

# Ensure that exactly two presidents are selected
if len(presidents) == 2:
    # Get the two selected DataFrames
    df1 = president_data[presidents[0]]
    df2 = president_data[presidents[1]]

    # Merge on 'Metric' to find common statistics
    df_comparison = pd.merge(df1, df2, on='Metric', suffixes=(f'_{presidents[0]}', f'_{presidents[1]}'))

    if not df_comparison.empty:
        st.write(f"### Comparison between {presidents[0]} and {presidents[1]}")
        # Use st.dataframe for an interactive table
        st.dataframe(df_comparison)
    else:
        st.write(f"No common statistics found between {presidents[0]} and {presidents[1]}")
else:
    st.write("Please select exactly two presidents to compare.")
