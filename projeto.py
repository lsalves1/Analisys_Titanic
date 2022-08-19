
import pandas            as pd
import streamlit         as st
import seaborn           as sns
import matplotlib.pyplot as plt
from io                  import BytesIO

# Set no tema do seaborn para melhorar o visual dos plots
custom_params = {"axes.spines.right": False, "axes.spines.top": False}
sns.set_theme(style="ticks", rc=custom_params)

@st.cache(show_spinner= True, allow_output_mutation=True)
def load_data():
    df = sns.load_dataset('titanic')
    df.drop_duplicates(inplace=True)
    df.reset_index()
    # Removendo colunas que não serão utilizadas na análise
    df.drop(columns=['who','adult_male', 'survived', 'class', 'adult_male','deck','embarked','sibsp'], inplace=True)
    df
    #Para a variável idade, vou colocar o valor da mediana, e para a variável do porto de embarque, vou colocar o valor com maior frequência.
    # age
    age_median = df['age'].median()
    df['age'].fillna(age_median, inplace=True)
    # embarked
    embarked_ = df['embark_town'].value_counts()[0]
    df['embark_town'].fillna(embarked_, inplace=True)
    # Alterar o nome das colunas e das variáveis para que sejam de mais fácil entendimento 
    df.columns = ["Classe","Sexo","Idade","Familiares", "Preço da Passagem","Local de Embarque", "Sobreviveu", "Sozinho"]
    df.reset_index()
    df.info()
    return df

# Função para filtrar baseado na multiseleção de categorias
@st.cache(allow_output_mutation=True)
def multiselect_filter(relatorio, col, selecionados):
    if 'all' in selecionados:
        return relatorio
    else:
        return relatorio[relatorio[col].isin(selecionados)].reset_index(drop=True)

# Função para converter o df para csv
@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# Função para converter o df para excel
@st.cache
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data


