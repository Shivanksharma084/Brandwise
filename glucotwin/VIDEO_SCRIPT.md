# GlucoTwin Demo Video - Script

**Project:** GlucoTwin: Multi-Model Diabetes & Glucose Prediction Pipeline  
**Team:** Pardeep Kumar, Shivank Atri, Rohan Diwedi, Rakesh Yadav  
**College:** IMS Engineering College, Department of Computer Science & Engineering  
**Guide:** Prof. Amit Kumar  
**Total Duration:** ~18-20 minutes  
**Format:** MP4 (H.264, 1080p)

---

## 1. Introduction (2 min)

**[Slide: Team Photo + GlucoTwin Project Logo]**

> "Good day! We're Team GlucoTwin from IMS Engineering College. We're final year B.Tech students from the Department of Computer Science & Engineering, working under the guidance of Prof. Amit Kumar at our university's Healthcare AI Research Lab."

**[Cut to team members speaking in rotation]**

> "I'm Pardeep Kumar, Project Lead and ML Engineer. I built the machine learning pipeline."
> "I'm Shivank Atri, Backend Developer. I handled the data processing pipeline."
> "I'm Rohan Diwedi, Frontend Developer. I designed the interactive dashboard you're about to see."
> "And I'm Rakesh Yadav, Data Analyst. I conducted data analysis and model evaluation."

> "This project was developed as part of the Digital Twin Hackathon 2024, organized by the Healthcare AI Research Lab in collaboration with the IEC Innovation & Entrepreneurship Council."

> "Our goal was simple: to create a predictive diabetes management system that doesn't just show current glucose levels, but predicts future values based on historical data and lifestyle factors."

---

## 2. Problem Overview (2 min)

**[Slide: Global Diabetes Statistics]**

> "Let me share why this matters. Diabetes affects 537 million adults worldwide—that's 1 in 10 people."

**[Cut to dashboard or screen showing problem points]**

> "Current glucose monitoring systems face five critical gaps:"
>
> **First** - they're reactive, not predictive. They show what's happening now, not what will happen in the next hour.
> **Second** - most approaches use a single model, missing out on ensemble benefits.
> **Third** - data from wearables, meal logs, and insulin records remain disconnected in silos.
> **Fourth** - users often receive alerts only after glucose levels have already gone critical.
> **And fifth** - generic algorithms don't account for individual physiological differences."

> "GlucoTwin addresses these gaps by providing multi-horizon predictions (30, 60, 90, 120 minutes ahead), combining five ML architectures, integrating multiple data sources, offering calibrated ensemble predictions with confidence scores, and supporting hypoglycemia early warning."

---

## 3. System Demo (8 min)

**[Screen share: Open dashboard.html in browser]**

> "Let's walk through the dashboard. When you open it, you'll see our overview section showing four datasets and five model architectures."

**[Pointer to KPI cards]**

> "The first metric shows our four data sources: Smart Wearable, GlucoTwin, CGM T1DM/T2DM, and OHIM."
> "The second shows our five model architectures—Linear Regression, Random Forest, LightGBM, XGBoost, and GRU Neural Network."
> "The third card highlights our calibrated ensemble approach, which achieved an AUC of 0.984 on the OHIM dataset."
> "And the fourth shows our threshold sweep analysis—testing 20 different thresholds to find the optimal balance between sensitivity and specificity."

**[Point to Model Performance Chart]**

> "This chart displays model performance on test data. The x-axis shows each model, and the y-axis shows RMSE for regression tasks and AUC for classification. Notice how LightGBM and XGBoost perform best for regression, while all models achieve strong AUC scores for classification."

**[Navigate to Dataset Overview section]**

> "Each dataset serves a different purpose. The Smart Wearable dataset helps us understand lifestyle factors like BMI, blood pressure, and step count."
> "The GlucoTwin dataset contains real Dexcom CGM readings paired with meal carbs and insulin doses—critical for glucose prediction."
> "The CGM T1DM/T2DM dataset combines data from both diabetes types, making our models more generalizable."
> "And the OHIM dataset provides additional wearable glucose signals for ensemble calibration."

**[Click on a prediction tab or interactive element]**

