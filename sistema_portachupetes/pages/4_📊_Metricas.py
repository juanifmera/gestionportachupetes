import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from crud.pedidos import listar_todos_pedidos
from crud.stock import listar_stock
import plotly.express as px
from database.engine import engine
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.models import MaterialPedido, Material
import plotly.graph_objects as go

st.title('Métricas 📊')
st.divider()

tabs_metricas = st.tabs([
    'Resumen General 📅',
    'Alertas de Stock ⚠️',
    'Materiales Más Usados 📈',
])

with tabs_metricas[0]:
    st.subheader("Resumen General de Pedidos", divider="rainbow")

    col1, col2, col3, col4 = st.columns(4)

    # Cargar pedidos
    hoy = datetime.today().date()
    hace_semana = hoy - timedelta(days=7)
    dos_semanas_atras = hace_semana - timedelta(days=7)

    df_pedidos = listar_todos_pedidos()
    df_pedidos["Fecha Creación"] = pd.to_datetime(df_pedidos["Fecha Creación"]) #type:ignore

    # Métricas generales
    pedidos_totales = df_pedidos.shape[0]#type:ignore
    pedidos_enproceso = df_pedidos[df_pedidos['Estado'] == 'En proceso'].shape[0]#type:ignore
    pedidos_cancelados = df_pedidos[df_pedidos['Estado'] == 'Cancelado'].shape[0]#type:ignore
    pedidos_terminados = df_pedidos[df_pedidos['Estado'] == 'Terminado'].shape[0]#type:ignore

    # Mostrar métricas generales
    with col1:
        st.metric('Pedidos Totales', value=pedidos_totales)

    with col2:
        st.metric('Pedidos en Proceso', pedidos_enproceso)

    with col3:
        st.metric('Pedidos Cancelados', pedidos_cancelados)

    with col4:
        st.metric('Pedidos Terminados', pedidos_terminados)

    # ---------------------------
    st.divider()
    st.markdown("### 🌐 Métricas de la Semana Actual")

    col1, col2, col3, col4 = st.columns(4)

    pedidos_semana_total = df_pedidos[df_pedidos['Fecha Creación'].dt.date >= hace_semana].shape[0]#type:ignore
    pedidos_semana_enproceso = df_pedidos[(df_pedidos['Fecha Creación'].dt.date >= hace_semana) & (df_pedidos['Estado'] == 'En proceso')].shape[0]#type:ignore
    pedidos_semana_cancelados = df_pedidos[(df_pedidos['Fecha Creación'].dt.date >= hace_semana) & (df_pedidos['Estado'] == 'Cancelado')].shape[0]#type:ignore
    pedidos_semana_terminados = df_pedidos[(df_pedidos['Fecha Creación'].dt.date >= hace_semana) & (df_pedidos['Estado'] == 'Terminado')].shape[0]#type:ignore

    with col1:
        st.metric('Pedidos esta semana', pedidos_semana_total)

    with col2:
        st.metric('En Proceso esta semana', pedidos_semana_enproceso)

    with col3:
        st.metric('Cancelados esta semana', pedidos_semana_cancelados)

    with col4:
        st.metric('Terminados esta semana', pedidos_semana_terminados)

    # ---------------------------
    st.divider()
    st.markdown("### 🔄 Comparativa Semana Actual vs Anterior")

    col1, col2, col3, col4 = st.columns(4)

    def calcular_delta(actual, anterior):
        if anterior == 0:
            return actual, "+100%", "normal" if actual > 0 else "off"
        delta_val = actual - anterior
        delta_pct = round(((actual / anterior) - 1) * 100, 2)
        color = "normal" if delta_val >= 0 else "inverse"
        return delta_val, f"{delta_pct}%", color

    prev_total = df_pedidos[(df_pedidos['Fecha Creación'].dt.date >= dos_semanas_atras) & (df_pedidos['Fecha Creación'].dt.date < hace_semana)].shape[0] #type:ignore
    prev_enproceso = df_pedidos[(df_pedidos['Fecha Creación'].dt.date >= dos_semanas_atras) & (df_pedidos['Fecha Creación'].dt.date < hace_semana) & (df_pedidos['Estado'] == 'En proceso')].shape[0]#type:ignore
    prev_cancelados = df_pedidos[(df_pedidos['Fecha Creación'].dt.date >= dos_semanas_atras) & (df_pedidos['Fecha Creación'].dt.date < hace_semana) & (df_pedidos['Estado'] == 'Cancelado')].shape[0]#type:ignore
    prev_terminados = df_pedidos[(df_pedidos['Fecha Creación'].dt.date >= dos_semanas_atras) & (df_pedidos['Fecha Creación'].dt.date < hace_semana) & (df_pedidos['Estado'] == 'Terminado')].shape[0]#type:ignore

    dif_total, pct_total, color_total = calcular_delta(pedidos_semana_total, prev_total)
    dif_enproceso, pct_enproceso, color_enproceso = calcular_delta(pedidos_semana_enproceso, prev_enproceso)
    dif_cancelados, pct_cancelados, color_cancelados = calcular_delta(pedidos_semana_cancelados, prev_cancelados)
    dif_terminados, pct_terminados, color_terminados = calcular_delta(pedidos_semana_terminados, prev_terminados)

    with col1:
        st.metric('Total Semanal', value=dif_total, delta=pct_total, delta_color= 'normal' if dif_total >= 0 else 'inverse')
        st.write()

    with col2:
        st.metric('En Proceso', value=dif_enproceso, delta=pct_enproceso, delta_color= 'normal' if dif_enproceso >= 0 else 'inverse')

    with col3:
        st.metric('Cancelados', value=dif_cancelados, delta=pct_cancelados, delta_color= 'normal' if dif_cancelados >= 0 else 'inverse')

    with col4:
        st.metric('Terminados', value=dif_terminados, delta=pct_terminados, delta_color= 'normal' if dif_terminados >= 0 else 'inverse')

    # ---------------------------
    st.divider()
    st.markdown("### 🔹 Evolución Semanal de Pedidos")

    # Agrupar pedidos por semana

    pedidos_semana = df_pedidos.copy()#type:ignore
    pedidos_semana["Semana"] = pedidos_semana["Fecha Creación"].dt.to_period("W").apply(lambda r: r.start_time)

    agrupado = pedidos_semana.groupby(["Semana", "Estado"]).size().unstack(fill_value=0)
    agrupado["Total"] = agrupado.sum(axis=1)

    # Crear figura con Plotly
    fig = go.Figure()#type:ignore

    fig.add_trace(go.Scatter(x=agrupado.index, y=agrupado["Total"], mode="lines+markers", name="Total", line=dict(color="red")))#type:ignore

    for estado, color in zip(["En proceso", "Cancelado", "Terminado"], ["orange", "pink", "green"]):
        if estado in agrupado.columns:
            fig.add_trace(go.Scatter(#type:ignore
                x=agrupado.index,
                y=agrupado[estado],
                mode="lines+markers",
                name=estado,
                line=dict(color=color)
            ))

    fig.update_layout(
        title="Evolución de Pedidos por Semana",
        xaxis_title="Semana",
        yaxis_title="Cantidad de Pedidos",
        legend_title="Estado"
    )

    st.plotly_chart(fig, width='stretch')

    # ---------------------------
    st.divider()
    st.markdown("### ✅ Porcentaje de Cumplimiento de Pedidos")

    if pedidos_totales > 0:
        porcentaje_terminados = int((pedidos_terminados / pedidos_totales) * 100)
        porcentaje_cancelados = int((pedidos_cancelados / pedidos_totales) * 100)

        st.progress(porcentaje_terminados / 100, text=f"Pedidos Terminados: {porcentaje_terminados}%")
        st.progress(porcentaje_cancelados / 100, text=f"Pedidos Cancelados: {porcentaje_cancelados}%")
    else:
        st.info("No hay pedidos suficientes para calcular progresos.")

