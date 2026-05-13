[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/D69TCBIW)

# Project Name (tbd?)

This project aims to build an interactive web platform that enables banks and financial institutions to predict and detect money laundering activities using synthetic financial transaction data. By combining data exploration tools with machine learning, our product helps compliance teams identify suspicious transactions and understand laundering patterns, ultimately reducing false positives and catching more illicit activity.

### What Is Money Laundering?

Money laundering is the process by which criminals disguise the origins of illegally obtained funds through a series of financial transactions. It typically follows three stages:

Placement - Introducing illicit funds into the financial system (e.g., cash deposits from smuggling or illegal gambling).
Layering - Moving and mixing funds across accounts, banks, and entities to obscure their origin.
Integration - Spending the now-disguised funds as though they were legitimate.

Detection is extremely challenging: automated systems suffer from high false-positive rates (legitimate transactions flagged as suspicious) and high false-negative rates (actual laundering going undetected). Criminals continuously adapt their methods to evade detection.


### What is FRISK?

- We are building a data science platform that allows users to:

- Interact with synthetic AML transaction data through a web interface

- Explore transaction trends, patterns, and anomalies

- Investigate relationships between accounts, entities, and laundering patterns

- Predict the likelihood that a given transaction is laundering using machine learning.


#### Motivation

- Anti-money laundering (AML) compliance is a critical concern for banks, regulators, and law enforcement worldwide. However, several challenges make AML research difficult:

- Data access is restricted — Real financial transaction data is proprietary and privacy-sensitive, making it nearly impossible to obtain for research.

- Labelling is unreliable — Even when real data is available, correctly tagging each transaction as laundering or legitimate is extremely difficult.

- Models have limited scope — A single bank only sees its own transactions, missing the broader network of cross-institution laundering activity.


**This project aims to:**

- Train and evaluate detection models on reliably labelled data

