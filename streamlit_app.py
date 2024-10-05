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
    'West Germany': 'Germany',
    'Yemen': 'Yemen, Rep.',
    'United States of America': 'United States'
    }
# Normalizing 'country' names
dataTemp.replace(replace_dic, inplace=True)
# Replacing 'country' in HOS df with normalized names
dataHOS['country'] = dataTemp

# Data (by World Bank Group), starting from 1948, for: Inflation rate; Unemployment rate; Annual GDP growth data; Annual GDP per capita growth                             
dataGeneral = wb.download(indicator=['NY.GDP.DEFL.KD.ZG', 'SL.UEM.TOTL.ZS', 'NY.GDP.MKTP.KD.ZG', 'NY.GDP.MKTP.KD.ZG'], start=1948, end=date.today().year, country=["all"])
# Format it as pandas dataframe
dataGeneral = pd.DataFrame(dataGeneral)
# Renaming columns of general data
dataGeneral.rename(columns={
    'NY.GDP.DEFL.KD.ZG': 'Inflation Rate', 
    'SL.UEM.TOTL.ZS': 'Unemployment Rate', 
    'NY.GDP.MKTP.KD.ZG': 'GDP Growth', 
    'NY.GDP.PCAP.KD.ZG': 'GDP Per Capita' #-----------------use this? prolly...yeah; at the end tho
    }, inplace=True)
# To use 'year' as a column for merging
dataGeneral.reset_index(inplace=True)

# Prepping a new df for average general data
dataAvg = dataHOS.merge(dataGeneral, left_on=['startyear', 'country'], right_on=['year', 'country'])
dataAvg.drop(columns=['year'], inplace=True)

# Calculation of average general data
for leader in dataHOS.iterrows(): #------------------------- needs hella optimization
    # References the years
    startTemp = leader[1]['startdate'][:4]
    endTemp = leader[1]['enddate'][:4]
    # Selects appropriate country and time range
    dataTemp = dataGeneral[(dataGeneral['country'] == leader[1]['country']) & (dataGeneral['year'] >= startTemp) & (dataGeneral['year'] <= endTemp)]

    # Calculates average data
    avgInf = dataTemp['Inflation Rate'].mean()
    avgUnemp = dataTemp['Unemployment Rate'].mean()
    avgGdp = dataTemp['GDP Growth'].mean()

    # Finds correct index in @dataAvg
    index = dataAvg[(dataAvg['country'] == leader[1]['country']) & (dataAvg['startyear'] == leader[1]['startyear']) & (dataAvg['endyear'] == leader[1]['endyear'])].index

    # Replaces with average data
    dataAvg.loc[index, 'Inflation Rate'] = avgInf
    dataAvg.loc[index, 'Unemployment Rate'] = avgUnemp
    dataAvg.loc[index, 'GDP Growth'] = avgGdp

# 'startyear' and 'endyear' not necessary anymore
dataAvg.drop(columns=['startyear', 'endyear'], inplace=True)
# Changed to correct names
dataAvg.rename(columns={
    'Inflation Rate': 'Avg. Inflation Rate', 
    'Unemployment Rate': 'Avg. Unemployment Rate', 
    'GDP Growth': 'Avg. GDP Growth' 
    }, inplace=True)

# Merge on 'startyear' == 'year'
dataStart = dataHOS.merge(dataGeneral, left_on=['startyear', 'country'], right_on=['year', 'country'])
# Merge on 'endyear' == 'year'
dataEnd = dataHOS.merge(dataGeneral, left_on=['endyear', 'country'], right_on=['year', 'country'])

# Make main dataframe from HOS df and PLAD df
dataMain = pd.concat([dataStart, dataEnd]).drop_duplicates()
# Removing unnecessary columns: 'startyear'; 'endyear'
dataMain.drop(columns=['startyear', 'endyear'], inplace=True)
# Sort first by 'country', then by'startdate', then by 'leader'
dataMain.sort_values(by=['country', 'startdate', 'leader'], inplace=True)
# Re-indexing by the above-written sort
dataMain.reset_index(drop=True, inplace=True)

# layout='wide' for more width from parent div of main df
st.set_page_config(page_title="Polistats", page_icon="🏛️", layout='wide')
# The title uses markdown for alignment
st.markdown("<h1 style='text-align: center'>🏛️ Polistats</h1>", unsafe_allow_html=True)

# For custom width
buffer, col1, buffer2 = st.columns([0.2, 0.6, 0.2])
with col1:
    # The tabs
    default, select, compare = st.tabs(["Default", "Select", "Compare"])
    # Tab for just showing the data table
    with default:
        st.dataframe(dataMain, hide_index=True, use_container_width=True, height=458)
    
    # Tab for selection of rows from the table
    with select:
        dataSelected = st.dataframe(
            dataAvg,
            on_select='rerun',
            selection_mode='multi-row',
            use_container_width=True,
            hide_index=True,
            height=388,
        )

        st.divider()

        # Displaying selected rows
        st.header("Selection")
        selection = dataSelected.selection.rows
        st.dataframe(
            dataAvg.iloc[dataSelected.selection.rows],
            use_container_width=True,
        )
    
    # Tab for graphical representation of selected rows
    with compare:
        # Df for 'Inflation Rate'
        dataInf = {}
        for item in selection:
            dataInf[dataAvg.iloc[item]['leader']] = dataAvg.iloc[item]['Avg. Inflation Rate']
        dataInf = pd.DataFrame(dataInf, index=['Avg. Inf. Rate'])

        # Df for 'Unemployment Rate'
        dataUnemp = {}
        for item in selection:
            dataUnemp[dataAvg.iloc[item]['leader']] = dataAvg.iloc[item]['Avg. Unemployment Rate']
        dataUnemp = pd.DataFrame(dataUnemp, index=['Avg. Unemp. Rate'])

        # Df for 'GDP Growth'
        dataGdp = {}
        for item in selection:
            dataGdp[dataAvg.iloc[item]['leader']] = dataAvg.iloc[item]['Avg. GDP Growth']
        dataGdp = pd.DataFrame(dataGdp, index=['Avg. GDP Growth Rate'])

        # When selections are made, show the scatter graphs
        if len(selection) > 1:
            st.header("Inflation data")
            st.scatter_chart(dataInf)
            st.divider()

            st.header("Unemployment data")
            st.scatter_chart(dataUnemp)
            st.divider()

            st.header("GDP data")
            st.scatter_chart(dataGdp)

        else:
            st.markdown("Nothing to see here yet folks!")

# A lovely tag
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