import os
import pandas as pd
import streamlit as st

# On suppose que ces modules sont disponibles
import func as f
import config as c
from download_data import download_data

#  CONFIGURATION DE LA PAGE 
st.set_page_config(page_title="Winter is Coming", layout="wide")

#  FONCTIONS CACHÉES (CRITIQUE POUR LA VITESSE) 
@st.cache_data
def get_static_data():
    """Charge les données statiques une seule fois."""
    # Vérification et téléchargement unique
    if not os.path.exists(c.DATA_DIR):
        download_data()
    
    # Chargement
    stations = f.load_good_stations_df()
    cities = f.load_cities_with_closest_stations_df()
    return stations, cities

@st.cache_data
def get_weather_data(dep_code, start, end, threshold):
    """Met en cache le traitement lourd des données météo."""
    return f.process_weather_data(
        dep_code,
        local_file=False,
        start_year=start,
        end_year=end,
        completion_rate_threshold=threshold,
    )

# --- INITIALISATION ---
start_year = c.START_YEAR
end_year = c.END_YEAR

# Chargement des données (rapide grâce au cache)
station_df, city_df = get_static_data()

# --- INTERFACE UTILISATEUR ---
st.title("❄ Winter is Coming")
st.markdown("Analyse des jours de gel en France par station météo.")

# Utilisation d'une sidebar pour les contrôles pour aérer la page principale
with st.sidebar:
    st.header("Localisation")
    
    # 1. Recherche améliorée
    # On laisse l'utilisateur taper, par défaut vide
    city_input = st.text_input("Rechercher une ville :", placeholder="Ex: Chamonix")
    
    selected_city_name = None
    selected_city_row = None

    if city_input:
        # Filtre insensible à la casse
        matches = city_df[city_df['name'].str.contains(city_input, case=False, na=False)]
        match_names = matches['name'].unique()
        
        if len(match_names) > 0:
            selected_city_name = st.selectbox("Sélectionnez la ville exacte :", match_names)
            # Récupération propre de la ligne (DataFrame)
            selected_city_row = city_df[city_df['name'] == selected_city_name].iloc[0]
        else:
            st.warning("Aucune ville trouvée.")

# --- AFFICHAGE DES RÉSULTATS ---
if selected_city_row is not None:
    # Extraction propre des variables
    city_name_str = selected_city_row['name']
    num_poste = selected_city_row['closest_station_num_poste']
    station_dep = str(num_poste)[:2] # Sécurisation conversion string
    
    st.divider()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Informations")
        st.write(f"*Ville :* {city_name_str}")
        st.write(f"*Station la plus proche :* {num_poste}")
        st.write(f"*Département :* {station_dep}")

    # Récupération des données météo
    with st.spinner(f'Récupération des données météo pour la station {num_poste}...'):
        try:
            # Appel de la fonction cachée
            full_weather_df = get_weather_data(
                station_dep, 
                start_year, 
                end_year, 
                c.COMPLETION_RATE_THRESHOLD
            )
            
            # Filtrage pour la station spécifique
            df_station = full_weather_df[full_weather_df['station_id'] == num_poste]
            
            if df_station.empty:
                st.error("Données trouvées pour le département, mais pas pour cette station spécifique.")
            else:
                # Calculs statistiques
                station_alti = df_station.iloc[0]['alti']
                mean_frost = f.compute_mean_number_of_frost_days(df_station)
                number_of_frost_days_per_year = f.compute_number_of_frost_days_per_year(df_station)
                frost_per_day = f.compute_frost_days_percentage_per_day(df_station)

                with col1:
                    st.metric("Altitude", f"{station_alti} m")
                    st.metric("Jours de gel (moyenne/an)", f"{mean_frost:.1f}")

                with col2:
                    st.subheader("Tendance annuelle")
                    # Conversion pour affichage propre
                    chart_data = number_of_frost_days_per_year.copy()
                    chart_data['year'] = chart_data['year'].astype(str)
                    st.line_chart(chart_data.set_index('year')['frost_day'], color="#29b5e8")

                st.subheader("Probabilité de gel par jour (Saisonnalité)")
                st.bar_chart(frost_per_day, color="#83c9ff")
                
                with st.expander("Voir les données brutes"):
                    st.dataframe(df_station.head(10))

        except Exception as e:
            st.error(f"Une erreur est survenue lors du traitement des données : {e}")

else:
    st.info("Veuillez rechercher et sélectionner une ville dans le menu latéral pour commencer.")
