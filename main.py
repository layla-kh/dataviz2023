import json
import pandas as pd
import streamlit as st
import plotly.express as px
import seaborn as sns

# Configurations de la sidebar
with st.sidebar:
    st.write("## SIDEBAR")
    st.write(" --------------- ")

    st.write("## About the author")
    st.write("## Layla Al Khoury - 20200443")
    st.write(" Follow me on LinkedIn")
    st.write("www.linkedin.com/in/laylaalkhoury")
    st.write(" ")
    st.write("#datavz2023efrei")
    st.image("https://www.efrei.fr/wp-content/uploads/2022/01/LOGO_EFREI-PRINT_EFREI-WEB.png", width=100)

# Titre de l'application
st.title('Criminalité en France')

# Importation des données
path = 'data.csv'
df = pd.read_csv(path, delimiter=';')

# Préparation des données
df.dropna()
df.drop_duplicates()
df['LOG'] = df['LOG'].str.replace(',', '.', regex=True).astype(float)
df['LOG'] = df['LOG'].astype(int)
df = df[df['Code.département'].isin(['2A', '2B']) == False]
df.reset_index(drop=True, inplace=True)
df['Code.département'] = df['Code.département'].astype(int)
df['tauxpourmille'] = df['tauxpourmille'].str.replace(',', '.', regex=True).astype(float)
df["tauxpourmille"]=df["tauxpourmille"].astype(int)


# Reformater la colonne "Code.déartement"
def format_departement(departement):
        return str(departement).zfill(2)

# Appliquer la fonction
df['Code.département'] = df['Code.département'].apply(format_departement)



# Créer une nouvelle colonne 'TotalFaits' qui calcule le nombre total de faits par année
df['TotalFaits'] = df.groupby('annee')['faits'].transform('sum')

# Créer un graphique en courbes pour montrer l'évolution du nombre total de faits chaque année
fig = px.line(
    df.drop_duplicates(subset=['annee']),
    x='annee',
    y='TotalFaits',
    title="Évolution du Nombre Total de Faits de Délinquance par Année",
    labels={'annee': 'Année', 'TotalFaits': 'Nombre Total de Faits'},
    line_shape='linear',
    width=800,
    height=400,
)

# Personnaliser l'apparence du graphique
fig.update_layout(
    xaxis_title=None,
    yaxis_title="Nombre Total de Faits",
    showlegend=False,

)

# Afficher le graphique interactif
st.plotly_chart(fig)
st.write("On constate une basse tres importante du nombre de faits de délinquance en 2020, cela est du au confinement et aux restrictions sanitaires")

st.write(" ## Nous allons maintenant nous intéresser à la répartition des faits de délinquance par type de crime ou délit")
# Sélection de l'année
year = st.selectbox("Sélectionner une année", df['annee'].unique())
# Sélection du département
departement = st.selectbox("Sélectionner un département", df['Code.département'].unique())

# Filtrer les données pour l'année et le département sélectionnés
filtered_df = df[(df['annee'] == year) & (df['Code.département'] == departement)]

# Créer un graphique en secteurs pour montrer la répartition des types de crimes et délits
fig = px.pie(
    filtered_df,
    names='classe',  # Utilisez 'classe' pour la répartition des types de crimes
    values='faits',
    title=f"Répartition des Crimes et Délits pour l'Année {year}",
    width=800,
    height=400,
    color='classe',
)

fig.update_layout(showlegend=True)
st.plotly_chart(fig)


# Créer un graphique en barres pour montrer la répartition des types de crimes et délits
fig = px.bar(
    filtered_df,
    x='classe',
    y='faits',
    labels={'classe': 'Type de Crime ou Délit', 'faits': 'Nombre de Faits'},
    width=800,
    height=400,
    color='classe',
)
fig.update_layout(
    xaxis_title=None,
    yaxis_title="Nombre de Faits",
    showlegend=False,

)
st.plotly_chart(fig)


def classe_max_faits(filtered_df):
    max_classe = filtered_df.loc[filtered_df['faits'].idxmax()]['classe']
    max_faits = filtered_df['faits'].max()
    return max_classe, max_faits

max_classe, max_faits = classe_max_faits(filtered_df)
# Appeler la fonction et afficher le résultat

st.write(f"La classe avec le plus de faits est: ")
st.write(f"{max_classe} avec {max_faits} faits dans le département {departement} ")




st.write(" ---------------------------------")

st.write("## Nous allons maintenant nous intéresser à la répartition des faits de délinquance par département")
with open('departements.geojson', 'r') as geojson_file:
    geojson_data = json.load(geojson_file)





st.write("------")
selected_year = st.slider("Sélectionnez une année ", min_value=df['annee'].min(), max_value=df['annee'].max(), value=df['annee'].min())

