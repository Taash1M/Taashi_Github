
# GCP Module: Serverless Streaming User Analytics

## 1. Executive Summary & Problem Statement
**The Challenge:** Mobile connectivity issues cause "Late Data," breaking traditional session metrics.
**The Solution:** Google Cloud Dataflow with Watermark handling.

## 2. Medallion Architecture Implementation
* **Bronze:** Raw JSON strings from Pub/Sub.
* **Silver:** Parsed objects with "Event Time" assigned (handling the 'late arrival' problem).
* **Gold:** Dynamic Session Windows that re-sequence the disordered events into accurate user journeys.

### GCP Architecture: Serverless Streaming Analytics

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'fontFamily': 'arial', 'fontSize': '14px'}}}%%
graph TD
    %% Definitions & Styling
    classDef storage fill:#DAE8FC,stroke:#6C8EBF,stroke-width:2px,color:#000;
    classDef compute fill:#FFF2CC,stroke:#D6B656,stroke-width:2px,color:#000;
    classDef governance fill:#F8CECC,stroke:#B85450,stroke-width:2px,color:#000;
    classDef source fill:#E1D5E7,stroke:#9673A6,stroke-width:2px,color:#000;

    subgraph Sources ["Data Sources - Mobile & Web"]
        MobileApp["Mobile App Events<br/>(High Latency/Disordered)"]:::source
        WebClick["Web Clickstream<br/>(Real-time)"]:::source
    end

    subgraph Ingestion ["Serverless Ingestion"]
        PubSub["Cloud Pub/Sub<br/>Topic: user-events"]:::compute
    end

    subgraph Processing ["Stream Processing (Apache Beam)"]
        Dataflow["Cloud Dataflow<br/>(Session Window Logic)"]:::compute
    end

    subgraph Governance ["Governance & Observability"]
        Catalog["Data Catalog<br/>Tagging & Lineage"]:::governance
        CloudMon["Cloud Operations<br/>(Monitoring/Alerting)"]:::governance
    end

    subgraph Warehouse ["BigQuery - Medallion Layers"]
        Bronze[("BQ Bronze<br/>Raw JSON Ingest")]:::storage
        Silver[("BQ Silver<br/>Parsed & Watermarked")]:::storage
        Gold[("BQ Gold<br/>Sessionized Aggregates")]:::storage
    end

    subgraph Serving ["Consumption Layer"]
        Looker["Looker<br/>User Journey Dashboards"]:::compute
        AIPlatform["Vertex AI<br/>Recommendation Engine"]:::compute
    end

    %% Data Flow
    MobileApp -->|"Publish (Async)"| PubSub
    WebClick -->|"Publish"| PubSub
    PubSub -->|"Read Unbounded"| Dataflow

    %% Medallion Flow inside Dataflow
    Dataflow --"1. Write Raw"--> Bronze
    Dataflow --"2. Assign Watermarks"--> Silver
    Dataflow --"3. Session Aggregation"--> Gold

    %% Governance & Monitoring
    Dataflow -.->|"Log Lag/Errors"| CloudMon
    Bronze -.->|"Register Schema"| Catalog
    Gold -.->|"Register Schema"| Catalog

    %% Serving
    Gold -->|"SQL Analysis"| Looker
    Gold -->|"Feature Lookup"| AIPlatform

    linkStyle 2,3,4,5 stroke:#007ACC,stroke-width:2px,fill:none;
```


## 3. How to Run
1.  `cd gcp_implementation`
2.  `python dataflow_pipeline.py`
