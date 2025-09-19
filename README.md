# Civey-Sonntagsfrage: Data and small dashboard

A project to automatically track and visualize the German federal election poll data ("Sonntagsfrage") from Civey.

## 📊 Dashboard Features

The project includes a Streamlit web application that provides:

-   **Latest Poll Metrics:** Displays the most recent poll numbers for major parties, with a comparison to the results from one month prior.
-   **Interactive Trend Chart:** A line chart showing the polling trends over time. Users can select which parties to display.
-   **Raw Data View:** An expandable section to view the underlying raw data table.

## ⚙️ How It Works

The project consists of three main components:

1.  **`get_data.py`:** A Python script that fetches the latest poll data from the public Civey API, transforms it, and appends it to `data.csv`.
2.  **`.github/workflows/update_data.yml`:** A GitHub Actions workflow that runs the `get_data.py` script daily. It then commits and pushes the updated `data.csv` back to the repository.
3.  **`app.py`:** A Streamlit application that reads `data.csv` and presents the data in an interactive dashboard.