# Filtrez le DataFrame par année sélectionnée
filtered_df = df[df['annee'] == selected_year]

# Calculez le total de faits pour chaque département pour l'année spécifique
total_by_dept = filtered_df.groupby('Code.département')['faits'].sum().reset_index()
total_by_dept.rename(columns={'faits': 'TotalFaits'}, inplace=True)

# Fusionnez le total calculé avec le DataFrame filtré pour avoir une colonne TotalFaits pour chaque département
filtered_df = pd.merge(filtered_df, total_by_dept, on='Code.département')

# Créez une carte
fig2 = px.choropleth_mapbox(filtered_df,
                            geojson=geojson_data,
                            locations="Code.département",
                            featureidkey="properties.code",
                            color="TotalFaits_y",
                            title=f"Répartition des Crimes et Délits en France en {selected_year}",
                            mapbox_style="open-street-map",
                            center={"lat": 46.6061, "lon": 1.875277},
                            zoom=5.0,
                            color_continuous_scale=["blue", "red"])

fig2.update_geos(projection_type="mercator", visible=False)
fig2.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.plotly_chart(fig2)

#maintenant par tauxpourmille
st.write("## Et par le taux pour mille habitants ")

filtre2 = df[df['annee'] == selected_year]
totaltaux_by_dept = filtered_df.groupby('Code.département')['tauxpourmille'].sum().reset_index()
totaltaux_by_dept.rename(columns={'tauxpourmille': 'Totaltaux'}, inplace=True)
filtre2 = pd.merge(filtered_df, totaltaux_by_dept, on='Code.département')

# Créez une carte
fig3 = px.choropleth_mapbox(filtre2,
                            geojson=geojson_data,
                            locations="Code.département",
                            featureidkey="properties.code",
                            color="Totaltaux",
                            title=f"Répartition des Crimes et Délits en France en {selected_year}",
                            mapbox_style="open-street-map",
                            center={"lat": 46.6061, "lon": 1.875277},
                            zoom=5.0,
                            color_continuous_scale=["blue", "red"])

fig3.update_geos(projection_type="mercator", visible=False)
fig3.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
st.plotly_chart(fig3)



total_taux_by_dept = filtre2.groupby('Code.département')['tauxpourmille'].sum().reset_index()
total_taux_by_dept.rename(columns={'tauxpourmille': 'Totaltaux'}, inplace=True)



top_10_faits = total_by_dept.sort_values(by='TotalFaits', ascending=False).head(10)
st.write("## Les 10 départements avec le plus haut nombre de faits de délinquance sont:")
st.write(top_10_faits)

top_10_taux = total_taux_by_dept.sort_values(by='Totaltaux', ascending=False).head(10)
st.write("## Les 10 départements avec le plus haut taux de délinquance sont:")
st.write(top_10_taux)


top_10_faits_set = set(top_10_faits['Code.département'])
departments_in_top_10_taux_not_in_top_10_faits = top_10_taux[~top_10_taux['Code.département'].isin(top_10_faits_set)]


st.write("Departments dans le top 10 des taux mais pas dans le top 10 des faits :")
st.write(departments_in_top_10_taux_not_in_top_10_faits)


def departement_min_incidents(df, selected_year):
    # Filtrer le DataFrame pour l'année sélectionnée
    year_data = df[df['annee'] == selected_year]

    # Regrouper par classe de crime et département, puis calculer le total des faits
    grouped_data = year_data.groupby(['classe', 'Code.département'])['faits'].sum().reset_index()

    # Pour chaque classe de crime, trouver le département avec le nombre minimum de faits
    min_incidents_departements = grouped_data.groupby(['classe'])['faits'].idxmin()

    # Obtenir les informations complètes des départements avec le minimum de faits pour chaque classe de crime
    min_incidents_data = grouped_data.loc[min_incidents_departements]

    return min_incidents_data


# Obtenez les départements avec le minimum d'incidents pour chaque classe de crime
min_incidents_data = departement_min_incidents(df, selected_year)

# Affichez ces données
st.write("## Départements avec le nombre minimum d'incidents par classe de crime pour l'année choisi sont:")

# Create a bar chart to visualize the departments with the minimum incidents for each class of crime
fig4 = px.bar(min_incidents_data, x='classe', y='faits', color='Code.département',
              title=f"Nombre Minimum de Faits de Délinquance par Classe de Crime pour l'Année {selected_year}")

# Customize the layout of the bar chart
fig4.update_layout(
    xaxis_title="Classe des Crimes et Délits",
    yaxis_title="Nombre de Faits",
)

# Display the bar chart
st.plotly_chart(fig4)
