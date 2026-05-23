# PacketMatch — WE Package Recommendation System

<div >

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Web Scraping](https://img.shields.io/badge/Web_Scraping-Data_Collection-4CAF50?style=for-the-badge)
![Pandas](https://img.shields.io/badge/-Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Seaborn](https://img.shields.io/badge/-Seaborn-4C72B0?style=for-the-badge&logo=seaborn&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/-Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![TensorFlow](https://img.shields.io/badge/-TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-brightgreen?style=for-the-badge)
![Dataset](https://img.shields.io/badge/Dataset-WE%20Data-blue?style=for-the-badge)
</div>

---

## Project Overview

PacketMatch is an intelligent Machine Learning-powered recommendation system designed to help WE internet users select the most suitable internet package based on their real usage behavior and consumption patterns.

The project addresses a real-world problem faced by many internet users in Egypt: internet bundles running out unexpectedly before month-end, resulting in extra costs and poor user experience.

The system analyzes user behavior such as:
- Daily internet consumption
- Number of connected devices
- Usage type
- Remaining quota
- Billing cycle information

Then predicts the optimal WE internet package using a trained XGBoost classification model.

The project combines Web Scraping, Synthetic Data Generation, Feature Engineering, Machine Learning, and Interactive Streamlit Deployment.

---

## Problem Statement

Many WE internet users in Egypt struggle with:

- Internet packages running out before the end of the month
- No clear visibility into where data consumption is going
- Unexpected spikes in usage leading to confusion and frustration
- Paying unnecessary extra bundle costs without understanding why
- Difficulty choosing the right package from available options

**Users are not struggling with lack of data plans —
they are struggling with lack of visibility and control over their internet usage.**

---

## Proposed Solution

PacketMatch transforms raw internet usage data into personalized package recommendations using Machine Learning.

The system:
- Analyzes user internet behavior
- Detects inefficient consumption patterns
- Predicts the most suitable package
- Helps reduce extra bundle costs
- Supports smarter internet usage decisions

![Home](images/home.png)
![Recommendation](images/result.png)

---

## Project Structure

```
PacketMatch/
│
├── data/                       
│   ├── WE_centrals.xlsx
│   ├── WE_Dataset.csv
│   └── we_plans.xlsx
│
├── models/                     
│   ├── we_model.pkl
│   ├── we_feature_cols.pkl
│   ├── we_pkg_le.pkl
│   └── we_target_le.pkl
│
├── notebooks/                  
│   └── WE_Analysis_Notebook.ipynb
│
├── scrapers/                    
│   ├── Centrals_Scraper.py
│   └── Packages_Scraper.py
│
├── utils/                      
│   └── WE_Dataset_Generator_v6.py
│
├── images/                      
│   ├── Package Information.png
│   └── Recommender.png
│
├── user_app.py                  
├── style.css
└── requirements.txt
```

---

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core language |
| Pandas & NumPy | Data processing |
| BeautifulSoup | Web scraping |
| Scikit-learn | Preprocessing & evaluation |
| XGBoost | ML classification model |
| Streamlit | Web app deployment |
| Matplotlib & Seaborn | Data visualization |

---

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/PacketMatch.git
cd PacketMatch
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run user_app.py
```
---
