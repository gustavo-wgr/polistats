import streamlit as st
import pandas as pd

from pandas_datareader import wb
from datetime import date

# Data of Head of States in respect to country and date (PLAD Harvard)
dataHOS = pd.read_csv('PLAD_April_2024.tab', sep='\t')

# For optimazation, don't rerun for any reason
@st.cache_data()
# Need function to use '@st.cache_data'
def norm_hos():
    dataTemp = dataHOS
    # Take only: country code; HOS; start year of HOS; end year of HOS
    dataTemp = dataTemp[['country', 'leader', 'startdate', 'enddate', 'startyear', 'endyear']]
    # Normalize column 'startyear' and 'endyear' types (float -> str)
    dataTemp = dataTemp.astype({'startyear': int})
    dataTemp = dataTemp.astype({'startyear': str})
    dataTemp = dataTemp.astype({'endyear': int})
    dataTemp = dataTemp.astype({'endyear': str})
    # Taking the 'country' column
    countryTemp = dataHOS['country']
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
    countryTemp.replace(replace_dic, inplace=True)
    # Replacing 'country' in HOS df with normalized names
    dataTemp['country'] = countryTemp

    return dataTemp

# For @calc_avg()
dataGeneral = {}
@st.cache_data()
def calc_general():
    # Data (by World Bank Group), starting from 1948, for: Inflation rate; Unemployment rate; Annual GDP growth; Annual GDP per capita growth
    dataTemp = wb.download(indicator=[
        'NY.GDP.DEFL.KD.ZG', 
        'SL.UEM.TOTL.ZS', 
        'NY.GDP.MKTP.KD.ZG', 
        'NY.GDP.PCAP.KD.ZG'
        ], start=1948, end=date.today().year, country=["all"])
    # Format it as pandas dataframe
    dataTemp = pd.DataFrame(dataTemp)
    # Renaming columns of general data
    dataTemp.rename(columns={
        'NY.GDP.DEFL.KD.ZG': 'Inflation Rate', 
        'SL.UEM.TOTL.ZS': 'Unemployment Rate', 
        'NY.GDP.MKTP.KD.ZG': 'GDP Growth', 
        'NY.GDP.PCAP.KD.ZG': 'GDP Per Capita Growth' #-----------------use this? prolly...yeah; at the end tho; which is now!
        }, inplace=True)
    # To use 'year' as a column for merging
    dataTemp.reset_index(inplace=True)

    return dataTemp

@st.cache_data()
def calc_avg():
    # Placeholder to return
    dataTemp = dataAvg

    for i in range(len(dataAvg)):
        # Saving specific row
        leader = dataAvg.iloc[i]
        # Selects data at appropriate country (@leader.iloc[0]) and time range (@leader.iloc[2][:4] = start year, @leader.iloc[3][:4] = end year)
        statsTemp = dataGeneral[(dataGeneral['country'] == leader.iloc[0]) & (dataGeneral['year'].between(leader.iloc[2][:4], leader.iloc[3][:4], inclusive='both'))].iloc[:, [2, 3, 4]]
        # Replaces [Inf; Unemp; GDP] with the means of data
        dataTemp.iloc[i, [4, 5, 6]] = statsTemp.mean()

    # Change to correct names
    dataTemp.rename(columns={
    'Inflation Rate': 'Avg. Inflation Rate', 
    'Unemployment Rate': 'Avg. Unemployment Rate', 
    'GDP Growth': 'Avg. GDP Growth', 
    'GDP Per Capita Growth': 'Avg. GDP Per Capita Growth'
    }, inplace=True)

    return dataTemp

@st.cache_data()
def calc_main():
    # Merge on 'startyear' == 'year'
    dataStart = dataHOS.merge(dataGeneral, left_on=['startyear', 'country'], right_on=['year', 'country'])
    # Merge on 'endyear' == 'year'
    dataEnd = dataHOS.merge(dataGeneral, left_on=['endyear', 'country'], right_on=['year', 'country'])

    # Make main dataframe from HOS df and PLAD df
    dataTemp = pd.concat([dataStart, dataEnd]).drop_duplicates()
    # Removing unnecessary columns: 'startyear'; 'endyear'
    dataTemp.drop(columns=['startyear', 'endyear'], inplace=True)
    # Sort first by 'country', then by'startdate', then by 'leader'
    dataTemp.sort_values(by=['country', 'startdate', 'leader'], inplace=True)
    # Re-indexing by the above-written sort
    dataTemp.reset_index(drop=True, inplace=True)

    return dataTemp

