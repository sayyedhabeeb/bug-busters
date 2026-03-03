# EDA Report — Bug Busters

Datasets: **166 resumes** · **7718 jobs** · **296 skills**

---

## Resumes
- Categories: 25
- Avg word count: 402.8
- Avg skills matched: **9.49**
- Resumes with 0 skills: 0

## Jobs
- Categories covered: 0
- Avg word count: 533.3
- Avg skills per job: 15.11

## Skills
- Total: **296**
- Top 5 in resumes: ['gin', 'sql', 'java', 'oop', 'python']
- Top 5 in jobs: ['gin', 'java', 'sql', 'aws', 'agile']

## Labels
- Current positive: 2 (0.0%)
- Expected positive after re-run: **0** (~4.2%)

## Category Coverage
- Categories with both resumes & jobs: **0**
- Missing jobs: ['Advocate', 'Arts', 'Automation Testing', 'Blockchain', 'Business Analyst', 'Civil Engineer', 'Data Science', 'Database', 'DevOps Engineer', 'DotNet Developer', 'ETL Developer', 'Electrical Engineering', 'HR', 'Hadoop', 'Health and fitness', 'Java Developer', 'Mechanical Engineer', 'Network Security Engineer', 'Operations Manager', 'PMO', 'Python Developer', 'SAP Developer', 'Sales', 'Testing', 'Web Designing']

## Charts  (outputs/reports/eda/)
| # | File | What it shows |
|---|------|---------------|
| 01 | 01_resume_category_count.png      | Resume count per category |
| 02 | 02_resume_text_length.png         | Word & char length histograms |
| 03 | 03_resume_skills_per_category.png | Avg skill matches per category |
| 04 | 04_resume_skill_count_hist.png    | Skill count histogram |
| 05 | 05_resume_wordcount_boxplot.png   | Word count boxplot by category |
| 06 | 06_job_category_count.png         | Job postings per category |
| 07 | 07_job_wordcount_by_category.png  | Avg job description word count |
| 08 | 08_job_skills_per_category.png    | Avg skills per job category |
| 09 | 09_top25_skills_resumes.png       | Top 25 skills in resume corpus |
| 10 | 10_top20_skills_jobs.png          | Top 20 skills in job descriptions |
| 11 | 11_skill_domain_pie.png           | Skill domain breakdown (pie) |
| 12 | 12_skill_heatmap.png              | Skill presence heatmap |
| 13 | 13_feature_distributions.png     | All 10 feature histograms |
| 14 | 14_feature_correlation.png       | Feature correlation heatmap |
| 15 | 15_feature_boxplots.png           | Feature boxplots (outliers) |
| 16 | 16_feature_pairplot.png           | Pairplot coloured by label |
| 17 | 17_label_distribution.png         | Label pie + bar chart |
| 18 | 18_features_by_label.png          | Feature distributions by label |
| 19 | 19_expected_labels_by_category.png| Expected positive labels (new) |
| 20 | 20_dataset_overview.png           | Dataset sizes summary |
| 21 | 21_resume_vs_job_coverage.png     | Resume vs job category coverage |