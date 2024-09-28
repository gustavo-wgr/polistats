import streamlit as st
import pandas as pd
import pandas_datareader as pdr

from pandas_datareader import wb


# Data of Head of States in respect to country and date (PLAD Harvard)
dataHOS = pd.read_csv('PLAD_April_2024.tab', sep='\t')

# Singular tables of data if needed

# Inflation data (World Bank)
# dataInf = wb.data.DataFrame("NY.GDP.DEFL.KD.ZG")

# Unemployment data (World Bank)
# dataUnem = wb.data.DataFrame("SL.UEM.TOTL.ZS")

# Annual GDP growth data (World Bank)
# dataGdpGrowth = wb.data.DataFrame("NY.GDP.MKTP.KD.ZG")

# Annual GDP per capita growth data (World Bank)
# dataGdpPcGworth = wb.data.DataFrame("NY.GDP.PCAP.KD.ZG")

# Data, starting from 1989, for: Inflation rate; Unemployment rate; Annual GDP growth data; Annual GDP per capita growth
dataGeneral = wb.download(indicator=['NY.GDP.DEFL.KD.ZG', 'SL.UEM.TOTL.ZS', 'NY.GDP.MKTP.KD.ZG', 'NY.GDP.PCAP.KD.ZG'], start=1989)


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
