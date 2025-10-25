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

def remove_dados_duplicados(dataframe):
    print('Removendo dados duplicados ...')
    verifica_dados_duplicados(dataframe)
    dataframe_limpo = dataframe.drop_duplicates()
    print(f'Dados duplicados removidos com sucesso! \nDimensão: {dataframe_limpo.shape}')
    return dataframe_limpo