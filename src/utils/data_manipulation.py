import pandas as pd
from typing import List, Optional, Dict
import re

import sys
sys.path.append('../avaliacao-python-ciencia-dados/')

from utils.data_analisys import *


def junta_dataframes(df1, df2, chave, tipo_juncao='inner'):
    df_final = pd.merge(df1, df2, on=chave, how=tipo_juncao)
    print(f'Dataframes unidos com sucesso! \nDimensão: {df_final.shape}')
    return df_final

def agrega_anos(df, anos, colunas_agregacao, coluna_agrupamento=['country'], janela_agrupamento=5, primeiro_ano_sozinho=True):
    """
    Feita usando IA como apoio.
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


def renomeia_coluna(df: pd.DataFrame, nome_anterior: str, novo_nome: str, inplace: bool = False,
                      errors: str = 'raise', previnir_sobrescrita: bool = True) -> pd.DataFrame:
    """
    Feita usando IA como apoio.
    Renomeia uma única coluna em um DataFrame pandas.

    Parâmetros
    ----------
    df : pd.DataFrame
        DataFrame de entrada.
    nome_anterior : str
        Nome atual da coluna a ser renomeada.
    novo_nome : str
        Novo nome da coluna.
    inplace : bool, default False
        Se True, modifica o DataFrame em lugar e retorna o próprio df.
    errors : {'raise', 'ignore'}, default 'raise'
        'raise' -> levanta ValueError se nome_anterior não existir.
        'ignore' -> retorna df inalterado se nome_anterior não existir.
    previnir_sobrescrita : bool, default True
        Se True, levanta ValueError se novo_nome já existir no DataFrame (evita sobrescrita).
        Se False, permite renomear e possivelmente sobrescrever coluna existente.

    Retorno
    -------
    pd.DataFrame
        DataFrame com a coluna renomeada (ou o mesmo objeto se inplace=True).
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("`df` precisa ser um pandas.DataFrame")
    if not isinstance(nome_anterior, str) or not isinstance(novo_nome, str):
        raise TypeError("`nome_anterior` e `novo_nome` devem ser strings")

    if nome_anterior not in df.columns:
        if errors == 'raise':
            raise ValueError(f"Coluna '{nome_anterior}' não existe no DataFrame.")
        else:
            # ignore: retorna sem alterações
            return df if inplace else df.copy()

    if previnir_sobrescrita and novo_nome in df.columns and novo_nome != nome_anterior:
        raise ValueError(f"Novo nome '{novo_nome}' já existe no DataFrame (previnir_sobrescrita=True).")

    if inplace:
        df.rename(columns={nome_anterior: novo_nome}, inplace=True)
        return df
    else:
        return df.rename(columns={nome_anterior: novo_nome})

def transpoe_anos(
    df: pd.DataFrame,
    colunas_agregacao: List[str],
    colunas_ano: Optional[List[str]] = None,
    regex_ano: str = r"(\d{4})",
    novo_nome_coluna: str = "value",
    var_name: str = "year",
    dropna: bool = True,
    converte_ano_para_inteiro: bool = True,
) -> pd.DataFrame:
    """
    Feita usando IA como apoio.
    Converte um DataFrame wide (uma coluna por ano) para long (uma linha por país+ano).
    - df: DataFrame de entrada.
    - colunas_agregacao: colunas que identificam a entidade, ex: ['country'].
    - colunas_ano: lista explícita de colunas que representam anos (opcional).
    - regex_ano: regex para extrair o ano do nome da coluna (default captura 4 dígitos).
      Se as colunas forem exatamente '1952','1957',... a detecção automática também funciona.
    - novo_nome_coluna: nome da coluna de valor no DataFrame resultante.
    - var_name: nome temporário gerado pelo melt (por padrão 'year', depois convertida).
    - dropna: se True, elimina linhas cujo valor seja NaN.
    - converte_ano_para_inteiro: se True, converte o ano para int quando puder.

    Retorna um DataFrame com columns = colunas_agregacao + ['year', novo_nome_coluna].
    """

    # validações
    if not set(colunas_agregacao).issubset(df.columns):
        missing = list(set(colunas_agregacao) - set(df.columns))
        raise ValueError(f"As colunas colunas_agregacao faltantes no df: {missing}")

    # detectar colunas ano quando não fornecidas
    if colunas_ano is None:
        # 1) colunas que são exatamente 4 dígitos (ex: '1952')
        candidate_years = [c for c in df.columns if re.fullmatch(r"\d{4}", str(c))]
        if candidate_years:
            colunas_ano = candidate_years
        else:
            # 2) colunas que contenham 4 dígitos em qualquer parte (ex: 'k_1952', 'Deaths 1952')
            colunas_ano = [c for c in df.columns if re.search(regex_ano, str(c))]

    if not colunas_ano:
        raise ValueError("Nenhuma coluna de ano identificada. Passe `colunas_ano` explicitamente ou ajuste `regex_ano`.")

    # mapear coluna -> ano (string)
    col_to_year: Dict[str, str] = {}
    for col in colunas_ano:
        m = re.search(regex_ano, str(col))
        if m:
            year_str = m.group(1)
        else:
            # se não extrair com regex, e o nome for exatamente um número, usa ele
            if re.fullmatch(r"\d{4}", str(col)):
                year_str = str(col)
            else:
                # fallback para nome literal da coluna (pouco provável)
                year_str = str(col)
        col_to_year[col] = year_str

    # melt
    melted = df.melt(id_vars=colunas_agregacao, value_vars=list(col_to_year.keys()),
                     var_name=var_name, value_name=novo_nome_coluna)

    # transformar a coluna do var_name para o ano extraído
    # aplicamos o mapping criado
    melted[var_name] = melted[var_name].map(col_to_year)

    # converter tipo do ano
    if converte_ano_para_inteiro:
        def to_int_safe(x):
            try:
                return int(x)
            except Exception:
                return x
        melted[var_name] = melted[var_name].apply(to_int_safe)

    # opcionalmente remover NaNs
    if dropna:
        melted = melted.dropna(subset=[novo_nome_coluna])

    # ordenar e reorganizar colunas
    out_cols = list(colunas_agregacao) + [var_name, novo_nome_coluna]
    melted = melted[out_cols]
    melted = melted.sort_values(list(colunas_agregacao) + [var_name]).reset_index(drop=True)

    return melted


def transpoe_e_trata_dataframe(df, nome_coluna_resultado='resultado'):
    tratado = df.copy()
    tratado = transpoe_anos(tratado, colunas_agregacao=['name'])
    tratado['value'] = tratado['value'].round(2)
    remove_dados_duplicados(tratado)
    renomeia_coluna(tratado, nome_anterior='name', novo_nome='country', inplace=True)
    renomeia_coluna(tratado, nome_anterior='value', novo_nome=nome_coluna_resultado, inplace=True)
    return tratado