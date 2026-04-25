[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/D69TCBIW)

# Project Name (tbd?)

This project aims to build an interactive web platform that enables banks and financial institutions to predict and detect money laundering activities using synthetic financial transaction data. By combining data exploration tools with machine learning, our product helps compliance teams identify suspicious transactions and understand laundering patterns, ultimately reducing false positives and catching more illicit activity.

### What Is Money Laundering?

Money laundering is the process by which criminals disguise the origins of illegally obtained funds through a series of financial transactions. It typically follows three stages:

Placement - Introducing illicit funds into the financial system (e.g., cash deposits from smuggling or illegal gambling).
Layering - Moving and mixing funds across accounts, banks, and entities to obscure their origin.
Integration - Spending the now-disguised funds as though they were legitimate.

Detection is extremely challenging: automated systems suffer from high false-positive rates (legitimate transactions flagged as suspicious) and high false-negative rates (actual laundering going undetected). Criminals continuously adapt their methods to evade detection.


### What is /projectname/?

We are building a data science platform that allows users to:

Interact with synthetic AML transaction data through a web interface

Explore transaction trends, patterns, and anomalies

Investigate relationships between accounts, entities, and laundering patterns

Predict the likelihood that a given transaction is laundering using machine learning.


#### Motivation

Anti-money laundering (AML) compliance is a critical concern for banks, regulators, and law enforcement worldwide. However, several challenges make AML research difficult:

Data access is restricted — Real financial transaction data is proprietary and privacy-sensitive, making it nearly impossible to obtain for research.

Labelling is unreliable — Even when real data is available, correctly tagging each transaction as laundering or legitimate is extremely difficult.

Models have limited scope — A single bank only sees its own transactions, missing the broader network of cross-institution laundering activity.


**This project aims to:**

Train and evaluate detection models on reliably labelled data

Study laundering patterns across an entire financial ecosystem (not just one bank's view)

Build models that understand the broad sweep of transactions across institutions, then apply those models to a single bank's transaction stream

Make AML insights accessible to non-technical compliance teams through interactive visualisations

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

-   Machine Learning ---\> hyperlink to a section describing the ML algorithm (maybe?)
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

-   Python 3.14

-   This project uses `uv` to ensure a reproducible and deterministic development environment.

-   To install dependencies:

    ```{bash}
    uv sync
    ```

------------------------------------------------------------------------

### Installation and Setup

Download the IBM AML dataset from Kaggle and place the CSV/TXT files in the data/ directory:
data/
├── HI-Small_Trans.csv
├── HI-Small_Patterns.txt
├── ...


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
anascrumit-aml/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── routes/               # Route blueprints (exploration, network, ML)
│   ├── models/               # ML model training and prediction
│   ├── templates/            # HTML templates
│   └── static/               # CSS, JS, images
├── data/                     # Dataset files (not committed)
├── notebooks/                # Exploratory analysis notebooks
├── tests/                    # Unit and integration tests
├── requirements.txt
├── config.py
└── README.md


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
