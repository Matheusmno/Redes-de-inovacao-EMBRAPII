import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.markdown("""
    <h1 style='text-align: center;'>Redes de inovação EMBRAPII</h1>
""", unsafe_allow_html=True)
# File upload in the main window
uploaded_file = st.file_uploader("Escolha o arquivo Excel 'Tabela Periódica - Excelência Operacional':", type=["xlsx", "xlsm"])

# Check if a file is uploaded
if uploaded_file is not None:
    # Pre processing
    data = pd.read_excel(uploaded_file, sheet_name='Dados', header=1)
    data['Soma das métricas'] = data['Impacto Potencial dos Resultados'] + data['Projetos de PD&I'] + data['Relações com empresas'] + data['QIM ver']
    
    # Sidebar with filters
    st.sidebar.title('Filtros')
    selected_category = st.sidebar.selectbox('Classificação', ["Diamante", "Ouro", "Prata"], index=0)
    sorted_unity = np.sort(data['Unidade EMBRAPII'].dropna().unique())
    selected_unity = st.sidebar.selectbox('Unidade', np.insert(sorted_unity, 0, "Todas", axis=0))
    selected_dimension = st.sidebar.selectbox('Dimensão', ['Impacto Potencial dos Resultados', 'Projetos de PD&I', 'Relações com empresas', 'QIM ver'])
    selected_tematicas = st.sidebar.multiselect('Temática', data['CLASSIFICAÇÃO TEMÁTICA EMBRAPII'].dropna().unique())
    selected_tipoue = st.sidebar.multiselect('Tipo da UE', data['TIPO DE INSTITUIÇÃO'].dropna().unique())

    # Apply filters
    if 'Diamante' in selected_category:
        filtered_data = data[data['Classificação'].isin(['DIAMANTE', 'OURO', 'PRATA', 'BRONZE'])]
    elif 'Ouro' in selected_category:
        filtered_data = data[data['Classificação'].isin(['OURO', 'PRATA', 'BRONZE'])]
    else:
        filtered_data = data[data['Classificação'].isin(['PRATA', 'BRONZE'])]

    if 'Todas' not in selected_unity:
        dimension_value = data.loc[data['Unidade EMBRAPII'] == selected_unity, selected_dimension].values[0]
        filtered_data = filtered_data[filtered_data[selected_dimension] <= dimension_value]

    if selected_tematicas:
        filtered_data = filtered_data[filtered_data['CLASSIFICAÇÃO TEMÁTICA EMBRAPII'].isin(selected_tematicas)]
    if selected_tipoue:
        filtered_data = filtered_data[filtered_data['TIPO DE INSTITUIÇÃO'].isin(selected_tipoue)]

    num_unidades = filtered_data['Unidade EMBRAPII'].count()
    
    if not filtered_data.empty:
        # Create two columns
        #col1, col2 = st.columns(2)
        
        # Scatter Plot
        color_discrete_map = {'DIAMANTE': 'rgb(185,242,255)',
                              'OURO': 'rgb(255,215,0)',
                              'PRATA': 'rgb(192,192,192)',
                              'BRONZE': 'rgb(184,115,51)'}
        fig_scatter = px.scatter_3d(filtered_data, x='Impacto Potencial dos Resultados',
                                    y='Projetos de PD&I',
                                    z='Relações com empresas',
              color='Classificação', size='Soma das métricas',
              color_discrete_map=color_discrete_map,
              hover_name="Unidade EMBRAPII",
              custom_data=['Unidade EMBRAPII'])
        
        hover_template = '%{customdata[0]}'
        fig_scatter.update_traces(hovertemplate=hover_template)
        fig_scatter.update_scenes(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False)
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        # Treemap
        treemap_data = filtered_data.groupby(['Classificação']).size().reset_index(name='Count')
        fig_treemap = px.treemap(treemap_data, path=['Classificação'], values='Count', color='Classificação', color_discrete_map=color_discrete_map)
        st.plotly_chart(fig_treemap, use_container_width=True)

        # Display table with selected columns
        selected_columns_data = filtered_data[['Unidade EMBRAPII', 'CIDADE', 
                                               'TIPO DE INSTITUIÇÃO', 
                                               'CLASSIFICAÇÃO TEMÁTICA EMBRAPII', 'Classificação']]
        st.markdown(selected_columns_data.to_html(index=False, escape=False), unsafe_allow_html=True)
    else:
        st.warning("Não há registros para os filtros selecionados.")

    # Card
    st.sidebar.markdown("""
    <div style="width: 100%; color: rgb(39,100,170); padding: 20px; border-radius: 5px; font-size: 25px;">
    {} <br>
    Unidades EMBRAPII
    </div>
    """.format(num_unidades), unsafe_allow_html=True)

else:
    st.warning("Por favor, faça o upload da última versão do arquivo Excel 'Tabela Periódica - Excelência Operacional'.")