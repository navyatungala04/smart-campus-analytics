# Student Success Scoring Methodology

> **Project:** Smart Campus Analytics: Predict, Optimize & Improve Student Success  
> **Phase:** Phase 2 — Data Integration, Success Scoring, Risk Analysis, and Personalized Insights  
> **Target Audience:** Students, Academic Advisors, and Placement Mentors  
> **Formula Version:** 2.0.0 (Transparent Multi-Criteria Composite Index)

---

## 1. Executive Rationale & Objectives

The primary objective of the **Student Success Score** is to provide each student with an objective, holistic, and completely transparent metric reflecting their progress in the campus ecosystem. Rather than judging a student purely by exam grades, this composite index evaluates academic resilience, engagement, digital habits, career readiness, and mentor feedback.

### Guiding Principles:
1. **Student-Centric Transparency:** A student must be able to inspect every component of their score and understand precisely what actions will improve it.
2. **Comparable Normalization:** All disparate scales (such as 10-point CGPA, percentage attendance, login counts, and 5-point Likert ratings) are normalized to standard $[0, 100]$ score spaces.
3. **Equitable Missing Data Policy:** Missing optional assessments (e.g., pending mock interviews or unsubmitted feedback) are never penalized with arbitrary zero scores.
4. **Leakage & Double-Counting Prevention:** Distinct underlying metrics are used across categories to prevent collinearity or artificial inflation.

---

## 2. Category Weights & Justifications

The overall Student Success Score is a weighted linear combination of seven core dimensions:

$$\text{Student Success Score} = \sum_{i=1}^{7} W_i \times S_i$$

Where $W_i$ denotes the configurable category weight and $S_i$ denotes the normalized category score ($S_i \in [0, 100]$).

| Category Dimension | Weight ($W_i$) | Category Percentage | Core Rationale |
| :--- | :---: | :---: | :--- |
| **1. Academic Performance** | $0.25$ | **25%** | Academic standing (CGPA, marks, backlog clearance) is the foundational baseline for graduation and recruiter minimum cutoff eligibility. |
| **2. Attendance Tracking** | $0.15$ | **15%** | Direct proxy for class engagement, discipline, and compliance with statutory 75% exam eligibility rules. |
| **3. LMS Activity** | $0.10$ | **10%** | Measures continuous learning, proactive digital self-study, and consistency in submitting coursework assignments. |
| **4. Campus Engagement** | $0.10$ | **10%** | Evaluates co-curricular breadth, team-building in clubs, hackathon participation, and extracurricular initiative. |
| **5. Placement Readiness** | $0.20$ | **20%** | Directly reflects career transition potential, quantitative aptitude, algorithmic coding prowess, and interview readiness. |
| **6. Skills Profiling** | $0.12$ | **12%** | Measures technical domain competency and behavioral soft skills required in modern industry settings. |
| **7. Feedback & Mentorship**| $0.08$ | **8%** | Captures faculty mentor appraisals and student satisfaction to reflect advisory alignment and campus experience. |
| **Total** | **1.00** | **100%** | **Strict Mathematical Closure ($\sum W_i = 1.00$)** |

---

## 3. Sub-Component Normalization & Formulas

### 3.1 Academic Performance Score ($S_{\text{acad}} \in [0, 100]$)
Composed of three sub-indicators:
1. **Scaled CGPA ($C_{\text{scale}}$):** $\text{clip}(\text{CGPA} \times 10.0, 0, 100)$
2. **Average Subject Marks ($M_{\text{avg}}$):** Mean marks across enrolled semester subjects ($\in [0, 100]$).
3. **Backlog Clearance Score ($B_{\text{score}}$):** $\text{max}(0, 100 - (\text{backlogs} \times 25))$.
   * 0 backlogs = 100
   * 1 backlog = 75
   * 2 backlogs = 50
   * 3 backlogs = 25
   * 4+ backlogs = 0

$$\mathbf{S_{\text{acad}}} = 0.50 \times C_{\text{scale}} + 0.30 \times M_{\text{avg}} + 0.20 \times B_{\text{score}}$$

---

### 3.2 Attendance Tracking Score ($S_{\text{att}} \in [0, 100]$)
Derived from cumulative classes attended across all courses divided by total scheduled classes:

$$\mathbf{S_{\text{att}}} = \text{round}\left(\frac{\sum \text{classes\_attended}}{\sum \text{total\_classes}} \times 100, 2\right)$$

---

### 3.3 LMS Activity Score ($S_{\text{lms}} \in [0, 100]$)
Measures online engagement combining login volume and coursework submission:
1. **Login Score ($L_{\text{score}}$):** Benchmarked against 50 logins/month ($100\%$ active):
   $$L_{\text{score}} = \text{min}\left(100, \frac{\text{login\_frequency}}{50.0} \times 100\right)$$
