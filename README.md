[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/D69TCBIW)

# Project Name (tbd?)

This project aims to create an easy-to-access, interactive web platform for exploring and analyzing data from the OpenSanctions database. Our product will allow businesses to make informed business decisions before going to a new market.

### What is OpenSanctions?

OpenSanctions is an open-source global sanctions dataset that aggregates information on sanctioned individuals, companies, organizations, and political entities from governments and international bodies around the world. It includes:

-   Names of sanctioned individuals and organizations
-   Associated countries
-   Sanction programs
-   Dates of designation
-   Entity types (person, company, vessel, etc.)
-   Relationships between entities

Sanctions datasets are critical for compliance, financial risk management, investigative journalism, and policy research.

### What is /projectname/?

We are building a mini data science platform that allows users to:

-   Interact with sanctions data through a web interface
-   Explore trends and patterns
-   Investigate entity relationships
-   Generate insights using machine learning

The application will be built using Flask and designed with clean architecture, modular code, and strong software engineering principles.

#### Motivation

Sanctions data plays a major role in:

-   Financial compliance
-   Anti-money laundering (AML)
-   Risk assessment
-   Corporate due diligence
-   International policy analysis

However, raw sanctions data is difficult to explore and analyze without technical expertise.

**This project aims to:**

-   Make sanctions data more accessible and understandable
-   Provide interactive exploration tools
-   Help businesses and researchers identify trends
-   Predict potential repeat sanctions using machine learning
-   Support better decision-making through data-driven insights

------------------------------------------------------------------------

## Features

-   Data Exploration
    -   Interactive filtering by:
        -   Country
        -   Entity type
        -   Sanction program
        -   Date
    -   Geographic distribution map
    -   Timeline of sanction additions
    -   Entity-type breakdown visualizations
    -   Summary statistics dashboard
-   Network Insights
    -   Exploration of entity connections
    -   Visualization of relationship networks
    -   Summary statistics of entity connectivity
    -   Identification of highly connected or influential entities
-   Machine Learning ---\> hyperlink to a section describing the ML algorithm (maybe?)
    -   We will implement a **predictive algorithm** to estimate the likelihood that an entity becomes sanctioned more than once.
    -   Custom-built ML algorithm (from scratch)
    -   Feature engineering based on:
        -   Country
        -   Entity type
        -   Connectivity metrics
        -   Historical sanction timing
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

We use the OpenSanctions Sanctions dataset:

<https://www.opensanctions.org/datasets/sanctions/>

#### Download Instructions

1.  Download the sanctions dataset (JSON format recommended).
2.  Download the files in the `data/raw/` folder as:
    -   dataname_raw.json
    -   dataname_raw.json
3.  The elaborated data will then be saved into `data/processed/`

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
analysis/
    cleaning/         # Data ingestion & preprocessing
    features/         # Feature engineering
    models/           # ML algorithms (implemented from scratch)
    orchestration/    # Coordinates data → features → model
    visuals/          # Visualization generation logic

app/
    routes/           # Flask route definitions
    templates/        # HTML templates (presentation layer)
    static/           # CSS and frontend assets

data/
    raw/              # Downloaded OpenSanctions dataset
    processed/        # Cleaned and transformed data

tests/                # Unit and integration tests
```

*For more information about the the layered system design please consult [our wiki](https://github.com/sbreganni/project-scrumit-sof.wiki.git)*

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

-   OpenSanctions for providing the dataset

------------------------------------------------------------------------

## The ScrumIt Team

<div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 20px; margin-top: 20px;">

  <div style="text-align: center;">
    <a href="https://github.com/adjicisse1">
      <img src="https://github.com/adjicisse1.png"
           style="width:80px; height:80px; border-radius:50%; object-fit:cover;" />
    </a>
    <br>
    <strong style="font-size: 0.9em;">Adji Bousso</strong>
  </div>

  <div style="text-align: center;">
    <a href="https://github.com/atulbharti1">
      <img src="https://github.com/atulbharti1.png"
           style="width:80px; height:80px; border-radius:50%; object-fit:cover;" />
    </a>
    <br>
    <strong style="font-size: 0.9em;">Atul Bharti</strong>
  </div>

  <div style="text-align: center;">
    <a href="https://github.com/ngpbruno">
      <img src="https://github.com/ngpbruno.png"
           style="width:80px; height:80px; border-radius:50%; object-fit:cover;" />
    </a>
    <br>
    <strong style="font-size: 0.9em;">Bruno Galvao</strong>
  </div>

  <div style="text-align: center;">
    <a href="https://github.com/sbreganni">
      <img src="https://github.com/sbreganni.png"
           style="width:80px; height:80px; border-radius:50%; object-fit:cover;" />
    </a>
    <br>
    <strong style="font-size: 0.9em;">Sofia Breganni</strong>
  </div>

  <div style="text-align: center;">
    <a href="https://github.com/ecassibry">
      <img src="https://github.com/ecassibry.png"
           style="width:80px; height:80px; border-radius:50%; object-fit:cover;" />
    </a>
    <br>
    <strong style="font-size: 0.9em;">Elizabeth Cassibry</strong>
  </div>

  <div style="text-align: center;">
    <a href="https://github.com/fenja-klockgether">
      <img src="https://github.com/fenja-klockgether.png"
           style="width:80px; height:80px; border-radius:50%; object-fit:cover;" />
    </a>
    <br>
    <strong style="font-size: 0.9em;">Fenja Klockgether</strong>
  </div>

  <div style="text-align: center;">
    <a href="https://github.com/Jishnu-Verma">
      <img src="https://github.com/Jishnu-Verma.png"
           style="width:80px; height:80px; border-radius:50%; object-fit:cover;" />
    </a>
    <br>
    <strong style="font-size: 0.9em;">Jishnu Verma</strong>
  </div>

</div>
