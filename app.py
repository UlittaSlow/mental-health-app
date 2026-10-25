import streamlit as st
import json
import os
import pandas as pd
import plotly.express as px

DATA_FILE = "data.json"

def save_entry(entry):
    # 1. Читаем старые данные
    if not os.path.exists(DATA_FILE):
        data = []
    else:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    # 2. Ищем, есть ли уже запись на эту дату
    entry_date = entry["date"]
    found_index = -1 # -1 значит "не найдено"

    for i, old_entry in enumerate(data):
        if old_entry.get("date") == entry_date:
            found_index = i
            break # Нашли! Дальше можно не искать

    # 3. Обновляем или добавляем
    if found_index != -1:
        # Если нашли — заменяем старую запись на новую
        data[found_index] = entry
    else:
        # Если не нашли — добавляем в конец
        data.append(entry)

    # 4. Сохраняем файл
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Настройка страницы (заголовок вкладки браузера и иконка)
st.set_page_config(page_title="Мое приложение", page_icon="🌱", layout="centered")

# --- НАВИГАЦИЯ ---
# Если в памяти нет текущей страницы, ставим по умолчанию "Главная"
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Главная"

# Функция для перехода на другой экран
def go_to(page_name):
    st.session_state["current_page"] = page_name
    st.rerun()

if st.session_state["current_page"] == "Главная":
    st.title("🌱 Ментальное здоровье")
    st.write("Добро пожаловать! Это твой личный дневник.")

    if st.button("📖 Дневник эмоций", use_container_width=True):
        go_to("Дневник эмоций")

    if st.button("📊 Статистика", use_container_width=True):
        go_to("Статистика")

# --- ЭКРАН 2: ДНЕВНИК ---
elif st.session_state["current_page"] == "Дневник эмоций":
    # Кнопка Назад
    if st.button("← Назад на главную"):
        go_to("Главная")

    st.title("📖 Дневник эмоций")

      # 1. Дата
    date_val = st.date_input("Дата")

    # 2. Уровень тревоги (от 1 до 10)
    anxiety_val = st.slider("Уровень фоновой тревоги", min_value=1, max_value=10, value=5)

    # 3. Аппетит
    appetite_val = st.radio("Аппетит", ["Плохой", "Удовлетворительный", "Хороший"], horizontal=True)

    # 4. Сон
    sleep_val = st.radio("Сон", ["Хороший", "Плохой"], horizontal=True)

    # 5. Симптомы (чекбоксы)
    st.write("Симптомы:")
    symptom_paralysis = st.checkbox("Сонный паралич")
    symptom_headache = st.checkbox("Головная боль")
    symptom_headache = st.checkbox("Приступ тревоги")

    # 6. Описание
    description_val = st.text_area("Описание", placeholder="Как прошел мой день...")

    if st.button("Сохранить запись", type="primary"):
        # Собираем все данные в один словарь (dict)
        new_entry = {
            "date": str(date_val), # Превращаем дату в текст, чтобы сохранить
            "anxiety": anxiety_val,
            "appetite": appetite_val,
            "sleep": sleep_val,
            "paralysis": symptom_paralysis,
            "headache": symptom_headache,
            "description": description_val
        }

        # Вызываем нашу функцию сохранения
        save_entry(new_entry)

        st.success("✅ Запись успешно сохранена в файл!")

    st.write("---")
    st.subheader("📚 Мои прошлые записи")

    # Проверяем, существует ли файл с данными
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        # Идем по записям с конца (чтобы свежие были сверху)
        for entry in reversed(saved_data):
            # Создаем раскрывающийся блок для каждой записи
            with st.expander(f"📅 {entry.get('date', 'Нет даты')} — Тревога: {entry.get('anxiety', '-')}/10"):
                st.write(f"**Аппетит:** {entry.get('appetite', '-')}")
                st.write(f"**Сон:** {entry.get('sleep', '-')}")

                # Собираем симптомы в кучу
                symptoms = []
                if entry.get('paralysis'): symptoms.append("Сонный паралич")
                if entry.get('headache'): symptoms.append("Головная боль")

                if symptoms:
                    st.write(f"**Симптомы:** {', '.join(symptoms)}")
                else:
                    st.write("**Симптомы:** нет")

                if entry.get('description'):
                    st.write(f"**Описание:** {entry.get('description')}")
    else:
        st.info("У вас пока нет записей. Заполните форму выше и нажмите 'Сохранить'!")

