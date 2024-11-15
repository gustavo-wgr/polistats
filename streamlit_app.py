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
    # Data (by World Bank Group), starting from 1948
    dataTemp = wb.download(indicator=[
        'NY.GDP.DEFL.KD.ZG', # Inflation rate
        'SL.UEM.TOTL.ZS', # Unemployment rate
        'NY.GDP.MKTP.KD.ZG', # Annual GDP growth
        'NY.GDP.PCAP.KD.ZG', # Annual GDP per capita growth
        'NE.TRD.GNFS.ZS', # Trade (% of GDP)
        'GC.DOD.TOTL.GD.ZS', # Central government debt (% of GDP)
        'SI.POV.GINI', # GINI index
        'SP.POP.GROW', # Population growth
        'SL.TLF.CACT.ZS', # Labor force participation rate
        ], start=1948, end=date.today().year, country=["all"])
    # Format it as pandas dataframe
    dataTemp = pd.DataFrame(dataTemp)
    # Renaming columns of general data
    dataTemp.rename(columns={
        'NY.GDP.DEFL.KD.ZG': 'Inflation Rate', 
        'SL.UEM.TOTL.ZS': 'Unemployment Rate', 
        'NY.GDP.MKTP.KD.ZG': 'GDP Growth', 
        'NY.GDP.PCAP.KD.ZG': 'GDP Per Capita Growth', 
        'NE.TRD.GNFS.ZS': 'Trade (% of GDP)', 
        'GC.DOD.TOTL.GD.ZS': 'Central Government Debt (% of GDP)', 
        'SI.POV.GINI': 'GINI index', 
        'SP.POP.GROW': 'Population Growth', 
        'SL.TLF.CACT.ZS': 'Labor Force Participation Rate', 
        }, inplace=True)
    # To use 'year' as a column for merging
    dataTemp.reset_index(inplace=True)

    return dataTemp

# To change col names; needed globally for Stat selecion to work efficiently
AvgColNames = {
    'Inflation Rate': 'Avg. Inflation Rate', 
    'Unemployment Rate': 'Avg. Unemployment Rate', 
    'GDP Growth': 'Avg. GDP Growth', 
    'GDP Per Capita Growth': 'Avg. GDP Per Capita Growth', 
    'Trade (% of GDP)': 'Avg. Trade', 
    'Central Government Debt (% of GDP)': 'Avg. Gov. Debt', 
    'GINI index': 'Avg. GINI index', 
    'Population Growth': 'Avg. Population Growth', 
    'Labor Force Participation Rate': 'Avg. LF. Part.'}

