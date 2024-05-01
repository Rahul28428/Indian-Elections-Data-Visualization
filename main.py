from matplotlib.pyplot import axis
import streamlit as st  # streamlit library
import pandas as pd  # pandas library
import yfinance as yf  # yfinance library
import datetime  # datetime library
from datetime import date
from plotly import graph_objs as go  # plotly library
from plotly.subplots import make_subplots
# from prophet import Prophet  # prophet library
# from prophet.plot import plot_plotly
import plotly.express as px
from streamlit_option_menu import option_menu  # select_options library
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import geopandas as gpd
from wordcloud import WordCloud
import plotly.graph_objects as go

from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import spacy
import re
nlp = spacy.load("en_core_web_sm")

from sklearn.feature_extraction import text
stop = text.ENGLISH_STOP_WORDS
from textblob import TextBlob



st.set_page_config(layout="wide", initial_sidebar_state="expanded")

def add_meta_tag():
    meta_tag = """
        <head>
            <meta name="google-site-verification" content="QBiAoAo1GAkCBe1QoWq-dQ1RjtPHeFPyzkqJqsrqW-s" />
        </head>
    """
    st.markdown(meta_tag, unsafe_allow_html=True)

# Main code
add_meta_tag()


import pandas as pd
raw_election_data = pd.read_csv("LS_2.0.csv")
convert = lambda x: float(str(x).split()[1].replace(",", "")) if str(x)[0] == 'R' else 0.0
raw_election_data.ASSETS = raw_election_data.ASSETS.apply(convert)
raw_election_data.LIABILITIES = raw_election_data.LIABILITIES.apply(convert)
raw_election_data['EDUCATION'] = raw_election_data['EDUCATION'].replace("Post Graduate\n", "Post Graduate")
raw_election_data['EDUCATION'] = raw_election_data['EDUCATION'].replace("Graduate Professional", "Graduate\nProfessional")
raw_election_data.at[192, "WINNER"] = 1
raw_election_data.at[702, "WINNER"] = 1
raw_election_data.at[951, "WINNER"] = 1
raw_election_data.at[1132, "WINNER"] = 1
raw_election_data.at[172, "WINNER"] = 0
candidates_df = raw_election_data.drop(['SYMBOL', 'GENERAL\nVOTES', 'POSTAL\nVOTES',
                        'OVER TOTAL ELECTORS \nIN CONSTITUENCY', 'OVER TOTAL VOTES POLLED \nIN CONSTITUENCY'], axis=1)
candidates_df.rename(columns = {"CRIMINAL\nCASES": "CRIMINAL CASES", "TOTAL\nVOTES": "TOTAL VOTES"}, inplace = True)
candidates_df.sort_values(["STATE", "CONSTITUENCY"], inplace = True)
candidates_df["CRIMINAL CASES"] = pd.to_numeric(candidates_df["CRIMINAL CASES"], errors = 'coerce').convert_dtypes()
candidates_personal_df = candidates_df[candidates_df.NAME != "NOTA"]
candidates_personal_df = candidates_personal_df.drop(["TOTAL VOTES", "TOTAL ELECTORS"], axis = 1)
winners_df = candidates_df[candidates_df.WINNER == 1].sort_values(["STATE", "CONSTITUENCY"]).reset_index()
winners_df.drop(["index", "WINNER"], axis = 1, inplace = True)
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt

sns.set_style('darkgrid')
matplotlib.rcParams['font.size'] = 14
matplotlib.rcParams['figure.figsize'] = (15, 10)
matplotlib.rcParams['figure.facecolor'] = '#00000000'

all_party_seats = winners_df.PARTY.value_counts().sort_values(ascending = False)

# Convert Series to DataFrame for plotting
df_all_party_seats = all_party_seats.reset_index()
df_all_party_seats.columns = ['Party', 'Count']

# Sort by Count in descending order
df_all_party_seats = df_all_party_seats.sort_values(by='Count', ascending=False)

# Assuming df_all_party_seats is the DataFrame containing party-wise seat counts
threshold = 10  # Define the threshold for grouping parties into "Others"

# Aggregate parties below the threshold into "Others"
df_others = df_all_party_seats[df_all_party_seats['Count'] < threshold]
others_count = df_others['Count'].sum()

# Add "Others" to the DataFrame
df_all_party_seats = df_all_party_seats[df_all_party_seats['Count'] >= threshold]
df_all_party_seats.loc[len(df_all_party_seats)] = ['Others', others_count]

# Calculate percentage seat share for each party
seat_percent = round((df_all_party_seats['Count'] / df_all_party_seats['Count'].sum()) * 100, 2)

# Add percentage seat share to the DataFrame
df_all_party_seats['Percentage'] = seat_percent.astype(str) + '%'

# Assuming df_all_party_seats is the DataFrame containing party-wise seat counts
threshold = 10  # Define the threshold for grouping parties into "Others"

# Aggregate parties below the threshold into "Others"
df_others = df_all_party_seats[df_all_party_seats['Count'] < threshold]
others_count = df_others['Count'].sum()

# Create a new DataFrame row for "Others"
others_row = pd.DataFrame({'Party': ['Others'], 'Count': [others_count]})

# Add "Others" row to the DataFrame
df_all_party_seats = pd.concat([df_all_party_seats, others_row], ignore_index=True)

# Custom colors for each party
colors = ['#f97d09', '#00bdfe', '#dc143c', '#0266b4', '#24b44c', '#ff6634',
          '#203354', '#105e27', '#22409a', '#FAAAAA']


age_groups = ['18-25', '26-35', '36-45', '46-55', '56-65', '66+']

# Categorize candidates' ages into age groups
candidates_personal_df['Age Group'] = pd.cut(candidates_personal_df['AGE'], bins=[18, 25, 35, 45, 55, 65, float('inf')], labels=age_groups)

# Calculate the count of candidates in each age group, segmented by whether they won or contested
age_group_counts = candidates_personal_df.groupby(['Age Group', 'WINNER']).size().unstack(fill_value=0).reset_index()

# Melt the DataFrame to create separate rows for each age group and status
melted_age_group_counts = pd.melt(age_group_counts, id_vars=['Age Group'], value_vars=[0, 1], var_name='Status', value_name='Number of Candidates')

# Rename the status values for better interpretation
melted_age_group_counts['Status'] = melted_age_group_counts['Status'].map({0: 'Contested', 1: 'Won'})
seat_category = winners_df.CATEGORY.value_counts()
pd.DataFrame(seat_category)

seat_category_df = seat_category.reset_index()
seat_category_df.columns = ['Category', 'Seats']

gender_group = candidates_personal_df.groupby(["GENDER", "WINNER"]).size()
gender_group = gender_group.unstack()
gender_group = gender_group[[1,0]]