elif st.session_state["current_page"] == "Статистика":

    if st.button("← Назад на главную"):
        go_to("Главная")

    st.title("📊 Статистика")

    if not os.path.exists(DATA_FILE):
        st.info("Пока нет данных для графиков. Сначала добавьте записи в Дневник.")
    else:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            st.info("Файл с данными пуст. Добавьте записи.")
        else:
            # 1. Загружаем данные и превращаем в нормальные даты
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')

            # 2. Вычисляем начало недели (понедельник) для каждой записи
            # Метод .dt.to_period('W').dt.start_time берет понедельник этой недели
            df['week_start'] = df['date'].dt.to_period('W').dt.start_time

            # 3. Получаем список недель, за которые есть записи
            unique_weeks = df['week_start'].dt.date.unique()
            unique_weeks = sorted(unique_weeks, reverse=True) # от новых к старым

            # 4. Делаем выпадающий список
            week_options = []
            for w in unique_weeks:
                w_end = w + pd.Timedelta(days=6)
                w_str = f"{w.strftime('%d %b')} — {w_end.strftime('%d %b')}"
                week_options.append((w_str, w))

            selected_week_str = st.selectbox("Выберите неделю:", options=[opt[0] for opt in week_options])
            selected_week = next(opt[1] for opt in week_options if opt[0] == selected_week_str)

            # 5. Фильтруем данные строго за эту неделю
            df_week = df[df['week_start'].dt.date == selected_week].copy()

            # 6. Делаем подписи по оси X
            days_ru = {0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс'}
            df_week['day_name'] = df_week['date'].dt.dayofweek.map(days_ru)

            # Формируем заголовок
            start_date = selected_week.strftime('%d')
            end_date = (selected_week + pd.Timedelta(days=6)).strftime('%d %B')
            months_ru = {'October': 'октября', 'November': 'ноября', 'December': 'декабря',
                         'January': 'января', 'February': 'февраля', 'March': 'марта',
                         'April': 'апреля', 'May': 'мая', 'June': 'июня', 'July': 'июля',
                         'August': 'августа', 'September': 'сентября'}
            for eng, ru in months_ru.items():
                end_date = end_date.replace(eng, ru)
            title_text = f"{start_date}-{end_date}"

            # 7. Создаем "скелет" из 7 дней для оси X
            all_days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
            df_plot = pd.DataFrame({'day_name': all_days})

            # 8. Объединяем скелет с нашими отфильтрованными данными
            df_plot = pd.merge(df_plot, df_week[['day_name', 'anxiety', 'paralysis']], on='day_name', how='left')

            # 9. Строим график
            st.subheader("Уровень фоновой тревоги")
            fig_anxiety = px.line(
                df_plot,
                x='day_name',
                y='anxiety',
                markers=True,
                labels={'day_name': 'День недели', 'anxiety': 'Тревога'}
            )

            # 10. Настраиваем ось X
            fig_anxiety.update_xaxes(categoryorder='array', categoryarray=all_days)

            # 11. Добавляем звездочки (паралич)
            paralysis_days = df_plot[df_plot['paralysis'] == True]
            if not paralysis_days.empty:
                fig_anxiety.add_scatter(
                    x=paralysis_days['day_name'],
                    y=paralysis_days['anxiety'],
                    mode='markers',
                    marker=dict(symbol='star', size=15, color='red'),
                    name='Сонный паралич'
                )

            fig_anxiety.update_layout(
                title=title_text,
                yaxis_range=[0, 11],
                xaxis_title=None
            )
            st.plotly_chart(fig_anxiety, use_container_width=True)

            st.caption(f"Записей за эту неделю: {len(df_week)}")