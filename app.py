import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="WeatherInsight", layout="wide")
st.title("🌦️ WeatherInsight: Погодные тренды")

DB_PATH = "data/weather.db"

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM weather ORDER BY date", conn)
    conn.close()
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"❌ Не удалось загрузить данные: {e}")
    st.stop()

st.subheader("📊 Общая статистика")
st.write(f"Всего записей: {len(df)}")
st.write(f"Уникальных городов: {df['city'].nunique()}")

st.subheader("🗓️ Выбор диапазона дат")
min_date = df["date"].min()
max_date = df["date"].max()
start_date, end_date = st.date_input("Выберите диапазон дат", value=(min_date, max_date))

cities = sorted(df["city"].unique())
selected_cities = st.multiselect("Выберите города", cities, default=cities[:2])

if not selected_cities:
    st.warning("Выберите хотя бы один город")
    st.stop()

filtered = df[(df["city"].isin(selected_cities)) & (df["date"] >= start_date) & (df["date"] <= end_date)]
if filtered.empty:
    st.warning("Нет данных")
    st.stop()

# --- 1. ЛИНЕЙНЫЙ ГРАФИК ТЕМПЕРАТУРЫ ---
st.subheader("📈 Динамика температуры")
fig1 = px.line(filtered, x="date", y="avg_temp", color="city", title="Температура по дням")
st.plotly_chart(fig1, use_container_width=True)

# --- 2. СТОЛБЧАТАЯ ДИАГРАММА ОСАДКОВ ---
st.subheader("💧 Осадки")
fig2 = px.bar(filtered, x="date", y="total_precip", color="city", title="Осадки по дням")
st.plotly_chart(fig2, use_container_width=True)

# --- 3. BOXPLOT ТЕМПЕРАТУРЫ ПО ГОРОДАМ ---
st.subheader("📦 Распределение температуры по городам")
fig3 = px.box(filtered, x="city", y="avg_temp", color="city", title="Температура")
st.plotly_chart(fig3, use_container_width=True)

# --- 4. ГИСТОГРАММА ТЕМПЕРАТУРЫ ---
st.subheader("📊 Гистограмма температуры")
fig4 = px.histogram(filtered, x="avg_temp", nbins=30, title="Распределение температуры", color="city")
st.plotly_chart(fig4, use_container_width=True)

# --- 5. СРАВНЕНИЕ СРЕДНЕЙ ТЕМПЕРАТУРЫ ПО ГОРОДАМ ---
st.subheader("📊 Сравнение городов")
avg_temp_city = filtered.groupby("city")["avg_temp"].mean().reset_index()
fig5 = px.bar(avg_temp_city, x="city", y="avg_temp", title="Средняя температура по городам")
st.plotly_chart(fig5, use_container_width=True)

# --- 6. СКОЛЬЗЯЩЕЕ СРЕДНЕЕ (для первого города) ---
if len(selected_cities) >= 1:
    st.subheader("📉 Скользящее среднее (температура)")
    city_first = selected_cities[0]
    city_df = filtered[filtered["city"] == city_first].sort_values("date")
    city_df["rolling_7"] = city_df["avg_temp"].rolling(window=7).mean()
    fig6 = px.line(city_df, x="date", y=["avg_temp", "rolling_7"], title=f"Температура в {city_first} (факт и среднее за 7 дней)")
    st.plotly_chart(fig6, use_container_width=True)

# --- 7. КОРРЕЛЯЦИЯ (если есть числовые колонки) ---
numeric_cols = filtered.select_dtypes(include=[np.number]).columns.tolist()
if len(numeric_cols) >= 2:
    st.subheader("🔗 Корреляционная матрица")
    corr = filtered[numeric_cols].corr()
    fig7 = px.imshow(corr, text_auto=True, title="Корреляция")
    st.plotly_chart(fig7, use_container_width=True)

# --- 8. ИНДЕКС КОМФОРТА (если есть) ---
if "comfort_index" in filtered.columns:
    st.subheader("🏆 Индекс комфорта")
    fig8 = px.line(filtered, x="date", y="comfort_index", color="city", title="Индекс комфорта (чем выше — тем комфортнее)")
    st.plotly_chart(fig8, use_container_width=True)

# --- 9. ТАБЛИЦА ДАННЫХ ---
st.subheader("📋 Таблица данных")
st.dataframe(filtered.sort_values("date", ascending=False), use_container_width=True)

st.success("✅ Готово")