> "Now let's look at the prediction interface. Here, users can input current glucose readings, meal information, and activity data to get forecasts."
> "The system predicts glucose levels at 30, 60, 90, and 120 minutes into the future—the multi-horizon prediction is one of our key innovations."

**[Show hypoglycemia warning section]**

> "This critical alert system notifies users when glucose might drop below 70 mg/dL in the next 60 minutes. For Type 1 diabetes patients, this could be life-saving."

---

## 4. ML Pipeline Deep Dive (5 min)

**[Slide: Architecture Diagram]**

> "Let's look under the hood. Our pipeline uses five distinct modeling approaches, each with unique strengths."

**[Explain the diagram]**

> "Linear Regression serves as our fast baseline. It's interpretable and gives us coefficient insights."
> "Random Forest captures non-linear interactions between features like age, BMI, and activity levels."
> "LightGBM, our fastest gradient booster, achieves excellent accuracy with leaf-wise tree growth."
> "XGBoost provides robust generalization, especially for outlier-prone real-world data."
> "And the GRU Neural Network—the only deep learning model—learns complex time-series patterns in glucose trends."

**[Show ensemble strategy]**

> "After training all five models, we apply isotonic regression to calibrate their outputs, then combine them using a weighted average."
> "This ensemble approach reduces variance and improves robustness. The OHIM calibrated ensemble achieved 0.984 AUC with 0.567 test F1 score after threshold optimization."

**[Explain threshold sweep]**

> "The threshold sweep is crucial for clinical applications. By testing 20 different decision thresholds, we identified the optimal balance between detecting true hypoglycemia and minimizing false alarms."

---

## 5. Technical Implementation (3 min)

**[Code snippets or architecture diagram]**

> "Our frontend uses pure HTML, CSS, and JavaScript with Chart.js for visualization. It's fully responsive and works across all modern browsers."
> "On the backend, we use Python with Pandas for data processing, scikit-learn for traditional ML, LightGBM and XGBoost for gradient boosting, and TensorFlow/Keras for the GRU network."

**[Show data flow diagram]**

> "The data pipeline works in four stages:"
>
> **First**, raw data ingestion from CSV files."
> **Second**, preprocessing—handling missing values, feature scaling, and time-series alignment."
> **Third**, model training with cross-validation across three stratified splits."
> **And fourth**, ensemble calibration and threshold optimization for clinical deployment."

> "All models are trained offline, and predictions happen in real-time within the dashboard without server calls."

---

## 6. Clinical Application (2 min)

**[Slide: Healthcare Provider Use Cases]**

> "This system is designed for two key user groups: patients and healthcare providers."

**[For Patients]**

> "Patients get 24-hour glucose forecasting, hypoglycemia early warnings, personalized insights about how meals and exercise affect their levels, and trend analysis over time."

**[For Healthcare Providers]**

> "Doctors can view aggregated patient data with consent, identify treatment patterns, stratify patient risk based on prediction confidence, and track how lifestyle interventions impact glucose control."

**[Show user personas]**

> "We designed for diverse needs—from young Type 1 diabetics managing exercise to elderly patients needing simple, clear alerts."

---

## 7. Q&A Preparation (1 min)

**[Slide: Common Questions]**

> "Let's address some questions you might have:"
>
> **Q: Is this clinically validated?**
> "We've designed the system to meet FDA Class II medical device data standards. Clinical validation is planned for our next phase."
>
> **Q: How accurate are the predictions?**
> "Our best ensemble achieves RMSE under 10% for 30-minute predictions. Accuracy degrades slightly for longer horizons, which is expected in glucose forecasting."
>
> **Q: Can this replace CGM devices?**
> "No—this complements CGM devices like Dexcom and Abbott by adding predictive value to the data they collect."
>
> **Q: How do you handle privacy?**
> "All data processing happens locally in the browser. Patient data never leaves the device."

---

## Closing (30 seconds)

**[End screen: Team names, college name, contact]**

> "GlucoTwin represents our vision for the future of diabetes management—predictive, personalized, and actionable."
>
> "Thank you for watching our presentation from Team GlucoTwin, IMS Engineering College!"

---

**Video Recording Details:**
- Format: MP4 (H.264, 1080p)
- Length: 18 minutes 45 seconds
- Speakers: All team members rotating segments
