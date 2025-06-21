import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuración de la página
st.set_page_config(
    page_title="Dashboard COVID-19 USA",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título del dashboard
st.title("COVID-19 en Estados Unidos")


# Cargar datos
try:
    df = pd.read_csv("us_covid_data2 (2).csv")  # Intenta en el directorio actual
except FileNotFoundError:
    try:
        # Intenta con la ruta relativa desde GitHub
        df = pd.read_csv("https://github.com/IvanCruzl/Covid-19-Dashboard/blob/main/us_covid_data.csv")
    except Exception as e:
        st.error(f"⚠️ Error al cargar datos: {str(e)}")

# Procesamiento inicial
df['date'] = pd.to_datetime(df['date'])
df['mortality'] = df['deaths'] / df['cases']

# Diccionario de nombre completo a abreviación
state_abbrev = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT',
    'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI',
    'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME',
    'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI',
    'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD',
    'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
    'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY'
}

# Agrega la abreviación
df['state_abbr'] = df['state'].map(state_abbrev)

territorios = ['District of Columbia', 'Puerto Rico', 'Virgin Islands', 'Guam', 'Northern Mariana Islands']

df = df[~df['state'].isin(territorios)]


# Verifica si hay estados no reconocidos
missing_states = df[df['state_abbr'].isna()]['state'].unique()
if len(missing_states) > 0:
    st.warning(f"Estados no reconocidos: {missing_states}")

# Sidebar con filtros
st.sidebar.header("Filtros")
min_date = df['date'].min()
max_date = df['date'].max()

start_date = st.sidebar.date_input("Fecha de inicio", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("Fecha de fin", max_date, min_value=min_date, max_value=max_date)

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

all_states = df['state'].unique()
selected_states = st.sidebar.multiselect("Seleccionar estados", all_states, default=["New York", "California"])
top_n = st.sidebar.slider("Top N estados", 2, 12, 6)

# Aplicar filtros
filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
if selected_states:
    filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]

# Métricas generales
st.subheader("Métricas generales")
col1, col2, col3 = st.columns(3)
total_cases = filtered_df['cases'].sum()
total_deaths = filtered_df['deaths'].sum()
avg_mortality = total_deaths / total_cases if total_cases > 0 else 0

col1.metric("Casos totales", f"{total_cases:,}")
col2.metric("Muertes totales", f"{total_deaths:,}")
col3.metric("Tasa de mortalidad", f"{avg_mortality:.2%}")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Mapas", "Barras y Áreas", "Tendencia Temporal", "Comparativas"])

