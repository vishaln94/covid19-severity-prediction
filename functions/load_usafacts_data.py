import pandas as pd

def load_daily_data(usafacts_data_cases = 'data/usafacts/confirmed_cases.csv',
                     usafacts_data_deaths = 'data/usafacts/deaths.csv'):
    
    cases = pd.read_csv(usafacts_data_cases, encoding="iso-8859-1")
    cases = cases.rename(columns={k: '#Cases_' + k for k in cases.keys() 
                                  if not 'county' in k.lower()
                                  and not 'state' in k.lower()})
    
    deaths = pd.read_csv(usafacts_data_deaths, encoding="iso-8859-1")
    deaths = deaths.rename(columns={k: '#Deaths_' + k for k in deaths.keys() 
                              if not 'county' in k.lower()
                              and not 'state' in k.lower()})
    
    cases = cases[cases.countyFIPS != 0] # ignore cases where county is unknown
    cases = cases.groupby(['countyFIPS']).sum().reset_index() # sum over duplicate counties
    deaths = deaths[deaths.countyFIPS != 0]
    deaths = deaths.groupby(['countyFIPS']).sum().reset_index()
    
    df = pd.merge(cases, deaths, how='left', on='countyFIPS')
    df = df.fillna(0)
    return df