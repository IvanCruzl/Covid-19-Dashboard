import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Dashboard COVID-19 USA",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("COVID-19 en Estados Unidos")


import pandas as pd
import streamlit as st

try:
    df = pd.read_csv("us_covid_data2 (2).csv")
except FileNotFoundError:
    try:
        github_url = "https://raw.githubusercontent.com/IvanCruzl/Covid-19-Dashboard/main/us_covid_data.csv"
        df = pd.read_csv(github_url)
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        st.stop()  

if 'df' in locals():
    df['date'] = pd.to_datetime(df['date'])
    df['mortality'] = df['deaths'] / df['cases']
else:
    st.warning("No se pudo cargar el DataFrame. Verifica la fuente de datos.")

df['date'] = pd.to_datetime(df['date'])
df['mortality'] = df['deaths'] / df['cases']

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

df['state_abbr'] = df['state'].map(state_abbrev)

territorios = ['District of Columbia', 'Puerto Rico', 'Virgin Islands', 'Guam', 'Northern Mariana Islands']

df = df[~df['state'].isin(territorios)]


missing_states = df[df['state_abbr'].isna()]['state'].unique()
if len(missing_states) > 0:
    st.warning(f"Estados no reconocidos: {missing_states}")

st.sidebar.header("Filtros")
min_date = df['date'].min()
max_date = df['date'].max()

start_date = st.sidebar.date_input("Fecha de inicio", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("Fecha de fin", max_date, min_value=min_date, max_value=max_date)

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

all_states = df['state'].unique()
selected_states = st.sidebar.multiselect("Seleccionar estados", all_states, default=["New York", "California", "Texas"])
top_n = st.sidebar.slider("Top N estados", 2, 12, 6)

filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
if selected_states:
    filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]

st.subheader("Métricas generales")
col1, col2, col3 = st.columns(3)
total_cases = filtered_df['cases'].sum()
total_deaths = filtered_df['deaths'].sum()
avg_mortality = total_deaths / total_cases if total_cases > 0 else 0

col1.metric("Casos totales", f"{total_cases:,}")
col2.metric("Muertes totales", f"{total_deaths:,}")
col3.metric("Tasa de mortalidad", f"{avg_mortality:.2%}")

tab1, tab2, tab3, tab4 = st.tabs(["Mapas", "Barras y Áreas", "Tendencia Temporal", "Comparativas"])

with tab1:
    st.subheader("Visualización geográfica")
    st.markdown("""
    <div style="background-color: transparent; border: 2px solid #DE4D3E; padding: 20px; border-radius: 12px; margin-top: 60px;">
        <p style="font-size: 20px;">
            Al ver el contraste entre los casos y las muertes, se puede calcular una tasa de mortalidad alta de 
            <span style="color: #DE4D3E; font-weight: bold; font-size: 22px;">aproximadamente 3%</span> en solo 6 meses.
        </p>
    </div>
    """, unsafe_allow_html=True)

    
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
            template="plotly_dark",
            labels={"state_abbr": "Estado", "cases": "Casos"}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: transparent; border: 2px solid #8CB370; padding: 15px; border-radius: 10px; margin-top: 60px;">
            <p style="font-size: 14px;">La gráfica muestra un mapa de Estados Unidos, en donde los rangos van desde los 0 hasta los 100 millones aproximadamente, siendo los estados más afectados Texas, California, Florida y Nueva York</p>
            <p style="font-size: 12px;">* Los parámetros que recibe son el dataframe, los estados y los casos *</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.write("") 
    
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
            template="plotly_dark",
            labels={"state_abbr": "Estado", "deaths": "Muertes"}
        )
    
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.markdown("""
        <div style="background-color: transparent; border: 2px solid #DE4D3E; padding: 15px; border-radius: 10px; margin-top: 60px;">
            <p style="font-size: 14px;">Este mapa interactivo representa el impacto territorial de la pandemia de COVID-19 en Estados Unidos, mostrando la distribución geográfica de las muertes confirmadas en un rango de 0 a 5 millones. Los estados más afectados fueron Nueva York, Texas, California, Florida y Nueva Jersey</p>
            <p style="font-size: 12px;">* Los parámetros que recibe son el dataframe, los estados y las muertes *</p>
        </div>
        """, unsafe_allow_html=True)

    