- Study laundering patterns across an entire financial ecosystem (not just one bank's view)

- Build models that understand the broad sweep of transactions across institutions, then apply those models to a single bank's transaction stream

- Make AML insights accessible to non-technical compliance teams through interactive visualisations

------------------------------------------------------------------------

## Features

- Data Exploration
- Interactive filtering by:
   - Date range
   - Transaction currency and payment format
   - Sending/receiving bank
   - Transaction amount range
   - Timeline of transaction volumes and laundering activity
   - Geographic distribution of transactions across banks
    - Summary statistics dashboard (transaction counts, laundering rates, amount distributions)

-   Machine Learning
    -   We will implement a **predictive algorithm** to estimate the likelihood that an entity becomes sanctioned more than once.
    -   Custom-built ML algorithm (from scratch)
    -   Feature engineering based on:
        -   Country
        -   Transaction type
        -   Connectivity metrics
    -   Prediction of “repeat offender” probability
    -   Model evaluation metrics

------------------------------------------------------------------------

## Getting Started

This section explains how to install, configure, and run the project locally, as well as how the repository is structured and how the system components interact.

------------------------------------------------------------------------

### System Requirements

-   macOS / Linux / Windows supported

-   Python 3.11

-   This project uses `uv` to ensure a reproducible and deterministic development environment.

-   To install dependencies:

    ```{bash}
    uv sync
    ```
-   To install required pacakges:

    ```{bash}
   uv pip install -r requirements.txt
    ```

------------------------------------------------------------------------

### Installation and Setup

Download the IBM AML dataset from Kaggle and place the CSV/TXT files in the data/ directory:
data/
├── HI-Small_Trans.csv
├── HI-Small_Patterns.txt


#### Packages used

The project relies on the following core libraries:

-   uv – Dependency management
-   Pandas – Data manipulation
-   NumPy – Numerical computation
-   Flask – Web framework
-   Pytest – Testing framework

### Running the Application

To start the Flask server:

```{bash}
python run.py
```

The application will be available at:

```         
http://localhost:5000
```

------------------------------------------------------------------------

## Repository Architecture

The repository follows a modular layered architecture:

```         
project-scrumit/
├── analysis/
│   ├── cleaning/          # data cleaning & aggregation
│   ├── features/          # ML preprocessing pipeline
│   ├── models/            # trained ML models & notebooks
│   └── visuals/           # Plotly chart functions
├── app/
│   ├── __init__.py        
│   ├── config.py
│   ├── routes/            # Flask route blueprints
│   ├── services/          # ML prediction services
│   ├── static/            # pre-computed charts & map data
│   │   ├── charts/        
│   │   ├── map/           
│   │   └── images/
│   └── templates/         # HTML templates
├── src/                   # helper functions & data pipeline
├── data/                  # raw/ and processed/ CSVs (not committed)
├── tests/                 # unit and integration tests
├── main.py                # pre-computes all charts & map data
├── run.py                 # start Flask server
├── pyproject.toml
└── README.md
```

*For more information about the the layered system design please consult [our wiki](https://github.com/hertie-dsa-26/project-scrumit/wiki/Layered-System-Design)*

### Execution Flow

When a user interacts with the application:

1.  A request is received by a Flask route.
2.  The route calls the orchestration layer.
3.  The orchestration layer:
    -   Loads processed data if needed
    -   Applies feature engineering
    -   Executes the machine learning algorithm
4.  Results are returned to the route.
5.  Templates render the final output.

This flow ensures strict separation between computation and presentation.

------------------------------------------------------------------------

## Design Principles

The architecture prioritizes:

-   Modularity
-   Testability
-   Clear dependency direction
-   Separation of concerns
-   Reproducibility

The analytical engine (`analysis/`) operates independently from the web interface (`app/`), allowing the system to be extended or refactored without tightly coupling components.

------------------------------------------------------------------------

## Machine Learning Model Files

This section describes all files involved in implementing the QDA-based AML detection model:

### Model Development & Training

-   **`analysis/models/retrain_qda_artifact.py`** – Main model training script. Loads preprocessed data, applies SMOTE for class imbalance handling, trains the custom QDA model, and saves the trained model artifact for deployment.

-   **`analysis/models/feature_importance.py`** – Computes permutation feature importance scores for the trained QDA model using recall as the evaluation metric. Helps identify which features most influence predictions.

-   **`analysis/models/QDA_model.ipynb`** – Development notebook for the Quadratic Discriminant Analysis model. Contains model design, training process, and initial evaluation (main notebook for replication).

-   **`analysis/models/QDA_recall_comparison.ipynb`** – Evaluation notebook comparing model performance across different threshold values and examining recall-precision tradeoffs.

### Visualization & Analysis

-   **`src/ml_run.py`** – Utilities for model inference and result formatting. Contains helpers for confidence score conversion, metric formatting, and prediction validation for API responses.


### Model Architecture & Core Algorithm

-   **`app/services/custom_qda.py`** – Custom implementation of the Quadratic Discriminant Analysis (QDA) classifier. Implements fit() for training and predict_proba() for generating probability estimates. Includes regularization parameter to improve numerical stability.

-   **`src/utils.py`** – Shared utility functions including API response formatting, input validation, model loading/caching, and prediction logging. Critical for integrating the trained model into the Flask application.

### Model Artifacts (Serialized Objects)

-   **`analysis/models/custom_qda_model_for_flask.pkl`** – Trained QDA model serialized with joblib. Contains learned class priors, means, and covariance matrices. Loaded by the prediction service for inference.

-   **`analysis/features/pycaret_preprocessing_pipeline.pkl`** – PyCaret preprocessing pipeline serialized with joblib. Handles feature scaling, encoding, and transformations. Applied to raw transaction features before model prediction.

-   **`analysis/models/feature_importance_results.pkl`** – Pre-computed permutation feature importance scores cached for the frontend. Contains feature names, importance means, and standard deviations.

### Application Layer (Flask Integration)

-   **`app/services/prediction_service.py`** – MoneyLaunderingPredictor class that orchestrates the prediction pipeline. Loads the trained model and preprocessing artifacts, accepts raw transaction data, applies preprocessing, and returns probability scores for money laundering.

-   **`app/services/feature_service.py`** – FeatureImportanceService class that loads and serves cached feature importance results. Provides top-N features ranked by importance for frontend visualization.

-   **`app/services/imputation_service.py`** – FeatureImputationService class that handles missing transaction features using sensible defaults. Provides mode values for categorical features and median/mean values for numerical features from the training data.

-   **`app/routes/ml.py`** – Flask blueprint defining the ML dashboard route. Serves the ml.html template at `/ml` endpoint.

-   **`app/routes/api.py`** – Flask blueprint defining ML API endpoints: `/api/health` (service status), `/api/predict` (transaction scoring), `/api/feature-importance` (top features). Handles request validation and response formatting.

-   **`app/templates/ml.html`** – Frontend template for the interactive ML dashboard. Contains UI for transaction input, prediction display, feature importance visualization, and model metadata. Communicates with backend via JavaScript/fetch API calls.

------------------------------------------------------------------------

# Acknowledgements

-   IBM — For creating and releasing the synthetic AML transaction dataset

------------------------------------------------------------------------

## The ScrumIt Team

<div style="text-align:center; margin-top:20px;">

<div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 20px; max-width: 900px; margin: 20px auto;">

<a href="https://github.com/adjicisse1" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; flex: 0 0 calc(33.333% - 20px);">
  <img src="https://github.com/adjicisse1.png"
       style="width:80px; height:80px; border-radius:50%; display:block; margin:auto; object-fit: cover;">
  <div style="font-size:0.85em; margin-top:6px;">Adji Bousso</div>
</a>

<a href="https://github.com/atulbharti1" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; flex: 0 0 calc(33.333% - 20px);">
  <img src="https://github.com/atulbharti1.png"
       style="width:80px; height:80px; border-radius:50%; display:block; margin:auto; object-fit: cover;">
  <div style="font-size:0.85em; margin-top:6px;">Atul Bharti</div>
</a>

<a href="https://github.com/ngpbruno" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; flex: 0 0 calc(33.333% - 20px);">
  <img src="https://github.com/ngpbruno.png"
       style="width:80px; height:80px; border-radius:50%; display:block; margin:auto; object-fit: cover;">
  <div style="font-size:0.85em; margin-top:6px;">Bruno Galvao</div>
</a>

<a href="https://github.com/sbreganni" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; flex: 0 0 calc(25% - 20px);">
  <img src="https://github.com/sbreganni.png"
       style="width:80px; height:80px; border-radius:50%; display:block; margin:auto; object-fit: cover;">
  <div style="font-size:0.85em; margin-top:6px;">Sofia Breganni</div>
</a>

<a href="https://github.com/ecassibry" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; flex: 0 0 calc(25% - 20px);">
  <img src="https://github.com/ecassibry.png"
       style="width:80px; height:80px; border-radius:50%; display:block; margin:auto; object-fit: cover;">
  <div style="font-size:0.85em; margin-top:6px;">Elizabeth Cassibry</div>
</a>

<a href="https://github.com/fenja-klockgether" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; flex: 0 0 calc(25% - 20px);">
  <img src="https://github.com/fenja-klockgether.png"
       style="width:80px; height:80px; border-radius:50%; display:block; margin:auto; object-fit: cover;">
  <div style="font-size:0.85em; margin-top:6px;">Fenja Klockgether</div>
</a>

<a href="https://github.com/Jishnu-Verma" style="display: flex; flex-direction: column; align-items: center; text-decoration: none; flex: 0 0 calc(25% - 20px);">
  <img src="https://github.com/Jishnu-Verma.png"
       style="width:80px; height:80px; border-radius:50%; display:block; margin:auto; object-fit: cover;">
  <div style="font-size:0.85em; margin-top:6px;">Jishnu Verma</div>
</a>

</div>

</div>
