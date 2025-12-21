"""
Data transformation functions for myfirstETL
"""

import duckdb
import pandas as pd


def select_and_clean_columns(df_raw: pd.DataFrame) -> pd.DataFrame:
    df = duckdb.query("""
        SELECT
            ANIO,
            MES,
            SEXO,
            DEPARTAMENTO_FALLECIMIENTO,
            PROVINCIA_FALLECIMIENTO,
            DISTRITO_FALLECIMIENTO,
            EDAD,
            PAIS_DOMICILIO,
            ETNIA,
            TIPO_LUGAR,
            NIVEL_DE_INSTRUCCION,
            MUERTE_VIOLENTA,
            UPPER(TRIM(REGEXP_REPLACE(DEBIDO_CAUSA_A, '[^a-zA-Z0-9 ]', '', 'g'))) AS DEBIDO_CAUSA_A
        FROM df_raw
        WHERE DEBIDO_CAUSA_A IS NOT NULL
    """).df()
    return df


def filter_and_agg_violent_deaths(df: pd.DataFrame) -> pd.DataFrame:
    gunshot_keywords = [
        "PROYECTIL DE ARMA DE FUEGO",
        "PENETRANTE POR PAF",
        "PERFORANTE POR PAF",
        "ARMA DE FUEGO",
        "PAF ",
        " PAF",
        "BALA",
        "DISPARO",
        "PROYECTIL",
        # "PENETRANTE",
        "PERFOROCONTUSA",
    ]

    # Keywords to capture knife/stabbing related causes
    knife_keywords = [
        "ARMA BLANCA",
        "PUNZOCORTANTE",
        "PUNZO CORTANTE",
        "PUNZOCORTOPENETRANTE",
        "PUNZO CORTO",
        "CORTANTE",
        "FILO",
        "DEGELLO",
        "DEGUELLO",
        "PUNTA",
    ]

    # Keywords to capture contusion/blunt force related causes
    contusion_keywords = [
        "CONTUSION",
        "CONTUCION",
        "CONTUSIN",
        "CONTUNDENTE",
        "CONTUSO CORTANTE",
        "APLASTAMIENTO",
        "ATRICCION",
        "ATRICCIN",
        "CERRADO",
    ]

    # falla organiza hemorragia
    organismo_hemo_keywords = [
        "SHOCK HIPOVOLEMICO",
        "CHOQUE HIPOVOLMICO",
        "HEMORRAGIA AGUDA",
        "ANEMIA AGUDA",
    ]

    # Build OR conditions for keyword matching
    like_conditions_gun = " OR ".join(
        [f"DEBIDO_CAUSA_A LIKE '%{keyword}%'" for keyword in gunshot_keywords]
    )
    like_conditions_knife = " OR ".join(
        [f"DEBIDO_CAUSA_A LIKE '%{keyword}%'" for keyword in knife_keywords]
    )
    like_conditions_contusion = " OR ".join(
        [f"DEBIDO_CAUSA_A LIKE '%{keyword}%'" for keyword in contusion_keywords]
    )
    like_conditions_organismo_hemo = " OR ".join(
        [f"DEBIDO_CAUSA_A LIKE '%{keyword}%'" for keyword in organismo_hemo_keywords]
    )

    result = duckdb.query(f"""
        SELECT
            ANIO,
            MES,
            MAKE_DATE(CAST(ANIO AS INTEGER), CAST(MES AS INTEGER), 1) as DATE,
            SEXO,
            PAIS_DOMICILIO,
            ETNIA,
            DEPARTAMENTO_FALLECIMIENTO,
            PROVINCIA_FALLECIMIENTO,
            DISTRITO_FALLECIMIENTO,
            EDAD,
            COUNT(*) as total_homicidios,
            SUM(CASE WHEN {like_conditions_gun} THEN 1 ELSE 0 END) as gunshot_homicidios,
            SUM(CASE WHEN {like_conditions_knife} THEN 1 ELSE 0 END) as knife_homicidios,
            SUM(CASE WHEN {like_conditions_contusion} THEN 1 ELSE 0 END) as contusion_homicidios,
            SUM(CASE WHEN {like_conditions_organismo_hemo} THEN 1 ELSE 0 END) as organismo_hemo_homicidios
        FROM df
        WHERE MUERTE_VIOLENTA = 'HOMICIDIO'
        GROUP BY
        ANIO,
        MES,
        SEXO,
        PAIS_DOMICILIO,
        ETNIA,
        DEPARTAMENTO_FALLECIMIENTO,
        PROVINCIA_FALLECIMIENTO,
        DISTRITO_FALLECIMIENTO,
        EDAD
        ORDER BY ANIO DESC, MES DESC
    """).df()
    return result
