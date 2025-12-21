"""
Data transformation functions for myfirstETL
"""

import duckdb
import pandas as pd
import plotly.graph_objects as go


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

def render_year_trend_and_change(result: pd.DataFrame) -> None:
    # Aggregate data by year
    yearly_data = result.groupby("ANIO").agg({
        "total_homicidios": "sum",
        "gunshot_homicidios": "sum"
    }).reset_index()

    yearly_data = yearly_data.sort_values("ANIO")

    # Calculate year-over-year percentage change for total homicides
    yearly_data["yoy_change"] = yearly_data["total_homicidios"].pct_change() * 100
    yearly_data["yoy_text"] = yearly_data.apply(
        lambda row: f"+{row['yoy_change']:.1f}%" if row["yoy_change"] > 0
        else f"{row['yoy_change']:.1f}%" if pd.notna(row["yoy_change"])
        else "",
        axis=1
    )
    yearly_data["yoy_color"] = yearly_data["yoy_change"].apply(
        lambda x: "#E74C3C" if x > 0 else "#3498DB" if pd.notna(x) else "black"
    )

    # Calculate year-over-year percentage change for gunshot homicides
    yearly_data["gunshot_yoy_change"] = yearly_data["gunshot_homicidios"].pct_change() * 100
    yearly_data["gunshot_yoy_text"] = yearly_data.apply(
        lambda row: f"+{row['gunshot_yoy_change']:.1f}%" if row["gunshot_yoy_change"] > 0
        else f"{row['gunshot_yoy_change']:.1f}%" if pd.notna(row["gunshot_yoy_change"])
        else "",
        axis=1
    )
    yearly_data["gunshot_yoy_color"] = yearly_data["gunshot_yoy_change"].apply(
        lambda x: "#E74C3C" if x > 0 else "#3498DB" if pd.notna(x) else "black"
    )

    # Create the figure
    fig = go.Figure()

    # Add bar chart for total homicides
    fig.add_trace(go.Bar(
        x=yearly_data["ANIO"],
        y=yearly_data["total_homicidios"],
        name="Homicidios Totales",
        text=yearly_data["total_homicidios"],
        textposition="outside",
        textfont={"size": 12, "color": "#2C3E50"},
        marker_color="#E67E22",
        opacity=0.8
    ))

    # Add line chart for gunshot homicides
    fig.add_trace(go.Scatter(
        x=yearly_data["ANIO"],
        y=yearly_data["gunshot_homicidios"]+2400,
        name="Por Arma de Fuego",
        mode="lines+markers+text",
        line={"color": "black", "width": 3},
        marker={"size": 8, "color": "black"},
        text=yearly_data["gunshot_homicidios"],
        textposition="top center",
        textfont={"size": 11, "color": "black"},
    ))

    # Add year-over-year change annotations for total homicides
    for _, row in yearly_data.iterrows():
        if pd.notna(row["yoy_change"]):
            fig.add_annotation(
                x=row["ANIO"],
                y=row["total_homicidios"],
                text=row["yoy_text"],
                showarrow=False,
                xshift=45,
                yshift=15,
                font={"size": 12, "color": "white", "family": "Arial Black"},
                bgcolor=row["yoy_color"],
                bordercolor=row["yoy_color"],
                borderwidth=1,
                borderpad=3
            )

    # Add year-over-year change annotations for gunshot homicides
    for _, row in yearly_data.iterrows():
        if pd.notna(row["gunshot_yoy_change"]):
            fig.add_annotation(
                x=row["ANIO"],
                y=row["gunshot_homicidios"]+2550,
                text=row["gunshot_yoy_text"],
                showarrow=False,
                xshift=45,
                yshift=0,
                font={"size": 12, "color": "white", "family": "Arial Black"},
                bgcolor=row["gunshot_yoy_color"],
                bordercolor=row["gunshot_yoy_color"],
                borderwidth=1,
                borderpad=3
            )

    # Update layout
    fig.update_layout(
        title={
            "text": "Tendencias Anuales de Homicidios en Perú (Datos SINADEF)",
            "font": {"size": 22}
        },
        xaxis_title="Año",
        yaxis_title="Cantidad de Homicidios",
        xaxis={
            "tickmode": "linear",
            "tick0": yearly_data["ANIO"].min(),
            "dtick": 1
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1
        },
        hovermode="x unified",
        template="plotly_white",
        height=600,
        showlegend=True
    )
    # fig.show()
    # Save the figure
    #fig.write_html("data/homicidios_trends.html")
    fig.write_image("data/homicidios_trends.png", width=1200, height=600, scale=2)
