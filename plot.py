import pandas
# (*) Tools to communicate with Plotly's server
import plotly.plotly as py
import plotly.graph_objs as go
import xml.etree.ElementTree as ET
import textwrap
tree = ET.parse('group_location.kml')
root = tree.getroot()
df_loc = pandas.DataFrame.from_records([(int(placemark.find('{http://www.opengis.net/kml/2.2}name').text), placemark.find('*//{http://www.opengis.net/kml/2.2}coordinates').text)
    for placemark in root.findall("*/{http://www.opengis.net/kml/2.2}Placemark")],
    columns=('Group Practice PAC ID', 'Coordinates'), index = 'Group Practice PAC ID')
# Create two lists for the loop results to be placed
lat = []
lon = []

# For each row in a varible,
for row in df_loc['Coordinates']:
    # Try to,
    try:
        # Split the row by comma and append
        # everything before the comma to lat
        lat.append(float(row.split(',')[1]))
        # Split the row by comma and append
        # everything after the comma to lon
        lon.append(float(row.split(',')[0]))
    # But if you get an error
except:
        # append a missing value to lat
        lat.append(np.NaN)
        # append a missing value to lon
        lon.append(np.NaN)

# Create two new columns from lat and lon
df_loc['latitude'] = lat
df_loc['longitude'] = lon
df = pandas.DataFrame.from_csv('Physician_Compare_2013_Group_Practice_Public_Reporting.csv', 
 index_col = 'Group Practice PAC ID')
df_results= df.join(df_loc)
colors = ["rgb(255,0,0)","rgb(255,255,0)","rgb(128,255,0)"]
labels = ["Low", "Average", "High"]
measures = [key for key in dict(df_results.dtypes) if dict(df_results.dtypes)[key] 
in ['float64', 'int64'] and key not in ['latitude','longitude']]
#Drop rows where any value is not recorded
df_results = df_results.dropna(axis=0, how="any", subset=measures)
practices_group=[]
layout = dict(
    title = "Interactive Map:<br> Physician Quality Reporting <br>System Results, 2013",
    autosize = True,
    legend = dict(
        x=1,
        y= 1,
        bgcolor="rgba(255, 255, 255, 0)"
        )
    )
df_results["mean"]=df_results[measures].mean(axis=1)
practices = []
cutoffs = [0,.25,.75,1]
cuttoff_designation = ['(Bottom Quartile)', '(Middle Quartiles)', '(Top Quartile)']
limits = df_results["mean"].quantile(cutoffs)
for i in range(len(cutoffs)-1):          
    df_sub = df_results[(df_results["mean"]
     >= limits[cutoffs[i]]) & (df_results["mean"] <= limits[cutoffs[i+1]])]
    practice = dict(
        type = 'scattergeo',
        locationmode = 'USA-states',
        legendgroup= colors[i],
        showlegend = True,
        hoverinfo="text",
        lon = df_sub['longitude'],
        lat = df_sub['latitude'],
        textposition='top left',
        text = "<b>"+ df_sub["Organization Legal Name or 'Doing Business As' Name"].str.wrap(25).str.replace("\n","<br>") + " (" + df_sub['State'] + ")</b>"
        "<br><b>Percent of patients who met standard of care:</b>"+
        "<br>"+df_sub[measures[0]].map(lambda x: '<b>%.2f%%</b> - <i>%s</i>' % (x, measures[0])).str.wrap(50).str.replace("\n","<br>") +
        "<br>"+df_sub[measures[1]].map(lambda x: '<b>%.2f%%</b> - <i>%s</i>' % (x, measures[1])).str.wrap(50).str.replace("\n","<br>") +
        "<br>"+df_sub[measures[2]].map(lambda x: '<b>%.2f%%</b> - <i>%s</i>' % (x, measures[2])).str.wrap(50).str.replace("\n","<br>") +
        "<br>"+df_sub[measures[3]].map(lambda x: '<b>%.2f%%</b> - <i>%s</i>' % (x, measures[3])).str.wrap(50).str.replace("\n","<br>"),
        marker = dict(
            size = 8,
            color = colors[i],
            line = dict(width=0.5, color='rgb(40,40,40)'),
            sizemode = 'area'
            ),
        name = '%s Performing'% labels[i]+ '<br>' + cuttoff_designation[i]
        )
    practices.append(practice)
    layout['geo'] = dict(
        scope='usa',
        projection=dict( type='albers usa' ),
        showland = True,
        landcolor = 'rgb(217, 217, 217)',
        subunitwidth=1,
        countrywidth=1,
        subunitcolor="rgb(255, 255, 255)",
        countrycolor="rgb(255, 255, 255)",
        font = dict(family='Arial' )
        )
    fig = dict(data=practices, layout=layout)
    py.iplot( fig, validate=False, filename='PQRS-final-2')