# Calculate percentages of candidates by gender
candidates_gender_percentage = (candidates_personal_df['GENDER'].value_counts(normalize=True) * 100).round(2)

# Calculate percentages of winning candidates by gender
winners_gender_percentage = ((winners_df['GENDER'].value_counts() / candidates_personal_df['GENDER'].value_counts()) * 100).round(2)
winners_df["EDUCATION"].unique()
education = winners_df.EDUCATION.value_counts()
education = education.reindex(["Illiterate", "Literate", "5th Pass", "8th Pass", "10th Pass", "12th Pass", "Graduate",
                               "Graduate\nProfessional","Post Graduate", "Doctorate", "Others"])
# Define the categories and values for the grouped bar chart
categories = education.index
values_male = candidates_personal_df[candidates_personal_df['GENDER'] == 'MALE']['EDUCATION'].value_counts()
values_female = candidates_personal_df[candidates_personal_df['GENDER'] == 'FEMALE']['EDUCATION'].value_counts()

total_voters = candidates_df.groupby(["STATE", "CONSTITUENCY"])[["TOTAL VOTES"]].sum()
total_electors = winners_df.groupby(["STATE", "CONSTITUENCY"])[["TOTAL ELECTORS"]].sum()
votes_df = total_voters.join(total_electors)
votes_df["VOTER TURNOUT"] = round(votes_df["TOTAL VOTES"]/votes_df["TOTAL ELECTORS"]*100,2)

votes_df = votes_df.rename(index = {"Andaman & Nicobar Islands": "Andaman &\nNicobar Islands"})
# this is done purely for visualization purposes
const_turnout = votes_df.sort_values(by = ["VOTER TURNOUT"], ascending = False)
# Voter Turnout of all constituencies

high_consts = const_turnout.head(10)
low_consts = const_turnout.tail(10)
# getting the highest and the lowest Voter Outcome Constituencies

# Just for aesthetics

xh = high_consts.index.get_level_values(1) + "\n(" + high_consts.index.get_level_values(0) + ")"
xl = low_consts.index.get_level_values(1) + "\n(" + low_consts.index.get_level_values(0) + ")"

# the xticks are re-written accordingly to show the desired result
# getting the state-wise data now
states_df = votes_df.groupby("STATE").sum().drop(["VOTER TURNOUT"], axis = 1)
states_df["VOTER TURNOUT"] = round(states_df["TOTAL VOTES"]/states_df["TOTAL ELECTORS"]*100,2)
# necessary arithmetic to calculate the required Voter Turnout of all States
states_turnout = states_df.sort_values(by = "VOTER TURNOUT", ascending = False)
high_stat = states_turnout.head(10)
low_stat = states_turnout.tail(10)
# getting the highest and lowest Voter Outcome States
crime = winners_df[winners_df["CRIMINAL CASES"] != 0]['PARTY'].value_counts()
import pandas as pd
import plotly.graph_objects as go

# Assuming crime is the Series containing party-wise seat counts
threshold = 5  # Define the threshold for grouping parties into "Others"

# Aggregate parties below the threshold into "Others"
crime_grouped = crime.copy()
crime_grouped['Others'] = crime_grouped[crime_grouped < threshold].sum()
crime_grouped = crime_grouped[crime_grouped >= threshold]

# Sort the values in descending order
crime_grouped = crime_grouped.sort_values(ascending=False)
winners_df.insert(11, "NET WORTH", winners_df["ASSETS"] - winners_df["LIABILITIES"])
intervals = [5e6, 1e7, 5e7, 10e7, 25e7, 50e7, 100e7]
# money intervals

assets = winners_df["ASSETS"].sort_values()
liabilities = winners_df["LIABILITIES"].sort_values()
net_worth = winners_df["NET WORTH"].sort_values()
def segregate(intervals, ownings):

    l = []
    l.append(ownings[ownings<=intervals[0]].count())
    for i in range(len(intervals)-1):
        l.append(ownings[(ownings > intervals[i]) & (ownings <= intervals[i+1])].count())
    l.append(ownings[ownings>intervals[i+1]].count())
    return l

data = {"ASSETS" : segregate(intervals, assets),
        "LIABILITIES" : segregate(intervals, liabilities),
        "NET WORTH" : segregate(intervals, net_worth)}
# data generated

worth_df = pd.DataFrame(data, index = ["<=50lac", ">50lac & <=1cr", ">1cr & <=5cr", ">5cr & <=10cr", ">10cr & <=25cr",
                           ">25cr & <=50cr", ">50cr & <=100cr", ">100cr"])
# new dataframe created

worth_df = worth_df.transpose()
# dataframe inverted for visualization purposes
worth_df.reset_index(inplace = True)
# index column added to the DataFrame

st.write('''# General Election 2019 Analysis ''')  
st.sidebar.write('''# General Election Analysis ''')
st.sidebar.image("img.jpeg", width=250 ,use_column_width=False)
with st.sidebar: 
        selected = option_menu("Options", ["Performance of Parties", "Performance in different States", "Seats by Category", 'Voter Turnout',"Election history report","Sentimental Analysis"])

