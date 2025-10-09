import pandas as pd

def analisa_dados_ausentes(dataframe):    
    dados_ausentes = dataframe.isna().sum()
    total = dataframe.shape[0]
    ausentes = dados_ausentes.reset_index(name="Quantidade")
    ausentes.rename(columns={"index": "variavel_analisada"}, inplace=True)
    ausentes['Percentual'] = (((ausentes['Quantidade'] / total)*100).round(2)).apply(lambda x: f'{x:.1f}%')
    filtro = ausentes['Quantidade'] > 0
    return ausentes[filtro]

def verifica_dados_duplicados(dataframe):
    qtd = dataframe.duplicated().sum()
    print(f'Foram encontrados {qtd} registros duplicados\n')
    print('Prévia dos dados duplicados:')
    filtro = dataframe.duplicated()
    return dataframe[filtro].head(5)

def importa_csv(dataframe_name, separador=";", encoding="utf-8"):
    print(f'Importando o dataframe: {dataframe_name} ...')
    dataframe = pd.read_csv(dataframe_name, sep=separador, encoding=encoding)
    print(f'Dataframe importado com sucesso! \nDimensão: {dataframe.shape}')
    return dataframe

def junta_dataframes(df1, df2, chave, tipo_juncao='inner'):
    df_final = pd.merge(df1, df2, on=chave, how=tipo_juncao)
    print(f'Dataframes unidos com sucesso! \nDimensão: {df_final.shape}')
    return df_final

def remove_dados_duplicados(dataframe):
    print('Removendo dados duplicados ...')
    verifica_dados_duplicados(dataframe)
    dataframe_limpo = dataframe.drop_duplicates()
    print(f'Dados duplicados removidos com sucesso! \nDimensão: {dataframe_limpo.shape}')
    return dataframe_limpo


def exporta_csv(dataframe, nome_arquivo, separador=";", encoding="utf-8", index=False):
    print(f'Exportando o dataframe para o arquivo: {nome_arquivo} ...')
    dataframe.to_csv(nome_arquivo, sep=separador, encoding=encoding, index=index)
    print('Dataframe exportado com sucesso!')