## BAJO STOCK ##
with tabs_metricas[1]:
    st.subheader("📉 Alerta de Stock Bajo", divider="rainbow")

    df_stock = listar_stock()
    stock_bajo = df_stock[df_stock['Cantidad'] < 5] # type: ignore

    st.dataframe(stock_bajo, width='stretch')
    st.caption(f"🔍 Se encontraron {stock_bajo.shape[0]} materiales con stock bajo (menos de 5 unidades).")

    # Gráfico de barras
    if not stock_bajo.empty:
        fig_stock = px.bar(
        stock_bajo,
        x="Cantidad",
        y="Descripción",
        color="Categoría",
        orientation="h",
        title="Materiales con Bajo Stock",
        labels={"Cantidad": "Cantidad en Stock", "Descripción": "Material"},
        )
        fig_stock.update_layout(yaxis_categoryorder='total ascending')
        st.plotly_chart(fig_stock, width='stretch')
    else:
        st.success("🎉 No hay materiales con stock bajo.")

### Materiales Más Usados 📈
with tabs_metricas[2]:
    st.subheader("📊 Materiales más Usados", divider="rainbow")

    # Cargar materiales usados
    session = Session(bind=engine)
    materiales_usados = session.query(
        MaterialPedido.codigo_material,
        func.sum(MaterialPedido.cantidad_usada).label("Cantidad Usada")
    ).group_by(MaterialPedido.codigo_material).all()

    df_usos = pd.DataFrame(materiales_usados, columns=["Código", "Cantidad Usada"])

    # Unir con info de Material
    materiales = session.query(Material).all()
    df_info = pd.DataFrame([{
        "Código": m.codigo_material,
        "Descripción": m.descripcion,
        "Categoría": m.categoria
    } for m in materiales])

    df_merged = pd.merge(df_usos, df_info, on="Código", how="left")

    # Filtro por categoría
    categorias = sorted(df_merged["Categoría"].dropna().unique())
    categoria_seleccionada = st.selectbox("Seleccioná una categoría para ver los más usados", categorias)

    df_filtrado = df_merged[df_merged["Categoría"] == categoria_seleccionada]
    df_top5 = df_filtrado.sort_values(by="Cantidad Usada", ascending=False).head(5)

    # Mostrar gráfico de barras horizontal
    fig = px.bar(
        df_top5,
        x="Cantidad Usada",
        y="Descripción",
        orientation='h',
        title=f"Top 5 Materiales más usados - Categoría: {categoria_seleccionada}",
        labels={"Descripción": "Material", "Cantidad Usada": "Usos"}
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))

    st.plotly_chart(fig, width='stretch')