@st.cache_data()
def calc_avg():
    # Placeholder to return
    dataTemp = dataAvg

    for i in range(len(dataAvg)):
        # Saving specific row
        leader = dataAvg.iloc[i]
        # Selects data at appropriate country (@leader.iloc[0]) and time range (@leader.iloc[2][:4] = start year, @leader.iloc[3][:4] = end year)
        statsTemp = dataGeneral[(dataGeneral['country'] == leader.iloc[0]) & (dataGeneral['year'].between(leader.iloc[2][:4], leader.iloc[3][:4], inclusive='both'))].iloc[:, 2:]
        # Replaces [Inf; Unemp; GDP] with the means of data
        dataTemp.iloc[i, 4:] = statsTemp.mean()

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
buffer, col, buffer2 = st.columns([0.2, 0.6, 0.2])
with col: 
    # The 3 great tabs of Polistats
    default, select, compare = st.tabs(["Default", "Select", "Compare"])
    # Tab for showing the data table and selecting statistics
    with default:
        # The dropdown selection
        StatSelection = st.multiselect("Stats", (
            'Inflation Rate', 
            'Unemployment Rate', 
            'GDP Growth', 
            'GDP Per Capita Growth', 
            'Trade (% of GDP)', 
            'Central Government Debt (% of GDP)', 
            'GINI index', 
            'Population Growth', 
            'Labor Force Participation Rate'), 
            placeholder='Select Stats', 
            label_visibility='collapsed', 
            default=['Inflation Rate', 'Unemployment Rate', 'GDP Growth', 'GDP Per Capita Growth'])

        # Displaying the data table with selected stats
        st.dataframe(dataMain[['country', 'leader', 'startdate', 'enddate', 'year'] + StatSelection], hide_index=True, use_container_width=True, height=421)

    # Tab for selection of rows from the table
    with select:
        dataSelected = st.dataframe(
            # Only showing necessary stats with @StatSelection and correcting names
            dataAvg[['country', 'leader', 'startdate', 'enddate'] + StatSelection].rename(columns=AvgColNames),
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
            dataAvg.iloc[dataSelected.selection.rows][['country', 'leader', 'startdate', 'enddate'] + StatSelection].rename(columns=AvgColNames),
            use_container_width=True,
            hide_index=True
        )
    
    # Tab for graphical representation of selected rows
    with compare:
        # When selections are made, show the scatter graphs
        if len(selection) > 0:
            # Skeleton df for all 3 statistics
            dataVar = {}
            # Skeleton df for 'Inflation Rate'
            dataInf = {}
            # Skeleton df for 'Unemployment Rate'
            dataUnemp = {}
            # Skeleton df for 'GDP Growth'
            dataGdp = {}
            # Skeleton df for 'GDP Per Capita Growth'
            dataGdpPc = {}
            # Skeleton df for 'Trade (% of GDP)'
            dataTr = {}
            # Skeleton df for 'Central Government Debt (% of GDP)'
            dataCGD = {}
            # Skeleton df for 'GINI index'
            dataGINI = {}
            # Skeleton df for 'Population Growth'
            dataPg = {}
            # Skeleton df for 'Labor Force Participation Rate'
            dataLFPR = {}

            # Selection of only stats; for optimization
            dataAvgTemp = dataAvg[StatSelection]

            for index in selection: # 
                # The selected rows of dataAvg
                point = dataAvg.iloc[index]

                # Name of datapoint: "leader; start year/end year; country"
                selectionName = (point['leader'] + "; " 
                + point['startdate'][:4] + "/" 
                + point['enddate'][:4] + "; " 
                + point['country'])

                # For while loop optimization
                point = dataAvgTemp.iloc[index]

                # Loop counter
                i = 0
                # Dictionary for specific stat values
                pointTemp = []
                # Temporary holder for Singular Graphs
                dataTemp = {}
                while(i < len(StatSelection)): 
                    pointTemp.append(point[i])

                    i += 1
                
                # For singular graphs
                point = dataAvg.iloc[index][4:]

                # Plugging in correct statistical data
                dataVar[selectionName] = pointTemp
                dataInf[selectionName] = point['Inflation Rate']
                dataUnemp[selectionName] = point['Unemployment Rate']
                dataGdp[selectionName] = point['GDP Growth']
                dataGdpPc[selectionName] = point['GDP Per Capita Growth']
                dataTr[selectionName] = point['Trade (% of GDP)']
                dataCGD[selectionName] = point['Central Government Debt (% of GDP)']
                dataGINI[selectionName] = point['GINI index']
                dataPg[selectionName] = point['Population Growth']
                dataLFPR[selectionName] = point['Labor Force Participation Rate']

            # Making dfs with appropriate index names
            dataVar = pd.DataFrame(dataVar, index=StatSelection)
            dataInf = pd.DataFrame(dataInf, index=['Avg. Inf. Rate'])
            dataUnemp = pd.DataFrame(dataUnemp, index=['Avg. Unemp. Rate'])
            dataGdp = pd.DataFrame(dataGdp, index=['Avg. GDP Growth Rate'])
            dataGdpPc = pd.DataFrame(dataGdpPc, index=['Avg. GDP PC. Growth Rate'])
            dataTr = pd.DataFrame(dataTr, index=['Avg. Trade'])
            dataCGD = pd.DataFrame(dataCGD, index=['Avg. Gov. Debt'])
            dataGINI = pd.DataFrame(dataGINI, index=['Avg. GINI index'])
            dataPg = pd.DataFrame(dataPg, index=['Avg. Population Growth'])
            dataLFPR = pd.DataFrame(dataLFPR, index=['Avg. LF. Part.'])

            # Display main data graph
            st.header("Scatter")
            st.scatter_chart(dataVar)

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

                    st.header("Avg. GDP Growth Data")
                    st.scatter_chart(dataGdp)
                    st.divider()

                    st.header("Avg. GDP PC. Growth Data")
                    st.scatter_chart(dataGdpPc)
                    st.divider()

                    st.header("Avg. Trade")
                    st.scatter_chart(dataTr)
                    st.divider()

                    st.header("Avg. Gov. Debt")
                    st.scatter_chart(dataCGD)
                    st.divider()

                    st.header("Avg. GINI index")
                    st.scatter_chart(dataGINI)
                    st.divider()

                    st.header("Avg. Population Growth")
                    st.scatter_chart(dataPg)
                    st.divider()

                    st.header("Avg. LF. Part.")
                    st.scatter_chart(dataLFPR)

        else:
            st.markdown("Nothing to see here yet folks!")

# A lovely tag <3 skypacca
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