2. **Assignment Completion Score ($A_{\text{comp}}$):** Percentage of completed mandatory assignments ($\in [0, 100]$).

$$\mathbf{S_{\text{lms}}} = 0.40 \times L_{\text{score}} + 0.60 \times A_{\text{comp}}$$

---

### 3.4 Campus Engagement Score ($S_{\text{eng}} \in [0, 100]$)
Measures collaborative and competitive involvement:
* **Events Score:** $\text{min}(100, (\text{events\_attended} / 8.0) \times 100)$ (Weight $20\%$)
* **Clubs Score:** $\text{min}(100, (\text{clubs\_participated} / 3.0) \times 100)$ (Weight $25\%$)
* **Hackathons Score:** $\text{min}(100, (\text{hackathons\_participated} / 4.0) \times 100)$ (Weight $30\%$)
* **Certifications Score:** $\text{min}(100, (\text{certifications\_count} / 3.0) \times 100)$ (Weight $15\%$)
* **Participation Tier:** High ($100$), Medium ($75$), Low ($40$) (Weight $10\%$)

$$\mathbf{S_{\text{eng}}} = 0.20 E + 0.25 C + 0.30 H + 0.15 \text{Cert} + 0.10 T$$

---

### 3.5 Placement Readiness Score ($S_{\text{place}} \in [0, 100]$)
Standard formulation with full data:

$$\mathbf{S_{\text{place}}} = 0.30 \times \text{Aptitude} + 0.40 \times \text{Coding} + 0.30 \times \text{Mock Interview}$$

#### Missing Data Treatment:
* If a student's mock interview has not yet been administered (pending schedule), treating it as $0$ would unfairly deduct up to 30 points.
* Instead, the system re-normalizes the sub-weights dynamically across the available components:
  * Aptitude Weight: $\frac{0.30}{0.30 + 0.40} = \frac{3}{7} \approx 42.86\%$
  * Coding Weight: $\frac{0.40}{0.30 + 0.40} = \frac{4}{7} \approx 57.14\%$
  * Interim Score: $S_{\text{place}} = \frac{3}{7} \times \text{Aptitude} + \frac{4}{7} \times \text{Coding}$
* The output dossier explicitly flags `mock_interview_pending: True` so the student understands that this sub-score is an interim projection.

---

### 3.6 Skills Profiling Score ($S_{\text{skills}} \in [0, 100]$)
Standard formulation:

$$\mathbf{S_{\text{skills}}} = 0.60 \times \text{Technical Skill Score} + 0.40 \times \text{Soft Skill Score}$$

#### Missing Data Treatment:
* When soft skills evaluations are pending, the technical skill score carries $100\%$ of the category score with `soft_skill_pending: True`.

---

### 3.7 Institutional Feedback Score ($S_{\text{feed}} \in [0, 100]$)
Scales ratings from $[1.0, 5.0]$ to $[0, 100]$ using $\text{Scaled} = \frac{\text{Rating} - 1.0}{4.0} \times 100$.
Standard formulation:

$$\mathbf{S_{\text{feed}}} = 0.60 \times \text{Faculty Mentorship} + 0.40 \times \text{Student Satisfaction}$$

#### Missing Data Treatment:
* When optional student satisfaction surveys are unsubmitted, the faculty mentorship rating carries $100\%$ of the category score with `satisfaction_survey_pending: True`.

---

## 4. Final Aggregation Example

Consider student **STU1001**:
* Academic Component: $75.25 \times 0.25 = 18.81$
* Attendance Component: $84.62 \times 0.15 = 12.69$
* LMS Component: $76.25 \times 0.10 = 7.63$
* Engagement Component: $68.50 \times 0.10 = 6.85$
* Placement Component: $75.40 \times 0.20 = 15.08$
* Skills Component: $74.50 \times 0.12 = 8.94$
* Feedback Component: $45.00 \times 0.08 = 3.60$
* **Final Success Score:** $\mathbf{73.62 / 100}$

---

## 5. Limitations & Future Directions

1. **Semester Weight Invariance:** Currently, semester standing does not alter category weights. For 4th-year students, placement readiness could be weighted higher (e.g., 30%), whereas for 2nd-year students, foundational coursework might be weighted at 35%.
2. **Linear Additivity Assumption:** While linear additive weights guarantee complete explainability, they assume mutual independence between categories.
3. **Synthetic Scale Calibrations:** Benchmark ceilings (e.g., 50 logins/month or 4 hackathons) are based on standard institutional targets and may be customized per department curriculum.