with tab2:
    st.subheader("Distribución por estado")
    
    st.markdown(f"**Top {top_n} estados con más casos**")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        treemap_df = df.groupby("state", as_index=False)["cases"].sum()
        treemap_top = treemap_df.sort_values("cases", ascending=False).head(top_n)

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

        center_text = f"Total:<br>{treemap_top['cases'].sum():,}"

        fig.update_layout(
            template="plotly_dark",
            uniformtext_minsize=12,
            uniformtext_mode='hide',
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.3,
                xanchor="center",
                x=0.5,
                itemwidth=30,  
                font=dict(size=10) 
            ),
            margin=dict(b=100),
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
            <p style="font-size: 14px;">Con esta información podemos determinar que los 5 estados de los que representan el top 10 con más casos ocupan prácticamente el 75% de los datos, esto puede ser explicado ya que estos estados tienen en general mayor densidad de población.p>
            <p style="font-size: 12px;">* Se reciben como parámetros los el dataframe, los estados y los casos *</p>
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
                title_font_size=12,
                font=dict(size=11)
            ),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.markdown("""
        <div style="background-color: transparent; border: solid 2px #DEDB3E; padding: 15px; border-radius: 10px; margin-top: 60px;">
            <p style="font-size: 14px;">En esta gráfica se observan varios volúmenes de casos y de muertes, desde el estado de Wyoming, hasta Nueva York, lo que nos puede dar una idea en proporción como le fue en esos 6 meses a cada uno de los estados. Se puede notar como Nueva York tiene un volumen en proporción a los casos confirmados un poco más grande que el resto de los estados.</p>
            <p style="font-size: 12px;">* Se reciben como parámetros los el dataframe, los estados y los valores numéricos de las muertes y los casos confirmados*</p>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.subheader("Evolución temporal")
    st.markdown("""
    <div style="background-color: transparent; border: solid 2px #FF4B4B; padding: 15px; border-radius: 10px; margin-top: 10px; margin-bottom: 20px;">
        <p style="font-size: 18px;">
            En este apartado se muestra la evolución en el tiempo de los casos y muertes ocasionados por el COVID-19 
            <span style="font-weight: bold; color: #FF4B4B;">desde el 1 de julio del 2020 hasta el 5 de diciembre del 2020</span>.
        </p>
        <p style="font-size: 18px;">
            Se nota cómo hay un 
            <span style="font-weight: bold; color: #FF4B4B;">ligero aceleramiento en la cantidad de casos confirmados</span> 
            a partir del mes de 
            <span style="font-weight: bold; color: #FF4B4B;">noviembre</span>, lo que puede indicar que, gracias a los 
            <span style="font-weight: bold; color: #FF4B4B;">climas más extremos</span>, se hizo una propagación más rápida.
        </p>
    </div>
    """, unsafe_allow_html=True)



    st.markdown("**Casos y muertes por día**")
    
    time_series = filtered_df.groupby("date")[["cases", "deaths"]].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=time_series['date'], y=time_series['cases'], name="Casos", line=dict(color='royalblue')))
    fig.add_trace(go.Scatter(x=time_series['date'], y=time_series['deaths'], name="Muertes", line=dict(color='firebrick')))
    fig.update_layout(template="plotly_dark", xaxis_title="Fecha", yaxis_title="Cantidad", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

    
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
             labels = {'cumulative_deaths': 'Muertes totales','state':'Estados','date':'Fecha'},
             text_auto=True,
             )

    fig.update_traces(textposition = 'inside',textfont_size = 12)
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 250
    fig.update_layout(yaxis_title="Muertes acumuladas", showlegend = False)

    st.plotly_chart(fig, use_container_width=True)
    

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
        Esta visualización muestra el porcentaje de fallecimientos en relación con los casos confirmados de COVID-19 en cada estado. Los estados se ordenan de mayor a menor tasa de letalidad
        """)

    with col2:
        st.markdown("**Relación entre casos y muertes por estado (Top 10 destacados)**")

        scatter_df = filtered_df.groupby("state")[["cases", "deaths"]].sum().reset_index()
        scatter_df['total_impact'] = scatter_df['cases'] + scatter_df['deaths']
        top_states = scatter_df.nlargest(10, 'total_impact')['state'].tolist()
        
        scatter_df['color_group'] = scatter_df['state'].apply(
            lambda x: x if x in top_states else 'Otros estados'
        )
        
        scatter_df = scatter_df.sort_values(by='color_group', ascending=False)
        
        fig = px.scatter(
            scatter_df,
            x="cases",
            y="deaths",
            color="color_group",
            size="cases",
            hover_name="state",
            log_x=True,
            log_y=True,
            template="plotly_dark",
            labels={
                'cases': 'Casos (escala log)',
                'deaths': 'Muertes (escala log)',
                'color_group': 'Estado'
            },
            color_discrete_map={
                'Otros estados': 'rgba(150, 150, 150, 0.3)' 
            },
            category_orders={"color_group": top_states + ['Otros estados']}
        )
        
        fig.update_traces(
            marker=dict(line=dict(width=0.5, color='DarkSlateGray')),
            selector=({'marker.color': 'rgba(150, 150, 150, 0.3)'})
        )
        
        fig.update_layout(
            legend_title_text='Top 10 estados<br>por impacto total',
            hoverlabel=dict(font_size=12),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.5,
                xanchor="center",
                x=0.5
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("""
        Comparación en escala logarítmica. Solo los 10 estados con mayor impacto (casos + muertes) se muestran con colores distintivos. 
        El tamaño de cada punto representa el volumen de casos. Estados sobre la diagonal imaginaria tienen mayor mortalidad relativa.
        """)
st.markdown("---")
st.markdown("""
<div style="display: flex; align-items: center; margin-bottom: 10px;">
    <img src="https://media.licdn.com/dms/image/v2/D4E03AQGD6y3GMhKpGg/profile-displayphoto-shrink_200_200/profile-displayphoto-shrink_200_200/0/1701370531159?e=2147483647&v=beta&t=EJfVA3ZMLGxiUwhIf_i2JUtGC9e64Hte2rWAU25eIF8" 
         style="border-radius: 50%; width: 30px; height: 30px; object-fit: cover; margin-right: 10px;">
    <span>Created by Ivan Cruz</span>
</div>
""", unsafe_allow_html=True)

