[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/D69TCBIW)

# FRISK

This project aims to build an interactive web platform that enables banks and financial institutions to predict and detect money laundering activities using synthetic financial transaction data. By combining data exploration tools with machine learning, our product helps compliance teams identify suspicious transactions and understand laundering patterns, ultimately reducing false positives and catching more illicit activity.

### What Is Money Laundering?

Money laundering is the process by which criminals disguise the origins of illegally obtained funds through a series of financial transactions. It typically follows three stages:

Placement - Introducing illicit funds into the financial system (e.g., cash deposits from smuggling or illegal gambling).
Layering - Moving and mixing funds across accounts, banks, and entities to obscure their origin.
Integration - Spending the now-disguised funds as though they were legitimate.

Detection is extremely challenging: automated systems suffer from high false-positive rates (legitimate transactions flagged as suspicious) and high false-negative rates (actual laundering going undetected). Criminals continuously adapt their methods to evade detection.


### What is FRISK?

We are building a data science platform that allows users to:

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

### System Requirements

-   macOS / Linux / Windows supported
-   Python 3.11
-   This project uses `uv` to ensure a reproducible and deterministic development environment.

-   To install dependencies:

    ```{bash}
    uv sync
    ```
-   Alternatively, to install required pacakges:

    ```{bash}
    pip install -r requirements.txt
    ```

------------------------------------------------------------------------

### Installation and Setup

Download the [IBM AML dataset](https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml) from Kaggle and place the CSV/TXT files in the data/ directory:

```
data/
├── HI-Small_Trans.csv
└── HI-Small_accounts.csv
```


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
uv run python run.py
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
├── analysis/              # archive with jupyter notebooks to track progress
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

The data cleaning and elaboration functions operate independently from the web interface, allowing the system to be extended or refactored without tightly coupling components.

------------------------------------------------------------------------

# Acknowledgements

-   IBM — For creating and releasing the synthetic AML transaction dataset

------------------------------------------------------------------------

## The ScrumIt Team

<table align="center" border="0" cellspacing="0" cellpadding="20">
  <tr>
    <td align="center"><a href="https://github.com/adjicisse1"><img src="https://github.com/adjicisse1.png" width="80" height="80" style="border-radius:50%"><br><sub>Adji Bousso</sub></a></td>
    <td align="center"><a href="https://github.com/atulbharti1"><img src="https://github.com/atulbharti1.png" width="80" height="80" style="border-radius:50%"><br><sub>Atul Bharti</sub></a></td>
    <td align="center"><a href="https://github.com/ngpbruno"><img src="https://github.com/ngpbruno.png" width="80" height="80" style="border-radius:50%"><br><sub>Bruno Galvao</sub></a></td>
    <td align="center"><a href="https://github.com/sbreganni"><img src="https://github.com/sbreganni.png" width="80" height="80" style="border-radius:50%"><br><sub>Sofia Breganni</sub></a></td>
    <td align="center"><a href="https://github.com/ecassibry"><img src="https://github.com/ecassibry.png" width="80" height="80" style="border-radius:50%"><br><sub>Elizabeth Cassibry</sub></a></td>
    <td align="center"><a href="https://github.com/fenja-klockgether"><img src="https://github.com/fenja-klockgether.png" width="80" height="80" style="border-radius:50%"><br><sub>Fenja Klockgether</sub></a></td>
    <td align="center"><a href="https://github.com/Jishnu-Verma"><img src="https://github.com/Jishnu-Verma.png" width="80" height="80" style="border-radius:50%"><br><sub>Jishnu Verma</sub></a></td>
  </tr>
</table>