# === TAB 1 ===
with tab1:
    st.subheader("Visualización geográfica")
    
    st.markdown("**Casos por estado**")
    col1, col2 = st.columns([3, 1]) 
    with col1:
        df_state = filtered_df.groupby("state_abbr", as_index=False)["cases"].sum()
        fig = px.choropleth(
            df_state,
            locations="state_abbr",
            locationmode="USA-states",
            color="cases",
            color_continuous_scale="Greens",
            scope="usa",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: transparent; border: 2px solid #8CB370; padding: 15px; border-radius: 10px; margin-top: 60px;">
            <p style="font-size: 14px;">El mapa muestra el número total de casos por COVID-19 en cada estado de EE.UU.</p>
            <p style="font-size: 12px;">* Se pueden utilizar los filtros de la barra lateral para seleccionar estados o rango de fechas *</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("") 
    
    # Segundo mapa: Tasa de mortalidad
    st.markdown("**Muertes por estado**")
    col3, col4 = st.columns([3, 1])
    
    with col3:
        df_deaths = filtered_df.groupby("state_abbr", as_index=False)["deaths"].sum()
        fig = px.choropleth(
            df_deaths,
            locations="state_abbr",
            locationmode="USA-states",
            color="deaths",
            color_continuous_scale="Reds",
            scope="usa",
            template="plotly_dark"
        )
    
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.markdown("""
        <div style="background-color: transparent; border: 2px solid #DE4D3E; padding: 15px; border-radius: 10px; margin-top: 60px;">
            <p style="font-size: 14px;">Este mapa muestra la cantidad de mertes por COVID-19 en cada estado de EE.UU.</p>
            <p style="font-size: 14px;">* Se pueden utilizar los filtros de la barra lateral para seleccionar estados o rango de fechas *</p>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    st.subheader("Distribución por estado")
    
    # Gráfico de donut - Top estados con más casos
    st.markdown(f"**Top {top_n} estados con más casos**")
    col1, col2 = st.columns([3, 1])  # 3/4 para gráfico, 1/4 para descripción
    
    with col1:
        treemap_df = df.groupby("state", as_index=False)["cases"].sum()
        treemap_top = treemap_df.sort_values("cases", ascending=False).head(top_n)

        # Configuración del gráfico
        pie_config = {
            "labels": treemap_top['state'],
            "values": treemap_top['cases'],
            "hole": 0.4,
            "textinfo": 'label+percent',
            "textposition": 'inside',
            "marker_colors": px.colors.sequential.speed,
            "hovertemplate": "<b>%{label}</b><br>Casos: %{value:,}<br>Porcentaje: %{percent}<extra></extra>",
            "pull": [0.1 if i == 0 else 0 for i in range(len(treemap_top))]
        }

        
        fig = go.Figure(go.Pie(**pie_config))

        # Texto central con salto de línea
        center_text = f"Total:<br>{treemap_top['cases'].sum():,}"

        fig.update_layout(
            template="plotly_dark",
            uniformtext_minsize=12,
            uniformtext_mode='hide',
            # Mover la leyenda para que no tape el gráfico
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.3,  # Más abajo
                xanchor="center",
                x=0.5,
                itemwidth=30,  # Reducir ancho de items
                font=dict(size=10)  # Reducir tamaño de fuente
            ),
            margin=dict(b=100),  # Aumentar margen inferior
            annotations=[dict(
                text=center_text,
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False,
                xanchor='center',
                yanchor='middle'
            )]
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: transparent; border: 2px solid #8CB370; padding: 15px; border-radius: 10px; margin-top: 60px;">
            <p style="font-size: 14px;">Gráfico de dona muestra la distribución de casos entre los {top_n} estados más afectados.</p>
            <p style="font-size: 14px;">El estado con más casos aparece ligeramente destacado.</p>
            <p style="font-size: 14px;">En el centro se muestra el total acumulado de casos para estos estados.</p>
        </div>
        """.format(top_n=top_n), unsafe_allow_html=True)
    
    st.write("")
    
    st.markdown("**Casos y muertes por estado**")
    col3, col4 = st.columns([3, 1])  
    
    with col3:
        stacked_df = filtered_df.groupby("state")[["cases", "deaths"]].sum().reset_index().melt(id_vars="state")

        fig = px.bar(
            stacked_df,
            x="state",
            y="value",
            color="variable",
            template='plotly_dark',
            labels={'value': 'Cantidad', 'state': 'Estado'},
            color_discrete_map={
                'cases': px.colors.sequential.speed[2],
                'deaths': px.colors.sequential.speed[6]
            }
        )

        fig.for_each_trace(lambda t: t.update(
            name=f"{'Casos' if t.name == 'cases' else 'Muertes'} (Total: {total_cases:,})" if t.name == 'cases' else f"{'Casos' if t.name == 'cases' else 'Muertes'} (Total: {total_deaths:,})",
            legendgroup=t.name,
            hovertemplate=f"{'Casos' if t.name == 'cases' else 'Muertes'}: %{{y:,}}<extra></extra>"
        ))

        fig.update_layout(
            barmode="stack",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                # title_text=f"<b>Leyenda</b><br>Casos totales: {total_cases:,}<br>Muertes totales: {total_deaths:,}",
                title_font_size=12,
                font=dict(size=11)
            ),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.markdown("""
        <div style="background-color: transparent; border: solid 2px #DEDB3E; padding: 15px; border-radius: 10px; margin-top: 60px;">
            <p style="font-size: 14px;">Gráfico de barras apiladas que compara casos confirmados y muertes por estado.</p>
        </div>
        """, unsafe_allow_html=True)

# === TAB 3 ===
with tab3:
    st.subheader("Evolución temporal")
    st.markdown("""
        <div style="background-color: transparent; border: solid 2px #FF4B4B; padding: 15px; border-radius: 10px; margin-top: 10px; margin-bottom: 20px;">
            <p style="font-size: 18px;">En este apartado se muestra la evolución en el timpo de los casos y muertes ocasionados por el COVID-19 desde el 21 de enero del 2020 hasta el 5 de diciembre del 2020</p>
        </div>
        """, unsafe_allow_html=True)
    st.write("")


    st.markdown("**Casos y muertes por día**")
    
    time_series = filtered_df.groupby("date")[["cases", "deaths"]].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_series['date'], y=time_series['cases'], name="Casos", line=dict(color='royalblue')))
    fig.add_trace(go.Scatter(x=time_series['date'], y=time_series['deaths'], name="Muertes", line=dict(color='firebrick')))
    fig.update_layout(template="plotly_dark", xaxis_title="Fecha", yaxis_title="Cantidad", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)


    #-------------------------Grafica animada

    st.markdown(f"**Gráfica animada 10 estados con más muertes**")
    df_state = df.groupby(['state', 'date'], as_index=False)['deaths'].sum()
    df_state['cumulative_deaths'] = df_state.groupby('state')['deaths'].cumsum()
    latest_date = df_state['date'].max()
    top_states = (
        df_state[df_state['date'] == latest_date]
        .nlargest(10, 'cumulative_deaths')['state']
        .tolist()
    )
    df_top = df_state[df_state['state'].isin(top_states)]

    fig = px.bar(df_top, 
             x='state', 
             y='cumulative_deaths', 
             animation_frame='date',
             range_y=[0, df_top['cumulative_deaths'].max() * 1.1],
             template='plotly_dark',
             color_discrete_sequence=['#63DE3E'],
             labels = {'cumulativa_deaths': 'Muertes totales','state':'Estados'},
             text_auto=True,
             )

    # Mejorar la animación
    fig.update_traces(textposition = 'inside',textfont_size = 12)
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 250
    fig.update_layout(yaxis_title="Muertes acumuladas", showlegend = False)

    # Mostrar en Streamlit
    st.plotly_chart(fig, use_container_width=True)
    

