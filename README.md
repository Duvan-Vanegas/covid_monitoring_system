# 🦠 COVID Monitoring System

Es un sistema automatizado de extracción, transformación, carga y visualización de datos globales sobre el COVID-19. Utiliza Airflow, SQLite y Streamlit, todo orquestado con Docker, para procesar datos diarios desde la API [disease.sh](https://disease.sh).

---

## 📂 Estructura del proyecto

```
covid_monitoring_system/
├── dags/                      # DAG de Airflow
├── data/
│   ├── covid.db               # Base de datos SQLite
│   ├── raw/                   # Datos JSON originales extraídos de la API
│   │   ├── countries.json
│   │   └── historical.json
│   └── processed/             # Datos CSV ya transformados
│       ├── current_data.csv
│       └── historical_data.csv
├── data_processing/
│   ├── extract.py             # Extracción de la API
│   ├── transform.py           # Limpieza y conversión
│   └── load.py               # Carga en SQLite
├── dashboard/
│   └── app.py               # Dashboard con Streamlit
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## ⚙️ Tecnologías usadas

* Python 3.10+
* Docker & Docker Compose
* Apache Airflow 2.7.2
* SQLite
* Streamlit
* Altair, Pydeck, Pandas
* API [disease.sh](https://disease.sh)

---

## 🚀 Instalación rápida

```bash
git clone https://github.com/tuusuario/covid_monitoring_system.git
cd covid_monitoring_system
docker-compose up --build
```

Luego crear el usuario administrador de Airflow:

```bash
docker exec -it covid_monitoring_system-webserver-1 airflow users create \
  --username admin \
  --firstname @name \
  --lastname @lastname \
  --role Admin \
  --email email@example.com \
  --password admin123
```

Ejecutar el dashboard:

```bash
cd dashboard
streamlit run app.py
```
---

## ⚒️ Instalación manual con entorno virtual (sin Docker)

### 1. Clona el repositorio

```bash
git clone https://github.com/tuusuario/covid_monitoring_system.git
cd covid_monitoring_system
```

### 2. Crea y activa un entorno virtual

- En **Windows**:
```bash
python -m venv env
env\Scripts\activate
```

- En **Linux / macOS**:
```bash
python3 -m venv env
source env/bin/activate
```

### 3. Instala las dependencias del proyecto

```bash
pip install -r requirements.txt
```

### 4. Ejecuta el pipeline ETL manualmente

```bash
python data_processing/extract.py
python data_processing/transform.py
python data_processing/load.py
```

### 5. Abre el dashboard en Streamlit

```bash
cd dashboard
streamlit run app.py
```

> El dashboard se abrirá automáticamente en tu navegador: http://localhost:8501

---

## 🌐 Panel de visualización

* ✅ KPIs globales (casos, muertes, activos, recuperados)
* 📅 Evolución temporal interactiva
* 🌍 Mapa mundial de casos activos
* 📊 Comparativa por país (gráfico + tabla)
* 🏆 Top 10 países con más casos acumulados

---

## 🚪 Automatización ETL con Airflow

El DAG `covid_etl_dag` corre todos los días a las **8:00 a.m. UTC** y sigue este orden:

```text
extract_data ➔ transform_data ➔ load_data
```

---

## ✅ Consideraciones

* El mapa mundial utiliza coordenadas (lat, long) guardadas en la base de datos.
* Los datos se actualizan a diario desde la API disease.sh.

---

## 👨‍💼 Autor

**Duvan Vanegas**
Estudiante de Ingeniería de Software
[duvan.vanegas741@pascualbravo.edu.co](mailto:duvan.vanegas741@pascualbravo.edu.co)
