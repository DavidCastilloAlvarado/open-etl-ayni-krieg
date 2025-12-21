"""
Data transformation functions for myfirstETL
"""

import duckdb
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
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


def render_year_trend_and_change(result: pd.DataFrame) -> None:
    # Aggregate data by year
    yearly_data = (
        result.groupby("ANIO")
        .agg({"total_homicidios": "sum", "gunshot_homicidios": "sum"})
        .reset_index()
    )

    yearly_data = yearly_data.sort_values("ANIO")

    # Calculate year-over-year percentage change for total homicides
    yearly_data["yoy_change"] = yearly_data["total_homicidios"].pct_change() * 100
    yearly_data["yoy_text"] = yearly_data.apply(
        lambda row: f"+{row['yoy_change']:.1f}%"
        if row["yoy_change"] > 0
        else f"{row['yoy_change']:.1f}%"
        if pd.notna(row["yoy_change"])
        else "",
        axis=1,
    )

    # Calculate year-over-year percentage change for gunshot homicides
    yearly_data["gunshot_yoy_change"] = yearly_data["gunshot_homicidios"].pct_change() * 100
    yearly_data["gunshot_yoy_text"] = yearly_data.apply(
        lambda row: f"+{row['gunshot_yoy_change']:.1f}%"
        if row["gunshot_yoy_change"] > 0
        else f"{row['gunshot_yoy_change']:.1f}%"
        if pd.notna(row["gunshot_yoy_change"])
        else "",
        axis=1,
    )

    # Create the figure
    fig, ax = plt.subplots(figsize=(12, 8))

    years = yearly_data["ANIO"].values
    total_hom = yearly_data["total_homicidios"].values
    gunshot_hom = yearly_data["gunshot_homicidios"].values

    # Bar chart for total homicides
    _ = ax.bar(years, total_hom, color="#E67E22", alpha=0.8, label="Homicidios Totales")

    # Add values on top of bars
    for i, (year, val) in enumerate(zip(years, total_hom, strict=False)):
        ax.text(year, val, str(val), ha="center", va="bottom", fontsize=10, color="#2C3E50")

        # Add YoY change for total homicides
        if pd.notna(yearly_data.iloc[i]["yoy_change"]):
            yoy_val = yearly_data.iloc[i]["yoy_change"]
            yoy_text = yearly_data.iloc[i]["yoy_text"]
            color = "#E74C3C" if yoy_val > 0 else "#3498DB"
            ax.text(
                year + 0,
                val + 150,
                yoy_text,
                ha="center",
                va="center",
                fontsize=10,
                color="white",
                weight="bold",
                bbox={"boxstyle": "round,pad=0.3", "facecolor": color, "edgecolor": color},
            )

    # Line chart for gunshot homicides
    ax2 = ax
    _ = ax2.plot(
        years,
        gunshot_hom + 2200,
        color="black",
        linewidth=3,
        marker="o",
        markersize=8,
        label="Por Arma de Fuego",
    )

    # Add values on the line
    for i, (year, val) in enumerate(zip(years, gunshot_hom, strict=False)):
        ax2.text(year, val + 2250, str(val), ha="center", va="bottom", fontsize=10, color="black")

        # Add YoY change for gunshot homicides
        if pd.notna(yearly_data.iloc[i]["gunshot_yoy_change"]):
            yoy_val = yearly_data.iloc[i]["gunshot_yoy_change"]
            yoy_text = yearly_data.iloc[i]["gunshot_yoy_text"]
            color = "#E74C3C" if yoy_val > 0 else "#3498DB"
            ax2.text(
                year + 0,
                val + 2400,
                yoy_text,
                ha="center",
                va="center",
                fontsize=10,
                color="white",
                weight="bold",
                bbox={"boxstyle": "round,pad=0.3", "facecolor": color, "edgecolor": color},
            )

    # Labels and title
    ax.set_xlabel("Año", fontsize=12)
    ax.set_ylabel("Cantidad de Homicidios", fontsize=12)
    ax2.set_ylabel("Homicidios por Arma de Fuego", fontsize=12)
    ax.set_title("Tendencias Anuales de Homicidios en Perú (Datos SINADEF)", fontsize=16, pad=20)

    # Set x-axis to show all years
    ax.set_xticks(years)
    ax.set_xticklabels(years, rotation=0)
    ax.set_ylim(0, 3000)
    # Legend
    bars_patch = mpatches.Patch(color="#E67E22", alpha=0.8, label="Homicidios Totales")
    line_patch = mpatches.Patch(color="black", label="Por Arma de Fuego")
    ax.legend(handles=[bars_patch, line_patch], loc="upper left", fontsize=10)

    # Grid
    ax.grid(axis="y", alpha=0.3, linestyle="--")

    plt.tight_layout()
    # plt.show()
    # Save the figure
    plt.savefig("data/homicidios_trends.png", dpi=200)
    plt.close()