# === TAB 4 ===
with tab4:
    st.subheader("Comparativas avanzadas")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Comparativa de tasa de mortalidad**")
        mortality_df = filtered_df.groupby("state").apply(
            lambda x: round(x['deaths'].sum() / x['cases'].sum(),4) if x['cases'].sum() > 0 else 0
        ).reset_index(name='mortality')
        mortality_df = mortality_df.sort_values('mortality', ascending=False).head(top_n)

        fig = px.bar(
            mortality_df,
            x='state',
            y='mortality',
            color='state',
            labels={'mortality': 'Tasa de mortalidad', 'state': 'Estado'},
            template="plotly_dark"
        )
        fig.update_layout(yaxis_tickformat=".2%",showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("""
        Muestra el porcentaje de fallecimientos respecto al total de casos confirmados por estado. 
        Los valores más altos indican mayores tasas de mortalidad. 
        """)

    with col2:
        st.markdown("**Relación entre casos y muertes por estado**")
        scatter_df = filtered_df.groupby("state")[["cases", "deaths"]].sum().reset_index()

        fig = px.scatter(
            scatter_df,
            x="cases",
            y="deaths",
            color="state",
            size="cases",
            hover_name="state",
            log_x=True,
            log_y=True,
            template="plotly_dark",
            labels={'cases': 'Casos', 'deaths': 'Muertes'}
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("""
         Comparación en escala logarítmica entre el volumen total de casos y fallecimientos. 
        El tamaño de cada punto representa la magnitud de casos. Estados que se desvían hacia arriba de la 
        diagonal imaginaria tienen tasas de mortalidad más altas que el promedio.
        """)

st.markdown("---")

