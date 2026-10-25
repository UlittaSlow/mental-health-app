import streamlit as st
import json
import os
import pandas as pd

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

# Создаем боковое меню для навигации (Экран 1)
st.sidebar.title("Навигация")
menu = st.sidebar.radio("Куда пойдем?", ["Главная", "Дневник эмоций", "Статистика"])

# Логика переключения экранов
if menu == "Главная":
    st.title("🌱 Ментальное здоровье")
    st.write("Добро пожаловать! Это твой личный дневник.")

    # Просто большие кнопки-заглушки для главного экрана
    if st.button("📖 Дневник эмоций", use_container_width=True):
        st.info("Тут мы потом сделаем переход на форму. А пока нажми 'Дневник эмоций' в меню слева 👈")

    if st.button("📊 Статистика", use_container_width=True):
        st.info("Тут будут графики. Пока нажми 'Статистика' в меню слева 👈")

elif menu == "Дневник эмоций":
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

elif menu == "Статистика":
    st.title("📊 Статистика")
    st.write("Здесь скоро появятся графики.")