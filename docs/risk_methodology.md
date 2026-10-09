# Student Risk Analysis & Segmentation Methodology

> **Project:** Smart Campus Analytics: Predict, Optimize & Improve Student Success  
> **Phase:** Phase 2 — Data Integration, Success Scoring, Risk Analysis, and Personalized Insights  
> **Target Audience:** Students, Academic Counselors, Placement Coordinators  
> **Version:** 2.0.0 (Explainable Rule-Based Architecture)

---

## 1. Ethical & Explainable Framework

Predictive AI systems in higher education must be **interpretable, actionable, and non-stigmatizing**. Rather than deploying an opaque, untrained black-box classifier that makes unverified predictions about future outcomes, the Smart Campus Analytics platform implements an **explainable rule-based diagnostic engine**.

### Key Tenets:
1. **Clear Causality:** Every risk tier (High, Moderate, Low) is backed by explicit, auditable metrics that triggered the classification.
2. **Action-Oriented Diagnostics:** A risk flag is never surfaced without an accompanying, concrete recovery recommendation.
3. **Missing Data Distinction:** Pending assessments (e.g., upcoming mock interviews or unsubmitted optional surveys) are strictly isolated as informational notices and never conflated with poor performance.

---

## 2. Academic Risk Methodology

Academic Risk measures a student's vulnerability to academic probation, exam debarment, semester delays, or graduation stoppage.

### 2.1 Indicators and Trigger Thresholds

| Indicator | Critical Threshold (High) | Moderate Threshold | Safe Benchmark (Low) | Metric Source |
| :--- | :---: | :---: | :---: | :--- |
| **Active Backlogs** | $\ge 2$ backlogs | $= 1$ backlog | $0$ backlogs | `academic.csv` |
| **Cumulative GPA** | $< 5.50 / 10.0$ | $5.50 \le \text{CGPA} < 7.00$ | $\ge 7.00 / 10.0$ | `academic.csv` |
| **Overall Attendance** | $< 65.0\%$ (Debarment Risk) | $65.0\% \le \text{Att} < 75.0\%$ | $\ge 75.0\%$ | `attendance.csv` |
| **Assignment Completion** | $< 50.0\%$ | $50.0\% \le \text{Assign} < 70.0\%$ | $\ge 70.0\%$ | `lms_activity.csv` |
| **Failed Coursework** | $\ge 1$ subject marks $< 40$ | Minimum mark $40 - 49$ | Minimum mark $\ge 50$ | `academic.csv` |

### 2.2 Severity Classification Logic:
* **High Academic Risk:** Triggered if a student has:
  * $\ge 2$ active backlogs, **OR**
  * $\text{CGPA} < 5.50$, **OR**
  * Overall attendance $< 65.0\%$, **OR**
  * Assignment completion $< 50.0\%$, **OR**
  * Any active course marks $< 40.0$.
* **Moderate Academic Risk:** Triggered if a student does not meet High Risk conditions but has:
  * Exactly $1$ active backlog, **OR**
  * $\text{CGPA} \in [5.50, 7.00)$, **OR**
  * Overall attendance $\in [65.0\%, 75.0\%)$, **OR**
  * Assignment completion $\in [50.0\%, 70.0\%)$, **OR**
  * Any enrolled course with attendance $< 75.0\%$.
* **Low Academic Risk:** Meets or exceeds all safe benchmarks with $0$ backlogs, $\text{CGPA} \ge 7.00$, attendance $\ge 75\%$, and coursework completion $\ge 70\%$.

---

## 3. Placement Risk Methodology

Placement Risk evaluates a student's readiness to clear initial corporate screening filters (quantitative aptitude tests, algorithmic coding challenges) and technical/behavioral interview rounds.

### 3.1 Indicators and Trigger Thresholds

| Indicator | Critical Threshold (High) | Moderate Threshold | Competitive Target (Low)| Metric Source |
| :--- | :---: | :---: | :---: | :--- |
| **Placement Readiness Index**| $< 50.0 / 100$ | $50.0 \le \text{Score} < 70.0$ | $\ge 70.0 / 100$ | `placement.csv` |
| **Algorithmic Coding Score** | $< 50.0 / 100$ | $50.0 \le \text{Score} < 65.0$ | $\ge 65.0 / 100$ | `placement.csv` |
| **Quantitative Aptitude** | $< 50.0 / 100$ | $50.0 \le \text{Score} < 65.0$ | $\ge 65.0 / 100$ | `placement.csv` |
| **Technical Domain Skills** | $< 55.0 / 100$ | $55.0 \le \text{Score} < 70.0$ | $\ge 70.0 / 100$ | `skills.csv` |
| **Mock Interview Score** | $< 50.0 / 100$ | $50.0 \le \text{Score} < 65.0$ | $\ge 65.0 / 100$ | `placement.csv` |

