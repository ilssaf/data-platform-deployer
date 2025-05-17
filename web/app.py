# streamlit_app.py

import streamlit as st
import yaml
import subprocess
import tempfile
import shutil
import os

st.set_page_config(page_title="Data Platform Deployer UI", layout="wide")
st.title("🛠 Data Platform Deployer (DPD)")

st.markdown("""
Это веб-интерфейс для CLI-инструмента `dpd`.
1. Заполните параметры проекта.
2. Нажмите «Сгенерировать и скачать».
3. Получите ZIP-архив с готовой директорией проекта.
""")

st.header("1. Параметры проекта")
project_name = st.text_input("Имя проекта (project.name)", value="data-platform")
project_version = st.text_input("Версия (project.version)", value="1.0.0")
project_description = st.text_area(
    "Описание (project.description)", height=68, value="Descritpion of the project"
)

st.header("2. Источники данных")

default_sources = [
    {"type": "postgres", "name": "psql_platform"},
    {"type": "s3", "name": "data_lake"},
]

n_sources = st.number_input(
    "Сколько источников добавить?",
    min_value=0,
    max_value=10,
    value=len(default_sources),
    step=1,
    key="n_sources",
)

sources = []
for i in range(n_sources):
    cols = st.columns([1, 2])

    if i < len(default_sources):
        d = default_sources[i]
    else:
        d = {"type": "postgres", "name": ""}

    src_type = cols[0].selectbox(
        f"Тип источника #{i + 1}",
        options=["postgres", "s3"],
        index=0 if d["type"] == "postgres" else 1,
        key=f"src_type_{i}",
    )

    src_name = cols[1].text_input(
        f"Имя источника #{i + 1}", value=d["name"], key=f"src_name_{i}"
    )

    sources.append({"type": src_type, "name": src_name})

st.header("3. Потоковые сервисы")
col1, col2 = st.columns(2)
num_brokers = col1.slider("Kafka: число брокеров", min_value=1, max_value=10, value=3)
connect_name = col2.text_input("Kafka Connect: имя", value="connect")

st.header("4. Хранилище и BI")
col3, col4 = st.columns(2)
ch_name = col3.text_input("ClickHouse: имя", value="ch")
superset_name = col4.text_input("Superset: имя", value="superset")

config = {
    "project": {
        "name": project_name,
        "version": project_version,
        "description": project_description,
    },
    "sources": sources,
    "streaming": {
        "kafka": {"num_brokers": num_brokers},
        "connect": {"name": connect_name},
    },
    "storage": {"clickhouse": {"name": ch_name}},
    "bi": {"superset": {"name": superset_name}},
}

st.header("5. Сгенерированный YAML-конфиг")
yaml_text = yaml.safe_dump(config, sort_keys=False, allow_unicode=True)
st.code(yaml_text, language="yaml")

if st.button("🚀 Сгенерировать и скачать проект"):
    try:
        with st.spinner("Генерация проекта…"):
            tmpdir = tempfile.TemporaryDirectory()
            cfg_path = os.path.join(tmpdir.name, "config.yaml")

            with open(cfg_path, "w", encoding="utf-8") as f:
                f.write(yaml_text)

            subprocess.run(
                ["dpd", "generate", "--config", cfg_path], cwd=tmpdir.name, check=True
            )

            project_dir = os.path.join(tmpdir.name, project_name)
            archive_base = os.path.join(tmpdir.name, project_name)
            zip_path = shutil.make_archive(
                base_name=archive_base,
                format="zip",
                root_dir=tmpdir.name,
                base_dir=project_name,
            )

        with open(zip_path, "rb") as fp:
            data = fp.read()
        st.success("Готово! Скачайте архив:")
        st.download_button(
            label="⬇️ Скачать ZIP",
            data=data,
            file_name=f"{project_name}.zip",
            mime="application/zip",
        )

    except subprocess.CalledProcessError as e:
        st.error(f"Ошибка при выполнении dpd: {e}")
    except Exception as e:
        st.error(f"Что-то пошло не так: {e}")
