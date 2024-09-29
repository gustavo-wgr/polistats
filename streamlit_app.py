import streamlit as st
import pandas as pd

from pandas_datareader import wb
from datetime import date

# Data of Head of States in respect to country and date (PLAD Harvard)
dataHOS = pd.read_csv('PLAD_April_2024.tab', sep='\t')
# Take only: country code; HOS; start year of HOS; end year of HOS
dataHOS = dataHOS[['country', 'leader', 'startdate', 'enddate', 'startyear', 'endyear']]
# Normalize column 'startyear' and 'endyear' types (float -> str)
dataHOS = dataHOS.astype({'startyear': int})
dataHOS = dataHOS.astype({'startyear': str})
dataHOS = dataHOS.astype({'endyear': int})
dataHOS = dataHOS.astype({'endyear': str})
# Taking the 'country' column
dataTemp = dataHOS['country']
# Country names to normalize
replace_dic = {
    'Bahamas': 'Bahamas, The',
    'Bosnia': 'Bosnia and Herzegovina',
    'Brunei': 'Brunei Darussalam',
    'Cap Verde': 'Cabo Verde',
    'Congo': 'Congo, Rep.',
    'Czech Republic': 'Czechia',
    'Democratic Republic of the Congo': 'Congo, Dem. Rep.',
    'East Timor': 'Timor-Leste',
    'Egypt': 'Egypt, Arab Rep.',
    'Gambia': 'Gambia, The',
    'Iran': 'Iran, Islamic Rep.',
    'Kyrgyzstan': 'Kyrgyz Republic',
    'Laos': 'Lao PDR',
    'Luxemburg': 'Luxembourg',
    'Macedonia': 'North Macedonia',
    'Moldavia': 'Moldova',
    'North Korea': 'Korea, Dem. People\'s Rep.',
    'Russia': 'Russian Federation',
    'Slovakia': 'Slovak Republic',
    'South Korea': 'Korea, Rep.',
    'Syria': 'Syrian Arab Republic',
    'Turkey': 'Turkiye',
    'Venezuela': 'Venezuela, RB',
    'Vietnam': 'Viet Nam',
    'Yemen': 'Yemen, Rep.',
    'United States of America': 'United States'
    }
# Normalizing 'country' names
dataTemp.replace(replace_dic, inplace=True)
# Replacing 'country' in HOS df with normalized names
dataHOS['country'] = dataTemp

# Singular tables of data if needed

# Inflation data (World Bank)
# dataInf = wb.data.DataFrame("NY.GDP.DEFL.KD.ZG")

# Unemployment data (World Bank)
# dataUnem = wb.data.DataFrame("SL.UEM.TOTL.ZS")

# Annual GDP growth data (World Bank)
# dataGdpGrowth = wb.data.DataFrame("NY.GDP.MKTP.KD.ZG")

# Annual GDP per capita growth data (World Bank)
# dataGdpPcGworth = wb.data.DataFrame("NY.GDP.PCAP.KD.ZG")

# Data (by World Bank Group), starting from 1948, for: Inflation rate; Unemployment rate; Annual GDP growth data; Annual GDP per capita growth                             
dataGeneral = wb.download(indicator=['NY.GDP.DEFL.KD.ZG', 'SL.UEM.TOTL.ZS', 'NY.GDP.MKTP.KD.ZG', 'NY.GDP.MKTP.KD.ZG'], start=1948, end=date.today().year, country=["all"]) # 'country=["AFG"]' is here just for testing performance
# Format it as pandas dataframe                                                                                                                                            # Switch with 'country=['all']' for full data
dataGeneral = pd.DataFrame(dataGeneral)
# Renaming columns of general data
dataGeneral.rename(columns={
    'NY.GDP.DEFL.KD.ZG': 'Inflation Rate', 
    'SL.UEM.TOTL.ZS': 'Unemployment Rate', 
    'NY.GDP.MKTP.KD.ZG': 'GDP Growth', 
    'NY.GDP.PCAP.KD.ZG': 'GDP Per Capita'
    }, inplace=True)
# To use 'year' as a column for merging
dataGeneral.reset_index(inplace=True)

# Merge on 'startyear' == 'year'
dataStart = dataHOS.merge(dataGeneral, left_on=['startyear', 'country'], right_on=['year', 'country'])
# Merge on 'endyear' == 'year'
dataEnd = dataHOS.merge(dataGeneral, left_on=['endyear', 'country'], right_on=['year', 'country'])

# Make main dataframe from HOS df and PLAD df
dataMain = pd.concat([dataStart, dataEnd]).drop_duplicates().reset_index(drop=True)
# Sort first by 'country', then by'startdate', then by 'leader'
dataMain.sort_values(by=['country', 'startdate', 'leader'], inplace=True)

st.write(dataMain) # Just for testing

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

st.markdown(
    """
        <footer>
            <p style="color: grey; margin: 2px 0;">Inspired by Ousama Ranking</p>
            <p style="color: grey; font-size: 10px; margin: 2px 0;">Economic data by The World Bank Group (2024)</p>
            <p style="color: grey; font-size: 10px; margin: 2px 0;">Head of State data by Harvard PLOD (2024)</p>
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