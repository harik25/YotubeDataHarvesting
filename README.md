# YouTube Data Harvesting Project

## Overview
This project focuses on harvesting data from YouTube using the YouTube API. The collected data is processed into a structured format, stored in a MySQL database, and visualized using a Streamlit application. The application provides an interactive interface to explore and analyze the data.

---

## Features
- **YouTube API Integration**: Extract detailed video and channel data directly from YouTube.
- **Data Processing**: Use `pandas` to clean, structure, and format data into a DataFrame for analysis.
- **Database Management**: Store the processed data in a MySQL database for efficient retrieval and storage.
- **Interactive Visualization**: Build a Streamlit app to visualize key insights and trends in the data.

---

## Technologies Used
- **Programming Language**: Python
- **Libraries**: 
  - `pandas` for data manipulation and analysis
  - `googleapiclient` for interacting with the YouTube API
  - `sqlalchemy` or `mysql-connector` for database operations
  - `streamlit` for app development
- **Database**: MySQL

---

## How It Works
1. **Data Extraction**:
   - Use the YouTube API to fetch video and channel details.
   - Extract data points such as title, views, likes, comments, and channel statistics.
2. **Data Processing**:
   - Clean and organize the extracted data into a DataFrame.
   - Perform necessary transformations for database storage and visualization.
3. **Data Storage**:
   - Insert processed data into a MySQL database.
   - Maintain efficient database structure for querying.
4. **Data Visualization**:
   - Create an interactive Streamlit dashboard.
   - Display metrics such as most-viewed videos, channel performance, and trends.

