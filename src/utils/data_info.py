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



def agrega_anos(df, anos, colunas_agregacao, coluna_agrupamento=['country'], janela_agrupamento=5, primeiro_ano_sozinho=True):
    """
    Agrega várias colunas em janelas que terminam em cada ano de `anos`.
    - df: DataFrame contendo pelo menos colunas coluna_agrupamento e 'year' (int).
    - anos: lista de anos-alvo (ex: [1952, 1957, ...]).
    - colunas_agregacao: lista de nomes de colunas a agregar (ex: ['k','j','L']).
    - coluna_agrupamento: colunas para agrupar (ex: ['country']).
    - janela_agrupamento: tamanho da janela em anos (padrão 5). A janela é [y-janela_agrupamento+1, y].
    - primeiro_ano_sozinho: se True, o menor ano em `anos` usa só ele próprio
      (evita olhar anos anteriores inexistentes). Se False aplica janela completa.
    Retorna DataFrame com coluna_agrupamento + ['year'] + ['<col>_sum' para cada col em colunas_agregacao].
    """
    # cópia local
    df = df.copy()
    if 'year' not in df.columns:
        raise ValueError("DataFrame precisa da coluna 'year'.")
    # garantir year inteiro
    df['year'] = df['year'].astype(int)

    # validar colunas pedidas
    missing = [c for c in colunas_agregacao if c not in df.columns]
    if missing:
        raise ValueError(f"As seguintes colunas não existem no DataFrame: {missing}")

    anos_sorted = sorted(anos)
    min_ano = anos_sorted[0]
    frames = []

    for y in anos_sorted:
        if primeiro_ano_sozinho and y == min_ano:
            start = y
        else:
            start = y - (janela_agrupamento - 1)
        # filtra os anos disponíveis na janela [start, y]
        mask = df['year'].between(start, y)
        # agrupa somando todas as colunas_agregacao ao mesmo tempo
        grp = df.loc[mask].groupby(coluna_agrupamento)[colunas_agregacao].sum(numeric_only=True).reset_index()
        grp['year'] = y
        frames.append(grp)

    # concatena todas as janelas
    result = pd.concat(frames, ignore_index=True)
    # renomeia colunas agregadas para '<col>_sum'
    rename_map = {col: f"{col}_sum" for col in colunas_agregacao}
    result = result.rename(columns=rename_map)
    # ordenar por coluna_agrupamento + year
    result = result.sort_values(coluna_agrupamento + ['year']).reset_index(drop=True)
    return result


import pandas as pd

def rename_one_column(df: pd.DataFrame, old_name: str, new_name: str, inplace: bool = False,
                      errors: str = 'raise', prevent_overwrite: bool = True) -> pd.DataFrame:
    """
    Renomeia uma única coluna em um DataFrame pandas.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    old_name : str
        Nome atual da coluna a ser renomeada.
    new_name : str
        Novo nome da coluna.
    inplace : bool, default False
        Se True, modifica o DataFrame em lugar e retorna o próprio df.
    errors : {'raise', 'ignore'}, default 'raise'
        'raise' -> levanta ValueError se old_name não existir.
        'ignore' -> retorna df inalterado se old_name não existir.
    prevent_overwrite : bool, default True
        Se True, levanta ValueError se new_name já existir no DataFrame (evita sobrescrita).
        Se False, permite renomear e possivelmente sobrescrever coluna existente.

    Retorno
    -------
    pd.DataFrame
        DataFrame com a coluna renomeada (ou o mesmo objeto se inplace=True).
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("`df` precisa ser um pandas.DataFrame")
    if not isinstance(old_name, str) or not isinstance(new_name, str):
        raise TypeError("`old_name` e `new_name` devem ser strings")

    if old_name not in df.columns:
        if errors == 'raise':
            raise ValueError(f"Coluna '{old_name}' não existe no DataFrame.")
        else:
            # ignore: retorna sem alterações
            return df if inplace else df.copy()

    if prevent_overwrite and new_name in df.columns and new_name != old_name:
        raise ValueError(f"Novo nome '{new_name}' já existe no DataFrame (prevent_overwrite=True).")

    if inplace:
        df.rename(columns={old_name: new_name}, inplace=True)
        return df
    else:
        return df.rename(columns={old_name: new_name})