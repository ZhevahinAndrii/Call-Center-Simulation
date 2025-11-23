import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from simulation.simulation import run_simulation, calculate_metrics

# Налаштування сторінки
st.set_page_config(
    page_title="Симуляція кол-центру",
    page_icon="📞",
    layout="wide"
)

# Заголовок та опис
st.title("📞 Симуляція кол-центру")
st.markdown("""
Ця програма моделює роботу кол-центру та аналізує вплив додавання чат-ботів
на навантаження системи та ключові показники ефективності (KPI).
""")

# Інформація про навігацію
st.info("""
**Навігація:** Використовуйте бічне меню зліва для переходу між сторінками:
1. **Головна сторінка** - Симуляція та аналіз роботи кол-центру
2. **Завантаження коду** - Доступ до вихідного коду програми
3. **Опис коду** - Опис функцій та фрагментів коду
""")

# Бокове меню з параметрами
st.sidebar.header("Параметри симуляції")

# Параметри вхідних дзвінків
with st.sidebar.expander("Параметри дзвінків", expanded=True):
    lambda_calls = st.slider("Інтенсивність вхідних дзвінків (дзвінків/хв)", 1.0, 15.0, 7.0, 0.5)
    call_duration = st.slider("Середня тривалість дзвінка (хв)", 0.5, 5.0, 2.0, 0.1)

# Параметри ресурсів
with st.sidebar.expander("Параметри ресурсів", expanded=True):
    operators = st.slider("Кількість операторів", 1, 20, 10, 1)
    chatbots = st.slider("Кількість чат-ботів", 0, 15, 6, 1)

# Загальні налаштування симуляції
with st.sidebar.expander("Налаштування симуляції", expanded=True):
    simulation_time = st.slider("Час симуляції (хв)", 60, 600, 300, 60)
    random_seed = st.number_input("Випадкове зерно", 1, 1000, 42, 1)

# Кнопка запуску симуляції
run_button = st.sidebar.button("Запустити симуляцію", type="primary")

# Ініціалізація стану сесії
if 'simulation_run' not in st.session_state:
    st.session_state.simulation_run = False
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None

# Створення вкладок
tab1, tab2, tab3 = st.tabs(["Панель результатів", "Детальні метрики", "Порівняння"])

# Запуск симуляції
if run_button:
    with st.spinner("Виконується симуляція..."):
        with_chatbots = run_simulation(lambda_calls, call_duration, operators, chatbots, simulation_time, random_seed, True)
        without_chatbots = run_simulation(lambda_calls, call_duration, operators, 0, simulation_time, random_seed, False)

        metrics_with = calculate_metrics(with_chatbots, operators, chatbots, lambda_calls, call_duration)
        metrics_without = calculate_metrics(without_chatbots, operators, 0, lambda_calls, call_duration)

        st.session_state.simulation_results = {
            "with_chatbots": with_chatbots,
            "without_chatbots": without_chatbots,
            "metrics_with": metrics_with,
            "metrics_without": metrics_without
        }
        st.session_state.simulation_run = True

# Виведення результатів
if st.session_state.simulation_run:
    results = st.session_state.simulation_results
    with_chatbots = results["with_chatbots"]
    without_chatbots = results["without_chatbots"]
    metrics_with = results["metrics_with"]
    metrics_without = results["metrics_without"]

    # Вкладка 1: Панель результатів
    with tab1:
        st.header("Огляд результатів симуляції")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Завантаження системи (ρ)", f"{metrics_with['rho']:.2f}", f"{metrics_with['rho'] - metrics_without['rho']:.2f}", delta_color="inverse")
        with col2:
            st.metric("ANT (хв)", f"{metrics_with['ANT']:.2f}")
        with col3:
            st.metric("CSAT", f"{metrics_with['CSAT']:.1f}", f"{metrics_with['CSAT'] - metrics_without['CSAT']:.1f}")
        with col4:
            st.metric("FCR (%)", f"{metrics_with['FCR']*100:.1f}", f"{(metrics_with['FCR'] - metrics_without['FCR'])*100:.1f}")

        st.subheader("Аналіз черги")
        fig_queue = go.Figure()
        fig_queue.add_trace(go.Scatter(x=with_chatbots["time_points"], y=with_chatbots["queue_lengths"], mode='lines', name='З чат-ботами', line=dict(color='green')))
        fig_queue.add_trace(go.Scatter(x=without_chatbots["time_points"], y=without_chatbots["queue_lengths"], mode='lines', name='Без чат-ботів', line=dict(color='red')))
        fig_queue.update_layout(title='Довжина черги протягом часу', xaxis_title='Час (хвилини)', yaxis_title='Кількість у черзі')
        st.plotly_chart(fig_queue, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.histogram(x=with_chatbots["wait_times"], nbins=20, title='Час очікування (з чат-ботами)', color_discrete_sequence=['green']), use_container_width=True)
        with col2:
            st.plotly_chart(px.histogram(x=without_chatbots["wait_times"], nbins=20, title='Час очікування (без чат-ботів)', color_discrete_sequence=['red']), use_container_width=True)

    # Вкладка 2: Детальні метрики
    with tab2:
        st.header("Детальні показники ефективності")
        metrics_df = pd.DataFrame({...})  # скорочено для зручності оформлення
        st.dataframe(metrics_df, use_container_width=True)

    # Вкладка 3: Порівняння сценаріїв
    with tab3:
        st.header("Порівняння сценаріїв")
        st.write(f"Оператори: {operators}, Чат-боти: {chatbots}")
        st.write("Порівняльний графік метрик:")
        comparison_df = pd.DataFrame({...})  # скорочено для стислості
        st.dataframe(comparison_df)