### 3.2 Handling Missing Assessments:
* If `mock_interview_score` is `NaN`:
  * **Not a risk flag:** It is labeled `Assessment Pending: Diagnostic Mock Interview Required`.
  * The student receives a high-priority recommendation to book an interview slot rather than being labeled as failing.

---

## 4. Student Segmentation Matrix

Students are mapped into mutually exclusive segments along two primary axes:
1. **Academic Performance Score:** High ($\ge 75.0$), Moderate ($[65.0, 75.0)$), Low ($< 65.0$)
2. **Placement Readiness Score:** High ($\ge 75.0$), Moderate ($[65.0, 75.0)$), Low ($< 65.0$)

```text
               Placement Score:
               Low (< 65)               Moderate [65, 75)        High (>= 75)
            +------------------------+------------------------+------------------------+
High (>= 75)| Strong Academics,      | Strong Academics,      | Strong Academics,      |
            | Low Placement Readiness| Moderate Placement     | Strong Placement Read. |
Academic    +------------------------+------------------------+------------------------+
Mod [65, 75)| Needs Placement        | Consistent All-Rounder | Moderate Academics,    |
            | Preparation            |                        | Strong Placement Read. |
            +------------------------+------------------------+------------------------+
Low (< 65)  | Needs Improvement in   | Needs Academic         | Weak Academics,        |
            | Multiple Areas         | Improvement            | Strong Placement Read. |
            +------------------------+------------------------+------------------------+
```

### Segment Descriptions and Strategies:
1. **Strong Academics, Strong Placement Readiness:** Honors mentorship, high-tier product hackathons, dream company off-campus hiring.
2. **Strong Academics, Low Placement Readiness:** Intensive coding bootcamps, timed aptitude drills, and mock interview coaching.
3. **Weak Academics, Strong Placement Readiness:** Practical hackers/coders needing academic stabilization, backlog clearance tutoring, and attendance recovery.
4. **Needs Academic Improvement:** Sound technical skills but vulnerable course grades; prioritize core coursework revision.
5. **Needs Placement Preparation:** Solid coursework base; enroll in corporate recruitment training tracks.
6. **Needs Improvement in Multiple Areas:** Comprehensive academic advising, weekly mentor check-ins, remedial coursework, and foundational skill workshops.

---

## 5. Personalized Recommendation Algorithms

Each recommendation is generated dynamically with:
* **Category:** Coursework, Attendance, Coding, Aptitude, Interview, Engagement.
* **Priority Tier:** Critical $\rightarrow$ High $\rightarrow$ Medium $\rightarrow$ Low.
* **Current Value vs. Measurable Improvement Target:**

### Dynamic Attendance Target Calculation:
If a student has attended $A$ classes out of $T$ total scheduled classes, their current attendance is $P = \frac{A}{T}$.
To reach the statutory target of $75\%$ ($0.75$), the number of additional consecutive classes $x$ the student must attend without any absence is calculated as:

$$\frac{A + x}{T + x} \ge 0.75 \implies A + x \ge 0.75T + 0.75x \implies 0.25x \ge 0.75T - A \implies \mathbf{x = \left\lceil \frac{0.75T - A}{0.25} \right\rceil}$$

The recommendation displays the exact number of consecutive sessions needed.

---

## 6. Current Methodological Limitations

1. **Static Rules vs. Temporal Trajectories:** Current risk evaluation operates on the latest semester snapshot. As multi-semester historical time-series data becomes available, trend derivatives (e.g., $\Delta \text{CGPA} < -0.5$) will be integrated.
2. **Equal Thresholding Across Departments:** Certain departments (e.g., Mechanical vs. Computer Science) may have different industry recruitment coding requirements.
3. **Qualitative Nuance:** Faculty feedback and mentor qualitative notes are currently captured numerically on a 1.0–5.0 Likert scale. Future iterations will incorporate natural language processing (NLP) on textual mentor comments.