def main():
    st.set_page_config(page_title = 'Titanic analisys', \
        page_icon = 'https://static.dw.com/image/59775562_401.jpg',
        layout="wide",
        initial_sidebar_state='expanded'
    )
    st.write('# Titanic analise dos sobreviventes')

    st.write('O Titanic era o maior navio de passageiros em serviço à época, \
    tinha 2208 pessoas a bordo quando atingiu um iceberg por volta de 23h40 \
    (horário no navio)[a] no domingo, 14 de abril de 1912. \
    O naufrágio aconteceu duas horas e quarenta minutos depois, às 02h20 \
    (05h18 GMT) na segunda-feira, 15 de abril, resultando na morte de 1 496 pessoas, \
    transformando-o em um dos desastres marítimos mais mortais.')

    st.markdown("---")
    
    image = 'https://static.dw.com/image/59775562_401.jpg'
    st.sidebar.image(image)

    df_ = load_data()

    titanic = df_.copy()

    st.write('## Antes dos filtros')
    st.write(titanic.head())

    with st.sidebar.form(key='my_form'):

        # SELECIONA O TIPO DE GRÁFICO
        graph_type = st.radio('Tipo de gráfico:', ('Barras', 'Pizza'))
    
        # IDADES
        max_age = int(titanic.Idade.max())
        min_age = int(titanic.Idade.min())
        idades = st.slider(label='Idade', 
                                    min_value = min_age,
                                    max_value = max_age, 
                                    value = (min_age, max_age),
                                    step = 1)

        # QUANTIDADE DE FAMILIARES
        max_fam = int(titanic.Familiares.max())
        min_fam = int(titanic.Familiares.min())
        familiares = st.slider(label='Quantidade de familiares', 
                                    min_value = min_fam,
                                    max_value = max_fam, 
                                    value = (min_fam, max_fam),
                                    step = 1)

        # Preço da passagem
        max_price = int(titanic['Preço da Passagem'].max())
        min_price = int(titanic['Preço da Passagem'].min())
        preco = st.slider(label='Preço da Passagem', 
                                    min_value = min_price,
                                    max_value = max_price, 
                                    value = (min_price, max_price),
                                    step = 1)

        # Local de embarque
        emb_list = titanic['Local de Embarque'].unique().tolist()
        emb_list.append('all')
        emb_selected =  st.multiselect("Local de Embarque", emb_list, ['all'])

        # Sexo
        sex_list = titanic['Sexo'].unique().tolist()
        sex_list.append('all')
        sex_selected =  st.multiselect("Estado civil", sex_list, ['all'])

        # Companhia?
        comp_list = titanic['Sozinho'].unique().tolist()
        comp_list.append('all')
        comp_selected =  st.multiselect("Acompanhado?", comp_list, ['all'])

        # Classe
        classe_list = titanic['Classe'].unique().tolist()
        classe_list.append('all')
        classe =  st.multiselect("Classe", classe_list, ['all'])
                
        # encadeamento de métodos para filtrar a seleção

        titanic = titanic[(titanic['Preço da Passagem'] >= preco[0]) & (titanic['Preço da Passagem'] <= preco[1])]
        titanic = (titanic.query("Idade >= @idades[0] and Idade <= @idades[1] \
                    and Familiares >=@familiares[0] and Familiares <= @familiares[1]") 
                    .pipe(multiselect_filter, 'Local de Embarque', emb_selected)
                    .pipe(multiselect_filter, 'Sexo', sex_selected)
                    .pipe(multiselect_filter, 'Sozinho', comp_selected)
                    .pipe(multiselect_filter, 'Classe', classe)
        )

        submit_button = st.form_submit_button(label='Aplicar')
        
    # Botões de download dos dados filtrados
    st.write('## Após os filtros')
    st.write(titanic.head())
    
    df_xlsx = to_excel(titanic)
    st.download_button(label='📥 Download tabela filtrada em EXCEL',
                        data=df_xlsx ,
                        file_name= 'titanic_filtrado.xlsx')
    st.markdown("---")

    # PLOTS    
    fig, ax = plt.subplots(1, 2, figsize = (5,3))

    df_perc = df_.Sobreviveu.value_counts(normalize = True).to_frame()*100
    df_perc = df_perc.sort_index()
    
    try:
        titanic_perc = titanic.Sobreviveu.value_counts(normalize = True).to_frame()*100
        titanic_perc = titanic_perc.sort_index()
    except:
        st.error('Erro no filtro')
    
    # Botões de download dos dados dos gráficos
    col1, col2 = st.columns(2)

    df_xlsx = to_excel(df_perc)
    col1.write('### Proporção original')
    col1.write(df_perc)
    col1.download_button(label='📥 Download',
                        data=df_xlsx ,
                        file_name= 'titanic_sobrev_original.xlsx')
    
    df_xlsx = to_excel(titanic_perc)
    col2.write('### Proporção da tabela com filtros')
    col2.write(titanic_perc)
    col2.download_button(label='📥 Download',
                        data=df_xlsx ,
                        file_name= 'titanic_sobreviventes.xlsx')
    st.markdown("---")

    st.write('## Proporção de aceite')
    # PLOTS    
    if graph_type == 'Barras':
        sns.barplot(x = df_perc.index, 
                    y = 'Sobreviveu',
                    data = df_perc, 
                    ax = ax[0])
        ax[0].bar_label(ax[0].containers[0])
        ax[0].set_title('Dados brutos',
                        fontweight ="bold")
        
        sns.barplot(x = titanic_perc.index, 
                    y = 'Sobreviveu', 
                    data = titanic_perc, 
                    ax = ax[1])
        ax[1].bar_label(ax[1].containers[0])
        ax[1].set_title('Dados filtrados',
                        fontweight ="bold")
    else:
        df_perc.plot(kind='pie', autopct='%.2f', y='Sobreviveu', ax = ax[0])
        ax[0].set_title('Dados brutos',
                        fontweight ="bold")
        
        titanic_perc.plot(kind='pie', autopct='%.2f', y='Sobreviveu', ax = ax[1])
        ax[1].set_title('Dados filtrados',
                        fontweight ="bold")
    fig.tight_layout()
    st.pyplot(plt)

    
if __name__ == '__main__':
	main()






