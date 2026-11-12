
# 📈 InstallScope – Play Store Growth Atlas

## 1. Project Overview

InstallScope – Play Store Growth Atlas is a data visualization project developed using Python and Streamlit.

The main objective of this project is to analyze Google Play Store applications based on their ratings, reviews, app size, categories, and installs.

The project uses a stacked area chart to visualize cumulative installs across different app categories. It also identifies months where installs increase by more than 25% compared to the previous month.

The dashboard provides an attractive and interactive user interface with category filters, KPI cards, application details, and category-wise install comparisons.

## 2. Objectives

- Analyze Google Play Store application data.
- Apply multiple conditions to filter applications.
- Visualize cumulative installs using a stacked area chart.
- Identify category-wise install growth.
- Highlight months with more than 25% growth.
- Display category names in different languages.
- Restrict chart visibility to a specific time window (4 PM to 6 PM IST).
- Build an interactive analytics dashboard using Streamlit.

## 3. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Dashboard development |
| Pandas | Data manipulation |
| NumPy | Numerical calculations |
| Plotly | Interactive visualizations |
| CSS | Dashboard styling |

## 4. Project Structure

```text
PlayStore_Install_Insights/
│
├── app.py
│
├── requirements.txt
│
├── README.md
│
└── data/
    └── Play Store Data.csv
```

### File Description

- `app.py` – Main Streamlit application.
- `requirements.txt` – Contains the required Python libraries.
- `README.md` – Project documentation.
- `data/Play Store Data.csv` – Google Play Store dataset.

Note: The User Reviews.csv dataset is not required for the current visualization.

## 5. Dataset Description

The project uses the Google Play Store dataset.

Important columns include:

- App – Application name.
- Category – Application category.
- Rating – Average application rating.
- Reviews – Number of user reviews.
- Size – Application size.
- Installs – Number of application installs.
- Last Updated – Last update date of the application.

The dataset is used to identify applications that satisfy the given filtering conditions.

## 6. Data Filtering Conditions

The following five conditions are applied before visualization.

| Condition | Requirement |
|---|---|
| Average Rating | At least 4.2 |
| App Name | Must not contain numbers |
| App Category | Must start with T or P |
| Reviews | Greater than 1,000 |
| App Size | Between 20 MB and 80 MB |

Applications that do not satisfy these conditions are excluded.

Unknown and variable app sizes are also excluded.

## 7. Category Name Translation

The following category names are translated in the chart legend.

| Original Category | Translated Name | Language |
|---|---|---|
| Travel & Local | Voyages et lieux | French |
| Productivity | Productividad | Spanish |
| Photography | 写真 | Japanese |

Other categories retain their original English names.

## 8. Stacked Area Chart

The main visualization is a stacked area chart created using Plotly.

Each application category is represented using a separate color band.

The chart displays cumulative installs over time.

### Chart Features

- Different colors for different categories.
- Cumulative installation calculation.
- Monthly grouping.
- Interactive hover information.
- Category-wise comparison.
- Growth highlighting.

## 9. Monthly Growth Detection

The application calculates month-over-month growth separately for each category.

When the install total of any category increases by more than 25% compared to the previous month, that month is highlighted.

### Growth Formula

Growth Percentage =

((Current Month Installs - Previous Month Installs) / Previous Month Installs) × 100

Months with growth above 25% are highlighted using amber-colored bands and diamond markers.

## 10. Time-Based Chart Visibility

One of the special features of this project is time-based visualization.

The stacked area chart is displayed only during the following time window:

- Start Time: 4:00 PM IST
- End Time: 6:00 PM IST
- Time Zone: Asia/Kolkata

Outside this time window, the chart is not displayed on the dashboard.

A message indicates that the visualization is currently locked.

The remaining dashboard sections stay accessible.

## 11. Dashboard Features

The dashboard includes:

1. **KPI Cards:** Display matching apps, categories, total listed installs, and growth alert months.

2. **Category Selection:** Allows users to select the application categories they want to analyze.

3. **Stacked Area Chart:** Displays cumulative installs across different categories.

4. **Growth Alerts:** Highlights months where any category experiences more than 25% growth.

5. **Filtered App Explorer:** Displays application names, ratings, reviews, sizes, and installs.

6. **Category Install Comparison:** Displays a category-wise install comparison using a horizontal bar chart.

7. **Multilingual Legend:** Displays selected category names in French, Spanish, and Japanese.

8. **Time-Based Access:** Restricts the main visualization to 4 PM–6 PM IST.

## 12. Installation and Setup

### Prerequisites

- Python 3.10 or above.
- Visual Studio Code.
- Internet connection for installing Python packages.

### Step 1: Clone or Extract the Project

Open the project folder in Visual Studio Code.

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment

For Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

For Git Bash:

```bash
source venv/Scripts/activate
```

### Step 4: Install Required Libraries

```bash
pip install -r requirements.txt
```

### Step 5: Run the Streamlit Application

```bash
streamlit run app.py
```

### Step 6: Open the Dashboard

Open the following address in your browser:

```text
http://localhost:8501
```

## 13. Expected Output

After successful execution, the application displays an interactive dashboard containing:

- InstallScope project heading.
- KPI cards.
- Category selection sidebar.
- Cumulative stacked area chart.
- Monthly growth alerts.
- Filtered application table.
- Category-wise install comparison.
- Project methodology.

The main chart is visible only between 4 PM and 6 PM IST.

## 14. Important Data Limitation

The supplied Google Play Store dataset contains current install ranges and application last-update dates. It does not contain actual historical monthly install records.

Therefore, the application assigns each app's current install count to its last-updated month, groups these values by category, and calculates cumulative totals.

This provides a last-updated-month-based estimate and should not be interpreted as actual historical monthly downloads or acquisition activity.

For genuine historical install analysis, dated install snapshots or Google Play Console acquisition records would be required.

## 15. Future Enhancements

- Integrate live application data.
- Add advanced machine learning-based install prediction.
- Develop additional category comparison charts.
- Add downloadable PDF reports.
- Add more interactive dashboard filters.
- Integrate sentiment analysis using user reviews.

## 16. Conclusion

InstallScope – Play Store Growth Atlas provides an interactive way to analyze Google Play Store application data.

By combining data filtering, cumulative install analysis, growth detection, multilingual category labels, and time-based chart visibility, the project demonstrates how Python and Streamlit can be used to develop an attractive and informative analytics dashboard.

---

**Project Name:** InstallScope – Play Store Growth Atlas

**Developed Using:** Python, Streamlit, Pandas, NumPy, Plotly

**Visualization:** Stacked Area Chart
