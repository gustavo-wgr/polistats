# Polistats
A comprehensive data aggregator designed to provide insights into various government administrations, enabling users to compare their performances quantitatively. Our platform offers a user-friendly interface that simplifies the exploration of key statistics across different leaders and their policies.

The app uses **Streamlit** for its general functionality and **pandas** for data manipulation.

## Functionality
2 distinct datasets, one for statistical data, another for heads of state,  have been first normalized to be in correspondence with each other.
> For more information about the sources of the datasets, check out the "Data" section.

Then, a couple of datasets have been made with their use:
- The dataset in the "**Default**" section,  which shows each country's stats in the year of their heads’ of state start- and end-of-term.
- The dataset  in the "**Select**" section, which shows the individual stats as an average, where the sum of them in given years is divided by the number of years a head of state has been in office: 
$$\frac{1}{N} \sum_{s}^{e} x_s $$ 
> $x_s$ = value of a statistic in the year $s$
> $s$/$e$ = year of start-of-term/end-of-term
> $N$ = number of years in office

The selection of stats is possible in the "**Default**" section.
The stats featured are:
- Inflation Rate
- Unemployment Rate
- GDP Growth
- GDP Per Capita Growth
- Trade (% of GDP)
- Central Government Debt (% of GDP)
- GINI index
- Population Growth
- Labor Force Participation Rate

For better visualization, one can select specific heads of state in the "**Select**" section and then have them displayed as a scatter plot in the "**Compare**" section. 

## Data
Statistical data by [The World Bank Group ](https://databank.worldbank.org/).
License: https://datacatalog.worldbank.org/public-licenses.

Heads of state data by Harvard [Political Leaders' Affiliation Database](https://plad.me/).
> The file inside the repository is from April 2024.
> If it has been updated:
> - Visit their official website:  https://plad.me/
> - Download the newest version
> - Replace the file "PLAD_April_2024.tab" in your local repository
> 
> Or just contact me and I will change  the file in the repository :D.