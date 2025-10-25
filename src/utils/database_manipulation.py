import pandas as pd
def importa_csv(dataframe_name, separador=";", encoding="utf-8"):
    print(f'Importando o dataframe: {dataframe_name} ...')
    dataframe = pd.read_csv(dataframe_name, sep=separador, encoding=encoding)
    print(f'Dataframe importado com sucesso! \nDimensão: {dataframe.shape}')
    return dataframe

def junta_dataframes(df1, df2, chave, tipo_juncao='inner'):
    df_final = pd.merge(df1, df2, on=chave, how=tipo_juncao)
    print(f'Dataframes unidos com sucesso! \nDimensão: {df_final.shape}')
    return df_final

def exporta_csv(dataframe, nome_arquivo, separador=";", encoding="utf-8", index=False):
    print(f'Exportando o dataframe para o arquivo: {nome_arquivo} ...')
    dataframe.to_csv(nome_arquivo, sep=separador, encoding=encoding, index=index)
    print('Dataframe exportado com sucesso!')