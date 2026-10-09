# Smart Campus Analytics

**Predict, Optimize & Improve Student Success**

## About the Project

Smart Campus Analytics is a student-focused web application that helps students understand their academic performance and improve their placement preparation.

It brings student information from different areas into one platform and uses analytics to identify strengths, weaknesses, and areas that need improvement.

## Key Features

* **Student Dashboard:** View important student performance details in one place.
* **Academic Performance:** Track CGPA, subject marks, and backlogs.
* **Attendance Tracking:** Monitor overall and subject-wise attendance.
* **LMS & Engagement:** Review assignment completion, learning activity, and participation.
* **Placement Readiness:** Track aptitude, coding, and mock interview scores.
* **Student Success Score:** Understand overall performance through a weighted score.
* **Risk Analysis:** Identify possible academic and placement difficulties.
* **AI Insights & Recommendations:** Receive suggestions based on identified performance gaps.
* **Improvement Plan:** Track progress on recommended activities.
* **Student Segmentation:** Classify performance patterns using defined rules.

## Technology Stack

* **Frontend:** React.js, Vite, Tailwind CSS, Recharts
* **Backend:** Python, FastAPI
* **Database:** SQLite for the current local authentication setup
* **Data Analysis:** Pandas, NumPy, Scikit-learn where applicable

## How It Works

1. Student information is collected from academic, attendance, LMS, engagement, placement, skills, and feedback datasets.
2. The data is cleaned and combined using a common student identifier.
3. The application calculates the Student Success Score using defined weights.
4. Risk rules identify areas where a student may need support.
5. The dashboard displays performance insights and personalized improvement suggestions.

## Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/navyatungala04/smart-campus-analytics.git
cd smart-campus-analytics
```

### 2. Start the backend

Install the Python dependencies listed in the project's dependency file, configure the environment variables if required, and start the FastAPI application using the commands documented in the backend setup instructions.

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Open the local URL displayed in the terminal.

Refer to the project setup instructions for the exact backend command, database initialization, and environment configuration.

## Dataset

The project includes demonstration datasets for the seven student data categories. Synthetic demonstration data should not be treated as real institutional student records.

## Project Documentation

Additional documentation is available in the `docs` folder, including:

* Dataset documentation
* Student Success Score methodology
* Risk identification methodology
* Presentation slides

## Future Improvements

* Integration with institutional student information systems
* More advanced predictive analytics
* Additional learning resources and placement preparation tools
* Cloud deployment and production database integration

## Disclaimer

Risk indicators and recommendations are intended to support student improvement. They do not guarantee academic or placement outcomes.