# layout='wide' for more width from parent div of main df
st.set_page_config(page_title="Polistats", page_icon="🏛️", layout='wide')
# The title uses markdown for alignment
st.markdown("<h1 style='text-align: center'>🏛️ Polistats</h1>", unsafe_allow_html=True)

# Normalizing Head of State df
dataHOS = norm_hos()
# Calculation of general statistics df
dataGeneral = calc_general()
# Calculation of main df
dataMain = calc_main()

# Prepping a new df for average general data
dataAvg = dataHOS.drop(columns=['endyear']).merge(dataGeneral, left_on=['startyear', 'country'], right_on=['year', 'country'])
dataAvg.drop(columns=['year', 'startyear'], inplace=True)
# Calculation of average general data
dataAvg = calc_avg()

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
            hide_index=True
        )
    
    # Tab for graphical representation of selected rows
    with compare:
        # When selections are made, show the scatter graphs
        if len(selection) > 0:
            # Skeleton df for all 3 statistics
            dataQuad = {}
            # Skeleton df for 'Inflation Rate'
            dataInf = {}
            # Skeleton df for 'Unemployment Rate'
            dataUnemp = {}
            # Skeleton df for 'GDP Growth'
            dataGdp = {}
            # Skeleton df for 'GDP Per Capita Growth'
            dataGdpPc = {}

            for index in selection:
                # The selected rows of dataAvg
                point = dataAvg.iloc[index]

                # Name of datapoint: "leader; start year/end year; country"
                selectionName = (point['leader'] + "; " 
                + point['startdate'][:4] + "/" 
                + point['enddate'][:4] + "; " 
                + point['country'])

                # Plugging in correct statistical data
                dataQuad[selectionName] = [
                    point['Avg. Inflation Rate'], 
                    point['Avg. Unemployment Rate'], 
                    point['Avg. GDP Growth'], 
                    point['Avg. GDP Per Capita Growth']]
                dataInf[selectionName] = point['Avg. Inflation Rate']
                dataUnemp[selectionName] = point['Avg. Unemployment Rate']
                dataGdp[selectionName] = point['Avg. GDP Growth']
                dataGdpPc[selectionName] = point['Avg. GDP Per Capita Growth']
            
            # Making dfs with appropriate index names
            dataQuad = pd.DataFrame(dataQuad, index=['Avg. Inf. Rate', 'Avg. Unemp. Rate', 'Avg. GDP Growth Rate', 'Avg. GDP PC. Growth Rate'])
            dataInf = pd.DataFrame(dataInf, index=['Avg. Inf. Rate'])
            dataUnemp = pd.DataFrame(dataUnemp, index=['Avg. Unemp. Rate'])
            dataGdp = pd.DataFrame(dataGdp, index=['Avg. GDP Growth Rate'])
            dataGdpPc = pd.DataFrame(dataGdpPc, index=['Avg. GDP PC. Growth Rate'])

            # Display main data graph
            st.header("Scatter")
            st.scatter_chart(dataQuad)

            st.divider()

            # Expander for singular data graph displays
            with st.expander("Singular Data Graphs"):
                # To make graphs smaller
                buffer, col, buffer2 = st.columns([0.2, 0.6, 0.2])
                with col:
                    st.header("Avg. Inflation Data")
                    st.scatter_chart(dataInf)
                    st.divider()

                    st.header("Avg. Unemployment Data")
                    st.scatter_chart(dataUnemp)
                    st.divider()

                    st.header("Avg. GDP Data")
                    st.scatter_chart(dataGdp)
                    st.divider()

                    st.header("Avg. GDP PC. Data")
                    st.scatter_chart(dataGdpPc)

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