if(selected == 'Performance of Parties'):
        import streamlit as st
        # Example data for the metrics
        num_constituencies = 543
        num_parties = 20
        num_candidates = 8039
        voter_turnout = 65.2
        avg_assets = 2000000
        highest_votes_party = 'Party A'
        highest_votes = 303

        # Set up Streamlit
        st.title("Indian Election Analysis")

        # Define colors for KPI cards
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']  

        # Display KPI cards for various metrics in two separate rows
        row1_col1, row1_col2, row1_col3 = st.columns(3)

        with row1_col1:
            st.markdown(
                f"""
                <div style="background-color:{colors[0]}; padding: 20px; border-radius: 10px;">
                    <h2 style="color:white;">Number of Constituencies</h2>
                    <p style="color:white; font-size:24px;">{num_constituencies}</p>
                    <p style="color:white;">Total number of constituencies in the Lok Sabha.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with row1_col2:
            st.markdown(
                f"""
                <div style="background-color:{colors[1]}; padding: 20px; border-radius: 10px;">
                    <h2 style="color:white;">Number of Parties</h2>
                    <p style="color:white; font-size:24px;">{num_parties}</p>
                    <p style="color:white;">Total number of different parties contesting.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with row1_col3:
            st.markdown(
                f"""
                <div style="background-color:{colors[2]}; padding: 20px; border-radius: 10px;">
                    <h2 style="color:white;">Number of Candidates</h2>
                    <p style="color:white; font-size:24px;">{num_candidates}</p>
                    <p style="color:white;">Total number of candidates participating.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        row2_col1, row2_col2, row2_col3 = st.columns(3)

        with row2_col1:
            st.markdown(
                f"""
                <div style="background-color:{colors[3]}; padding: 20px; border-radius: 10px;">
                    <h2 style="color:white;">Voter Turnout</h2>
                    <p style="color:white; font-size:24px;">{voter_turnout}%</p>
                    <p style="color:white;">Average voter turnout across constituencies.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with row2_col2:
            st.markdown(
                f"""
                <div style="background-color:{colors[4]}; padding: 20px; border-radius: 10px;">
                    <h2 style="color:white;">Average Assets</h2>
                    <p style="color:white; font-size:24px;">₹{avg_assets:,}</p>
                    <p style="color:white;">Average assets of contesting candidates.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        with row2_col3:
            st.markdown(
                f"""
                <div style="background-color:{colors[5]}; padding: 20px; border-radius: 10px;">
                    <h2 style="color:white;">Highest Votes Obtained</h2>
                    <p style="color:white; font-size:24px;">{highest_votes}</p>
                    <p style="color:white;">The highest number of votes obtained by any party.</p>
                </div>
                """,
                unsafe_allow_html=True
            )

        csv_file_path = 'lok Shabha Result 2019.csv'
        df = pd.read_csv(csv_file_path)
        df['Constituency Name'] = df['Constituency Name'].str.lower()
        geojson_file = 'india_pc_2019_simplified.geojson'
        gdf = gpd.read_file(geojson_file)
        gdf['pc_name'] = gdf['pc_name'].str.lower()
        merged_data = pd.merge(gdf, df, left_on='pc_name', right_on='Constituency Name', how='left')

        merged_data['Party'].fillna('BJP', inplace=True)

        # Define color palette
        color_palette = {
            'BJP': '#F47216',  # Assigning saffron color to BJP
            'INC': '#008000'   # Assigning green color to INC
            # Add more party-color mappings as needed
        }

        # Generate random colors for parties not in the color palette
        random_colors = px.colors.qualitative.Light24

        # Create a function to map parties to colors
        def assign_color(party):
            if party in color_palette:
                return color_palette[party]
            else:
                # Assign random color
                return random_colors[hash(party) % len(random_colors)]

        # Apply color mapping to the 'Party' column
        merged_data['Party_Color'] = merged_data.apply(lambda x: assign_color(x['Party']), axis=1)

        # Create choropleth map
        fig = px.choropleth(merged_data,
                            geojson=gdf.geometry,  # replace gdf with your GeoDataFrame
                            locations=merged_data.index,
                            color='Party',
                            hover_name='pc_name',
                            hover_data={'Party': True, 'Winning Margin %': True},
                            title='Indian General Elections 2019',
                            color_discrete_map=color_palette  
                            )

        # # Update layout to cover the whole screen
        fig.update_layout(
            autosize=True,
            width=900,  
            height=500, 
            legend_title='Party'
        )

        # Update layout
        fig.update_geos(fitbounds="locations", visible=False)

        # Show the interactive plot
        st.plotly_chart(fig)

        




        import plotly.express as px

        st.title('Type of chart')
        selected_option = st.selectbox('Select a Chart', ['Pie Chart', 'Bar Chart', 'Tree Map'])
        
        if selected_option == 'Pie Chart':
            fig = px.pie(df_all_party_seats, values='Count', names='Party',
                hover_data=['Count', 'Percentage'],
                title='Distribution of Winners by Party',
                color_discrete_sequence=px.colors.qualitative.Pastel)

            st.plotly_chart(fig)
        
        if selected_option == 'Bar Chart':
            fig = px.bar(df_all_party_seats, x='Party', y='Count', color='Party', color_discrete_sequence=colors,
                        hover_data={'Count': True, 'Party': False},
                        title='Distribution of Winners by Party',
                        labels={'Count': 'Seat Count', 'Party': 'Party'})

            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)


        if selected_option == 'Tree Map':
            fig = px.treemap(df_all_party_seats, path=['Party'], values='Count',
                 color='Count', color_continuous_scale='RdBu',
                 title='Seat Distribution by Party',
                 hover_data={'Count': True, 'Party': False})

            # Update layout for better visibility
            fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

            st.plotly_chart(fig)
        data = pd.read_csv("lok Shabha Result 2019.csv")
        party_stats = data.groupby('Party').agg({'Total Electors': 'sum',
                                        'Valid Votes': 'sum',
                                        'Candidate Name': 'count'}).reset_index()

        # Plot the stacked bar chart using Plotly
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=party_stats['Party'],
            x=party_stats['Total Electors'],
            name='Total Electors',
            orientation='h',
            marker=dict(color='steelblue')
        ))

        fig.add_trace(go.Bar(
            y=party_stats['Party'],
            x=party_stats['Valid Votes'],
            name='Valid Votes',
            orientation='h',
            marker=dict(color='darkorange')
        ))

        fig.add_trace(go.Bar(
            y=party_stats['Party'],
            x=party_stats['Candidate Name'],
            name='Candidate Count',
            orientation='h',
            marker=dict(color='forestgreen')
        ))

        fig.update_layout(
            barmode='stack',
            title='Party-wise Analysis of Total Electors, Valid Votes, and Candidate Count',
            xaxis_title='Count',
            yaxis_title='Party',
            template='plotly_dark',
            width=900,
            height=600
        )

        st.plotly_chart(fig)

if(selected == "Performance in different States"):
    
    data = pd.read_csv("lok Shabha Result 2019.csv")
    
    # Define the function to plot winning party for each state
    def plot_winning_party(state_name):
        state_data = data[data['State Name'] == state_name]
        winning_party = state_data['Party'].value_counts().reset_index()
        winning_party.columns = ['Party', 'Constituencies']
        fig = px.bar(winning_party, x='Party', y='Constituencies', title=f'Winning Party in {state_name}',color='Party')
        fig.update_xaxes(title='Party')
        fig.update_yaxes(title='Number of Constituencies')
        st.plotly_chart(fig)

    # Define the function to plot winning party for each state as a pie chart
    def plot_winning_party_pie(state_name):
        state_data = data[data['State Name'] == state_name]
        winning_party = state_data['Party'].value_counts().reset_index()
        winning_party.columns = ['Party', 'Constituencies']
        fig = px.pie(winning_party, values='Constituencies', names='Party', title=f'Winning Party in {state_name}')
        st.plotly_chart(fig)

    # Define the function to plot voter turnout for each constituency in a state
    def plot_voter_turnout(state_name):
        state_data = data[data['State Name'] == state_name]
        fig = px.scatter(state_data, x='Turnout %', y='Constituency Name',
                        title=f'Voter Turnout in {state_name}',
                        labels={'Turnout %': 'Voter Turnout (%)'},
                        hover_data={'Constituency Name': True, 'Turnout %': ':.2f', 'Party': True},
                        color = "Party")
        st.plotly_chart(fig)

    # Define the function to plot winning percentage for each constituency in a state
    def plot_winning_percentage(state_name):
        state_data = data[data['State Name'] == state_name]
        fig = px.scatter(state_data, x='Candidate Vote Share %', y='Constituency Name',
                        title=f'Winning Percentage in {state_name}',
                        labels={'Candidate Vote Share %': 'Winning Percentage (%)'},
                        hover_data={'Constituency Name': True, 'Candidate Vote Share %': ':.2f', 'Party': True},
                        color="Party")
        st.plotly_chart(fig)


    
    title = st.text_input('Enter the name of state', 'Maharashtra')



    plot_type = st.radio("Select Plot Type", ["Bar Chart","Pie Chart"])
    if plot_type == "Bar Chart":
        plot_winning_party(title)
    if plot_type == "Pie Chart":
        plot_winning_party_pie(title)
    plot_voter_turnout(title)
    plot_winning_percentage(title)

    data['State Name'] = data['State Name'].str.lower()
    
    geojson_file = 'india_pc_2019_simplified.geojson'
    gdf = gpd.read_file(geojson_file)


    gdf['st_name'] = gdf['st_name'].str.lower()

    # Merge data
    merged_data = gdf.merge(data, left_on='st_name', right_on='State Name')


if(selected == 'Seats by Category'):
    import streamlit as st
    import plotly.graph_objects as go
    st.title('Distribution of Seats by Category')
    category = st.selectbox('Select a category', ['Age', 'Caste','Gender','Educational Qualification','Crime','Assets and Liabilities'])
    if category == 'Age':   
        option = st.selectbox('Select an option', ['Candidates Contested', 'Candidates Won'])

        # Create histogram for candidates contested
        if option == 'Candidates Contested':
            histogram_data = candidates_personal_df['AGE']
            histogram_name = 'Candidates Contested'
            histogram_color = 'indigo'
            # Calculate statistics
            mean_age = round(histogram_data.mean(), 2)
            median_age = histogram_data.median()
            min_age = histogram_data.min()
            max_age = histogram_data.max()
        # Create histogram for candidates who won
        else:
            histogram_data = winners_df['AGE']
            histogram_name = 'Candidates Won'
            histogram_color = 'lightgreen'
            # Calculate statistics
            mean_age = round(histogram_data.mean(), 2)
            median_age = histogram_data.median()
            min_age = histogram_data.min()
            max_age = histogram_data.max()

        # Create the histogram
        histogram = go.Histogram(
            x=histogram_data,
            name=histogram_name,
            marker_color=histogram_color,
            opacity=0.5
        )

        # Define layout
        layout = go.Layout(
            title='Age of Candidates Contested and Won',
            xaxis=dict(title='Age', tickfont=dict(size=15)),
            yaxis=dict(title='Number of candidates', tickfont=dict(size=15)),
            legend=dict(font=dict(size=15)),
            bargap=0.1
        )

        # Combine histogram and layout into a figure
        fig = go.Figure(data=[histogram], layout=layout)

        # Add annotations for statistics
        fig.add_annotation(
            x=mean_age,
            y=50,
            text=f"Mean Age: {mean_age}",
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-40
        )

        fig.add_annotation(
            x=median_age,
            y=50,
            text=f"Median Age: {median_age}",
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-60
        )

        fig.add_annotation(
            x=min_age,
            y=50,
            text=f"Min Age: {min_age}",
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-80
        )

        fig.add_annotation(
            x=max_age,
            y=50,
            text=f"Max Age: {max_age}",
            showarrow=True,
            arrowhead=7,
            ax=0,
            ay=-100
        )

        # Show the plot in Streamlit
        st.plotly_chart(fig)

        st.title('Distribution of Age among Candidates')

        # Combine the age data from candidates who contested and candidates who won
        all_candidates_age = pd.concat([candidates_personal_df['AGE'], winners_df['AGE']], axis=1)
        all_candidates_age.columns = ['Contested', 'Won']

        # Dropdown to select between contestants and winners
        option = st.selectbox('Select an option', ['Contested', 'Won'])

        # Create a box plot using Plotly
        fig = px.box(all_candidates_age, y=option, points="all", title="Distribution of Age among Candidates",
                    labels={'value': 'Age', 'variable': 'Status'},
                    template='plotly_white')

        # Customize layout
        fig.update_layout(xaxis=dict(title='Status', tickfont=dict(size=15)),
                        yaxis=dict(title='Age', tickfont=dict(size=15)),
                        legend=dict(font=dict(size=15)))

        # Show the plot in Streamlit
        st.plotly_chart(fig)
        st.title('Distribution of Candidates\' Ages by Age Group and Status')

        # Create a stacked bar plot using Plotly
        fig = px.bar(melted_age_group_counts, x='Age Group', y='Number of Candidates', color='Status', barmode='stack',
                    title='Distribution of Candidates\' Ages by Age Group and Status',
                    labels={'Number of Candidates': 'Number of Candidates', 'Age Group': 'Age Group'})

        # Customize layout
        fig.update_layout(xaxis=dict(title='Age Group', tickfont=dict(size=12)),
                        yaxis=dict(title='Number of Candidates', tickfont=dict(size=12)),
                        legend=dict(title='Status', font=dict(size=12)))

        # Show the plot in Streamlit
        st.plotly_chart(fig)
    if category == 'Caste':
        fig = px.pie(seat_category_df, values='Seats', names='Category',
                title='Distribution of Seats by Category',
                labels={'Seats': 'Seats', 'Category': 'Category'},
                color_discrete_sequence=px.colors.qualitative.Set2)

        # Customize layout
        fig.update_traces(textposition='inside', textinfo='percent+label')

        st.plotly_chart(fig)

        seat_category_df['Proportion'] = seat_category_df['Seats'] / seat_category_df['Seats'].sum()

        # Create a treemap using Plotly
        fig = px.treemap(seat_category_df, path=['Category'], values='Proportion',
                        title='Distribution of Seats by Category (Treemap)',
                        color='Category',
                        color_discrete_sequence=px.colors.qualitative.Set2)

        # Customize layout
        fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))

        st.plotly_chart(fig)
    if category == 'Gender':
            st.title('Candidate Gender Analysis')
            # Create a donut plot to represent the percentage breakdown of candidates by gender
            fig1 = go.Figure(data=[go.Pie(labels=candidates_gender_percentage.index, values=candidates_gender_percentage,
                                        hole=.3, marker_colors=['#1f77b4', '#ff7f0e'])])
            fig1.update_layout(title='Percentage Breakdown of Candidates by Gender')

            # Show the donut plot in Streamlit
            st.plotly_chart(fig1)

            # Create a stacked bar plot to show the distribution of winning and losing candidates within each gender category
            fig2 = px.bar(gender_group, barmode='stack',
                        title='Distribution of Candidates by Gender and Status',
                        labels={'value': 'Number of Candidates', 'GENDER': 'Gender'},
                        color_discrete_sequence=['#1f77b4', '#ff7f0e'])

            # Customize layout of the stacked bar plot
            fig2.update_layout(xaxis=dict(title='Gender'),
                            yaxis=dict(title='Number of Candidates'),
                            legend_title='Status')

            # Add annotations for percentages and information
            for gender, percentage_contested, percentage_won in zip(candidates_gender_percentage.index, candidates_gender_percentage, winners_gender_percentage):
                fig2.add_annotation(x=gender, y=gender_group.loc[gender].sum(), text=f"{percentage_contested}% candidates contested",
                                    font=dict(size=10), showarrow=False)
                fig2.add_annotation(x=gender, y=0, text=f"{percentage_won}% candidates won",
                                    font=dict(size=10), showarrow=False)

            # Show the stacked bar plot in Streamlit
            st.plotly_chart(fig2)
    if category == 'Educational Qualification':
            st.title('Educational Qualifications of Winners')
            # Create a bar plot using Plotly with individual colors for each bar
            fig = px.bar(x=education.index, y=education.values,
                        labels={'x': 'Education Status', 'y': 'No. of Candidates'},
                        title='EDUCATIONAL QUALIFICATIONS OF WINNERS',
                        color_discrete_sequence=px.colors.qualitative.Plotly)

            # Customize layout
            fig.update_layout(xaxis=dict(title='Education Status', tickangle=60),
                            yaxis=dict(title='No. of Candidates'),
                            title_font_size=18)

            # Show the plot in Streamlit
            st.plotly_chart(fig)

            fig = px.pie(names=education.index, values=education.values,
             title='Educational Qualifications of Candidates')

            # Customize layout
            fig.update_traces(textinfo='percent+label')

            st.plotly_chart(fig)

            import plotly.graph_objects as go
            import numpy as np

            # Define the categories and values for the radar chart
            categories = education.index
            values = education.values

            # Normalize the values to range between 0 and 1
            max_value = max(values)
            normalized_values = [v / max_value for v in values]

            # Create the radar chart using Plotly
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=normalized_values,
                theta=categories,
                fill='toself',
                name='Education Qualifications'
            ))

            # Update layout
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]  # Adjust the range as needed
                    )),
                showlegend=False,
                title='Educational Qualifications of Candidates (Radar Chart)'
            )

            st.plotly_chart(fig)
            import plotly.graph_objects as go
            # Create the grouped bar chart using Plotly
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=categories,
                y=values_male,
                name='Male',
                marker_color='rgb(31, 119, 180)'
            ))

            fig.add_trace(go.Bar(
                x=categories,
                y=values_female,
                name='Female',
                marker_color='rgb(255, 127, 14)'
            ))

            # Update layout
            fig.update_layout(
                barmode='group',
                xaxis=dict(title='Education Qualifications'),
                yaxis=dict(title='Number of Candidates'),
                title='Educational Qualifications of Candidates by Gender (Grouped Bar Chart)'
            )

            # Show the plot
            st.plotly_chart(fig)
            # Create a bar plot using Plotly
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=education.index,
                y=education.values,
                marker_color='rgb(31, 119, 180)'  # Set the color of the bars
            ))

            # Update layout
            fig.update_layout(
                xaxis=dict(title='Education Status', tickangle=45),  # Rotate x-axis labels for better readability
                yaxis=dict(title='No. of Candidates'),
                title='Educational Qualifications of Winners',
                title_font=dict(size=18),
            )

            # Add hover information
            fig.update_traces(
                hoverinfo='y+text',
                text=education.values,
            )
            st.plotly_chart(fig)

    if category == "Crime":
        st.title('Crime Analysis')
        fig = go.Figure()
        fig.add_trace(go.Bar(x=crime_grouped.index, y=crime_grouped.values))

        # Update layout
        fig.update_layout(
            title='Distribution of Crime Cases by Party',
            xaxis_title='Party',
            yaxis_title='Number of Crime Cases',
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig)

    if category == "Assets and Liabilities":
        st.title('Analysis According to assets')
        import plotly.graph_objects as go

        # Create a Plotly figure
        fig = go.Figure()

        # Add bar traces for each category
        fig.add_trace(go.Bar(x=worth_df['index'], y=worth_df['<=50lac'], name='<=50lac', marker_color='rgb(31, 119, 180)'))
        fig.add_trace(go.Bar(x=worth_df['index'], y=worth_df['>50lac & <=1cr'], name='>50lac & <=1cr', marker_color='rgb(255, 127, 14)'))
        fig.add_trace(go.Bar(x=worth_df['index'], y=worth_df['>1cr & <=5cr'], name='>1cr & <=5cr', marker_color='rgb(44, 160, 44)'))
        fig.add_trace(go.Bar(x=worth_df['index'], y=worth_df['>5cr & <=10cr'], name='>5cr & <=10cr', marker_color='rgb(214, 39, 40)'))
        fig.add_trace(go.Bar(x=worth_df['index'], y=worth_df['>10cr & <=25cr'], name='>10cr & <=25cr', marker_color='rgb(148, 103, 189)'))
        fig.add_trace(go.Bar(x=worth_df['index'], y=worth_df['>25cr & <=50cr'], name='>25cr & <=50cr', marker_color='rgb(140, 86, 75)'))
        fig.add_trace(go.Bar(x=worth_df['index'], y=worth_df['>50cr & <=100cr'], name='>50cr & <=100cr', marker_color='rgb(227, 119, 194)'))
        fig.add_trace(go.Bar(x=worth_df['index'], y=worth_df['>100cr'], name='>100cr', marker_color='rgb(127, 127, 127)'))

        # Update layout
        fig.update_layout(
            barmode='stack',
            title="DISTRIBUTION OF ASSETS, LIABILITIES AND NET WORTH OF ALL WINNING CANDIDATES",
            xaxis=dict(title=None, tickangle=0),
            yaxis=dict(title="No. of Candidates", titlefont_size=15, tickfont_size=14),
            legend=dict(font=dict(size=13.5)),
            width=600,
            height=900,
        )

        st.plotly_chart(fig)



if selected == 'Voter Turnout':
    st.title('Voter Turnout Analysis')

    # Dropdown to select the viewing option
    analysis_option = st.selectbox('Select Viewing Option', ['By State', 'By Constituency'])

    if analysis_option == 'By State':
        # Code for analyzing voter turnout by state
        order_option = st.selectbox('Select Viewing Option', ['Highest', 'Lowest'])
        if order_option == 'Highest':
            # Code for displaying highest state voter turnout
            fig1 = go.Figure(go.Scatter(
                x=high_stat.index,
                y=high_stat["VOTER TURNOUT"],
                mode='lines+markers',
                name='Highest State Voter Turnout',
                line=dict(color='blue', width=2),
                marker=dict(color='blue', size=10)
            ))
            fig1.update_layout(
                title='Highest State Voter Turnout',
                xaxis=dict(title='States', tickangle=45),
                yaxis=dict(title='Voter Turnout (%)'),
                title_font=dict(size=18),
            )
            st.plotly_chart(fig1)
            fig1 = go.Figure(go.Bar(
                x=high_stat.index,
                y=high_stat['VOTER TURNOUT'],
                marker_color='blue',
                name='Highest State Voter Turnout'
            ))
            fig1.update_layout(
                title='Highest State Voter Turnout',
                xaxis=dict(title='States', tickangle=45),
                yaxis=dict(title='Voter Turnout (%)', range = [76,84]),
                title_font=dict(size=18),
            )

            st.plotly_chart(fig1)

        elif order_option == 'Lowest':
            # Code for displaying lowest state voter turnout
            fig1 = go.Figure(go.Scatter(
                x=low_stat.index,
                y=low_stat["VOTER TURNOUT"],
                mode='lines+markers',
                name='Lowest State Voter Turnout',
                line=dict(color='blue', width=2),
                marker=dict(color='blue', size=10)
            ))
            fig1.update_layout(
                title='Lowest State Voter Turnout',
                xaxis=dict(title='States', tickangle=45),
                yaxis=dict(title='Voter Turnout (%)'),
                title_font=dict(size=18),
            )
            st.plotly_chart(fig1)

            fig1 = go.Figure(go.Bar(
                x=low_stat.index,
                y=low_stat['VOTER TURNOUT'],
                marker_color='blue',
                name='Lowest State Voter Turnout'
            ))
            fig1.update_layout(
                title='Lowest State Voter Turnout',
                xaxis=dict(title='States', tickangle=45),
                yaxis=dict(title='Voter Turnout (%)', range = [42,64]),
                title_font=dict(size=18),
            )

            st.plotly_chart(fig1)

    elif analysis_option == 'By Constituency':
        # Code for analyzing voter turnout by constituency
        order_option = st.selectbox('Select Viewing Option', ['Highest', 'Lowest'])
        if order_option == 'Highest':
            # Code for displaying highest constituency voter turnout
            fig3 = go.Figure(go.Scatter(
                x=xh,
                y=high_consts["VOTER TURNOUT"],
                mode='lines+markers',
                name='Highest Constituency Voter Turnout',
                line=dict(color='green', width=2),
                marker=dict(color='green', size=10)
            ))
            fig3.update_layout(
                title='Highest Constituency Voter Turnout',
                xaxis=dict(title='Constituencies', tickangle=45),
                yaxis=dict(title='Voter Turnout (%)'),
                title_font=dict(size=18),
            )
            st.plotly_chart(fig3)
            fig3 = go.Figure(go.Bar(
                    x=xh,
                    y=high_consts["VOTER TURNOUT"],
                    name='Highest Constituency Voter Turnout',
                    marker_color = 'green'
                ))
            fig3.update_layout(
                title='Highest Constituency Voter Turnout',
                xaxis=dict(title='Constituencies', tickangle=45),
                yaxis=dict(title='Voter Turnout (%)', range = [83,85]),
                title_font=dict(size=18),
            )
            st.plotly_chart(fig3)

        elif order_option == "Lowest":
            # Code for displaying lowest constituency voter turnout
            fig3 = go.Figure(go.Scatter(
                x=xh,
                y=low_consts["VOTER TURNOUT"],
                mode='lines+markers',
                name='Lowest Constituency Voter Turnout',
                line=dict(color='green', width=2),
                marker=dict(color='green', size=10)
            ))
            fig3.update_layout(
                title='Lowest Constituency Voter Turnout',
                xaxis=dict(title='Constituencies', tickangle=45),
                yaxis=dict(title='Voter Turnout (%)'),
                title_font=dict(size=18),
            )
            st.plotly_chart(fig3)
            fig3 = go.Figure(go.Bar(
                    x=xh,
                    y=low_consts["VOTER TURNOUT"],
                    name='Lowest Constituency Voter Turnout',
                    marker_color = 'green'
                ))
            fig3.update_layout(
                title='Lowest Constituency Voter Turnout',
                xaxis=dict(title='Constituencies', tickangle=45),
                yaxis=dict(title='Voter Turnout (%)', range = [8,47]),
                title_font=dict(size=18),
            )
            st.plotly_chart(fig3)
    data = pd.read_csv("lok Shabha Result 2019.csv")
    fig = px.scatter(data, x='Turnout %', y='Winning Margin %',
                 color='Party',
                 hover_name='Candidate Name',
                 hover_data=['State Name', 'Constituency Name'],
                 title='Turnout vs Winning Margin by Party',
                 labels={'Turnout %': 'Turnout (%)', 'Winning Margin %': 'Winning Margin (%)'},
                 template='plotly_dark',
                 opacity=0.7,
                 width=900,
                 height=600)

    # Customize layout
    fig.update_layout(
        legend_title='Party',
        legend_traceorder='reversed',
        hoverlabel=dict(font_size=10),
        hovermode='closest'
    )

    st.plotly_chart(fig)

    party_stats = data.groupby('Party').agg({'Turnout %': 'mean', 'Winning Margin %': 'mean'}).reset_index()

    # Plot the bar chart using Plotly
    fig = px.bar(party_stats, y='Party', x=['Turnout %', 'Winning Margin %'],
                barmode='group',
                title='Average Turnout and Winning Margin by Party',
                labels={'value': 'Percentage', 'variable': 'Metric', 'Party': 'Party'},
                template='plotly_dark',
                width=800,
                height=1000)

    # Customize layout
    fig.update_layout(
        yaxis=dict(tickformat=".2%"),
        legend_title='Metric',
        hoverlabel=dict(font_size=10),
    )

    st.plotly_chart(fig)

if selected == 'Election history report':
    df = pd.read_csv("Loksabha_1962-2019 .csv")
    df.head()
    import pandas as pd
    import plotly.graph_objs as go

    # Replace non-numeric values in 'Turnout' column with NaN
    df['Turnout'] = pd.to_numeric(df['Turnout'].str.replace('%', ''), errors='coerce')

    # Group by 'year' and calculate average turnout for each year
    average_turnout_by_year = df.groupby('year')['Turnout'].mean().reset_index()

    # Create a line graph using Plotly
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=average_turnout_by_year['year'],
                            y=average_turnout_by_year['Turnout'],
                            mode='lines+markers',
                            name='Average Turnout Percentage'))

    # Update layout
    fig.update_layout(title='Average Voter Turnout Percentage by Year',
                    xaxis_title='Year',
                    yaxis_title='Voter Turnout Percentage',
                    hovermode='closest')

    # Show plot
    st.plotly_chart(fig)

    # fig = go.Figure()

    # # Add stacked bars for each year
    # for i, year in enumerate(average_turnout_by_year['year']):
    #     fig.add_trace(go.Bar(
    #         x=[year],
    #         y=[average_turnout_by_year.loc[i, 'Turnout']],
    #         name=str(year)
    #     ))

    # # Update layout
    # fig.update_layout(
    #     title='Average Voter Turnout Percentage by Year',
    #     xaxis_title='Year',
    #     yaxis_title='Voter Turnout Percentage',
    #     barmode='stack'  # Stacked bar chart mode
    # )
    
    # st.plotly_chart(fig)



    # Group by year and party to calculate seats won by each party in each year
    party_seats = df.groupby(['year', 'party']).size().reset_index(name='seats')

    # Get the top 5 parties in terms of total seats won across all years
    top_parties = party_seats.groupby('party')['seats'].sum().nlargest(7).index.tolist()

    # Filter the dataset to include only the top 5 parties
    top_party_data = party_seats[party_seats['party'].isin(top_parties)]

    # Plot the line graph
    fig = px.line(top_party_data, x='year', y='seats', color='party',
                title='Seats Won by Top Parties in Indian Elections (1962-2019)',
                labels={'year': 'Year', 'seats': 'Seats', 'party': 'Party'})
    st.plotly_chart(fig)

    election_year = st.text_input('Enter the year', '2019')
    election_year = int(election_year)
    election_data_year = df[df['year'] == election_year]

    # Group data by party and calculate the total number of seats won by each party
    party_seat_counts = election_data_year['party'].value_counts().reset_index()
    party_seat_counts.columns = ['Party', 'Seats']

    # Sort parties by the number of seats won
    party_seat_counts = party_seat_counts.sort_values(by='Seats', ascending=False)

    # Calculate the percentage of seats won by each party
    party_seat_counts['Percentage'] = (party_seat_counts['Seats'] / party_seat_counts['Seats'].sum()) * 100

    # Create a pie chart
    fig_pie = px.pie(party_seat_counts, values='Seats', names='Party', title=f'Seat Distribution Among Parties in {election_year}')

    # Create a donut chart
    fig_donut = px.pie(party_seat_counts, values='Seats', names='Party', title=f'Seat Distribution Among Parties in {election_year}',
                    hole=0.5)

    # Show both charts
    st.plotly_chart(fig_pie)
    st.plotly_chart(fig_donut)

    election_data_year = df[df['year'] == election_year]

    # Group data by party and calculate the total number of seats won by each party
    party_seat_counts = election_data_year['party'].value_counts().reset_index()
    party_seat_counts.columns = ['Party', 'Seats']

    # Sort parties by the number of seats won
    party_seat_counts = party_seat_counts.sort_values(by='Seats', ascending=False)

    # Create a tree map
    fig_tree_map = px.treemap(party_seat_counts, path=['Party'], values='Seats', title=f'Proportional Representation of Parties in {election_year}')

    # Show the tree map
    st.plotly_chart(fig_tree_map)

    # Filter data for a specific election year, let's say 2019
    election_data_year = df[df['year'] == election_year]

    # Group data by party and calculate the total number of seats won by each party
    party_seat_counts = election_data_year['party'].value_counts().reset_index()
    party_seat_counts.columns = ['Party', 'Seats']

    # Sort parties by the number of seats won
    party_seat_counts = party_seat_counts.sort_values(by='Seats', ascending=False)

    # Create a stacked bar chart
    fig_stacked_bar = px.bar(party_seat_counts, x='Party', y='Seats', title=f'Distribution of Seats Among Parties in {election_year}',
                            labels={'Seats': 'Number of Seats', 'Party': 'Party'},
                            color='Party')

    # Update layout to increase figure size
    fig_stacked_bar.update_layout(
        width=800,  # Set the width of the figure
        height=600,  # Set the height of the figure
    )

    # Show the stacked bar chart
    st.plotly_chart(fig_stacked_bar)

if selected == 'Sentimental Analysis':

    st.subheader("WordCloud for 2024 Ploitical Scenario")

    df = pd.read_csv("LokSabha_Election_2024_Tweets.csv")
    df = df.dropna().reset_index(drop=True)
    text_data = ' '.join(df['text'])

    # wordcloud = WordCloud(width=800, height=800,
    #                     background_color='white',
    #                     stopwords=set(STOPWORDS),
    #                     min_font_size=10).generate(text_data)

    # # Display WordCloud using Streamlit
    # st.title('WordCloud')
    # st.image(wordcloud.to_array(), use_column_width=True)

    # Generate WordCloud
    wordcloud = WordCloud().generate(text_data)

    # Set matplotlib backend to 'Agg' to prevent warning in Streamlit
    plt.switch_backend('Agg')

    # Display the generated image using matplotlib
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()
    # Disable the warning
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()


    st.subheader("Top 20 words based on IDF scores")


    from sklearn.feature_extraction.text import TfidfVectorizer
    import plotly.graph_objects as go

    # Assuming you have loaded your dataset into a DataFrame called df
    text_data = df['text']

    # Create TF-IDF vectorizer
    tfidf_vectorizer = TfidfVectorizer()

    # Fit and transform the text data
    tfidf_matrix = tfidf_vectorizer.fit_transform(text_data)

    # Get feature names (words)
    feature_names = tfidf_vectorizer.get_feature_names_out()

    # Calculate TF-IDF scores
    tfidf_scores = tfidf_matrix.sum(axis=0).A1

    # Create a DataFrame to store word and its corresponding TF-IDF score
    tfidf_df = pd.DataFrame({'word': feature_names, 'tfidf_score': tfidf_scores})

    # Sort DataFrame by TF-IDF score in descending order
    tfidf_df = tfidf_df.sort_values(by='tfidf_score', ascending=False)

    # Plot TF-IDF scores
    fig = go.Figure(go.Bar(
                x=tfidf_df['word'][:20],
                y=tfidf_df['tfidf_score'][:20],
                marker_color='skyblue'
    ))

    fig.update_layout(
                    xaxis_title='Word',
                    yaxis_title='TF-IDF Score')

    st.plotly_chart(fig)


    st.subheader("WordCloud for Top Leaders")

    df_Modi = pd.read_csv("Narendra Modi_data.csv")
    df_Rahul = pd.read_csv("Rahul Gandhi_data.csv")
    df_ak = pd.read_csv("Arvind Kejriwal_data.csv")

    # for Modi's tweets
    df_Modi['Tweet'] = df_Modi['Tweet'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))

    # for Rahul's tweets
    df_Rahul['Tweet'] = df_Rahul['Tweet'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))

    # for Kejriwal's tweets
    df_Rahul['Tweet'] = df_Rahul['Tweet'].apply(lambda x: ' '.join([word for word in x.split() if word not in (stop)]))

    # Generate word cloud for Modi's tweets
    modi_tweets = ' '.join(df_Modi['Tweet'])
    wordcloud_modi = WordCloud(width = 400, height = 400, 
                background_color ='white', 
                stopwords = stop, 
                min_font_size = 10).generate(modi_tweets)

    # Plot word cloud for Modi
    plt.figure(figsize = (15, 5))
    plt.subplot(1, 3, 1)
    plt.imshow(wordcloud_modi, interpolation='bilinear') 
    plt.axis("off") 
    plt.title("Modi's Tweets")

    # Generate word cloud for Rahul's tweets
    rahul_tweets = ' '.join(df_Rahul['Tweet'])
    wordcloud_rahul = WordCloud(width = 400, height = 400, 
                    background_color ='white', 
                    stopwords = stop, 
                    min_font_size = 10).generate(rahul_tweets)

    # Plot word cloud for Rahul
    plt.subplot(1, 3, 2)
    plt.imshow(wordcloud_rahul, interpolation='bilinear') 
    plt.axis("off") 
    plt.title("Rahul's Tweets")

    # Generate word cloud for Kejriwal's tweets
    kejriwal_tweets = ' '.join(df_ak['Tweet'])
    wordcloud_kejriwal = WordCloud(width = 400, height = 400, 
                    background_color ='white', 
                    stopwords = stop, 
                    min_font_size = 10).generate(kejriwal_tweets)

    # Plot word cloud for Kejriwal
    plt.subplot(1, 3, 3)
    plt.imshow(wordcloud_kejriwal, interpolation='bilinear') 
    plt.axis("off") 
    plt.title("Kejriwal's Tweets")

    plt.tight_layout()
    # Disable the warning
    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
    


    st.subheader("Sentimental Analysis for Top Leaders")

    # Function to perform sentiment analysis
    def get_sentiment(text):
        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0:
            return 'Positive'
        elif analysis.sentiment.polarity == 0:
            return 'Neutral'
        else:
            return 'Negative'

    # Apply sentiment analysis to each politician's tweets
    df_Modi['Sentiment'] = df_Modi['Tweet'].apply(get_sentiment)
    df_Rahul['Sentiment'] = df_Rahul['Tweet'].apply(get_sentiment)
    df_ak['Sentiment'] = df_ak['Tweet'].apply(get_sentiment)

    # Create grouped bar graph
    fig = go.Figure()

    # Add traces for each politician
    fig.add_trace(go.Bar(x=df_Modi['Sentiment'].value_counts().index, y=df_Modi['Sentiment'].value_counts().values, name="Modi"))
    fig.add_trace(go.Bar(x=df_Rahul['Sentiment'].value_counts().index, y=df_Rahul['Sentiment'].value_counts().values, name="Rahul"))
    fig.add_trace(go.Bar(x=df_ak['Sentiment'].value_counts().index, y=df_ak['Sentiment'].value_counts().values, name="Kejriwal"))

    # Update layout
    fig.update_layout(barmode='group', title="Sentiment Distribution of Tweets by Politicians",
                    xaxis_title="Sentiment", yaxis_title="Count")

    # Show plot
    st.plotly_chart(fig)



    st.subheader("Distribution of Sentiment Labels")

    df1 = pd.read_csv("Twitter_Data.csv")
    df1 = df1.sample(n=50000, random_state=42)
    df2 = pd.read_csv("Reddit_Data.csv")
    df2.rename(columns={'clean_comment': 'clean_text'}, inplace=True)
    df2 = df2.sample(n=13000, random_state=42)
    df_merged = pd.concat([df2, df1], ignore_index=True)
    df_merged = df_merged.dropna()

    sentiment_counts = df_merged['category'].value_counts()
    labels = ['Neutral', 'Positive', 'Negative']
    values = [sentiment_counts.get(0, 0), sentiment_counts.get(1, 0), sentiment_counts.get(-1, 0)]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
    fig.update_layout()
    st.plotly_chart(fig)



    st.subheader("Top Positive and Negative Words")

    # Assuming df_merged is your DataFrame containing 'clean_text' and 'category' columns
    positive_texts = ' '.join(df_merged[df_merged['category'] == 1]['clean_text'])
    negative_texts = ' '.join(df_merged[df_merged['category'] == -1]['clean_text'])

    def preprocess_text(text):
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Tokenize words using SpaCy
        doc = nlp(text)
        # Lemmatize and filter out stopwords
        words = [token.lemma_ for token in doc if not token.is_stop]
        return words

    # Preprocess positive and negative texts
    chunk_size = 1000000  # Set the chunk size
    positive_chunks = [positive_texts[i:i+chunk_size] for i in range(0, len(positive_texts), chunk_size)]
    negative_chunks = [negative_texts[i:i+chunk_size] for i in range(0, len(negative_texts), chunk_size)]

    positive_words = []
    negative_words = []

    for chunk in positive_chunks:
        positive_words.extend(preprocess_text(chunk))

    for chunk in negative_chunks:
        negative_words.extend(preprocess_text(chunk))

    # Count word frequencies
    positive_word_freq = Counter(positive_words)
    negative_word_freq = Counter(negative_words)

    # Get top 10 positive and negative words
    top_positive_words = positive_word_freq.most_common(10)
    top_negative_words = negative_word_freq.most_common(10)

    # Extract words and frequencies
    top_positive_words, top_negative_words = zip(*top_positive_words), zip(*top_negative_words)
    positive_words, positive_freq = top_positive_words
    negative_words, negative_freq = top_negative_words

    # Create subplots
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Top Positive Words', 'Top Negative Words'))

    # Add bar traces for positive words
    fig.add_trace(
        go.Bar(x=list(positive_words), y=list(positive_freq), name='Positive', marker_color='green'),
        row=1, col=1
    )

    # Add bar traces for negative words
    fig.add_trace(
        go.Bar(x=list(negative_words), y=list(negative_freq), name='Negative', marker_color='red'),
        row=1, col=2
    )

    # Update layout
    fig.update_layout(title='Top Words by Sentiment', barmode='group')
    fig.update_xaxes(title_text='Word', row=1, col=1)
    fig.update_xaxes(title_text='Word', row=1, col=2)
    fig.update_yaxes(title_text='Frequency', row=1, col=1)
    fig.update_yaxes(title_text='Frequency', row=1, col=2)

    # Show plot
    st.plotly_chart(fig)





