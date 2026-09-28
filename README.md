# National Weather Big Data Analytics Platform

**Smart India Hackathon 2026 — Problem Statement 26069**

A national-scale weather analytics platform designed to collect, process, analyze, verify, and visualize real-time weather-related information across India using Big Data, AI/ML, NLP, and modern web technologies.

---

## 📌 Problem Statement

Develop a scalable platform for collecting and analyzing real-time weather information from multiple sources such as:

- Social media
- Public datasets
- Weather websites
- APIs
- Citizen reports

The platform is designed to process weather-related posts and reports containing relevant hashtags such as `#IMD`, along with metadata including date/time, city, state, GPS coordinates, photographs, videos, and event categories.

The system aims to help identify and analyze events such as:

- 🌧️ Heavy Rainfall
- ⛈️ Thunderstorms
- 🌊 Flooding
- 🌡️ Heatwaves
- 🌫️ Fog
- 🌪️ Dust Storms
- 💨 Strong Winds

---

## 🎯 Objectives

- Collect weather information from multiple heterogeneous sources.
- Build a centralized weather-event database.
- Process large-scale weather data using Big Data technologies.
- Detect duplicate and misleading reports.
- Classify weather events automatically.
- Extract locations and event information using NLP.
- Assign confidence and risk scores to detected events.
- Provide real-time weather visualization and analytics.
- Provide an administrative interface for event verification and monitoring.

---

## 🏗️ System Architecture

The platform is organized into the following major modules:

```text
Data Sources
     │
     ├── Social Media
     ├── Public Datasets
     ├── Weather APIs
     └── Citizen Reports
             │
             ▼
     Data Ingestion Layer
             │
             ▼
     Data Cleaning & Validation
             │
             ▼
       Big Data Processing
        Python / PySpark
             │
             ▼
      PostgreSQL Database
             │
       ┌─────┴─────┐
       ▼           ▼
   AI / NLP     REST API
       │           │
       └─────┬─────┘
             ▼
      React Web Dashboard
             │
       ┌─────┴─────┐
       ▼           ▼
 Public Dashboard  Admin Panel

 ## 🚀 Key Features

- Real-time weather event dashboard
- Interactive India weather map
- Weather event filtering
- Event intelligence and risk scoring
- AI confidence and insights
- Event timeline and analytics
- Current-location weather conditions
- Admin panel for event verification
- Support for rainfall, floods, heatwaves, thunderstorms, fog, dust storms, and strong winds

---

## 🛠️ Technology Stack

- **Frontend:** React, Vite, Tailwind CSS
- **Maps:** Leaflet
- **Backend:** FastAPI
- **Database:** SQLite
- **Data Processing:** Python, Pandas, Data Engineering Pipelines
- **Version Control:** Git & GitHub

---

## 📁 Repository Structure

```text
national-weather-big-data-platform/
├── data-engineering/
├── frontend/
├── sample_weather_events.json
├── .gitignore
└── README.md
## 🚀 Running Locally

### Backend Setup
```bash
cd backend
python -m venv venv
# Activate venv: `venv\Scripts\activate` on Windows, or `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
python seed.py  # Seed local SQLite database
python -m uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
Any sensitive API keys, JWT secrets, and database credentials should be stored in a `.env` file (which is gitignored). Never commit actual credentials.
