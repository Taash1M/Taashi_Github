
# Azure Module: Real-Time Dynamic Inventory Mesh

## 1. Executive Summary & Problem Statement
**The Challenge:** Inventory data is often "eventually consistent," leading to overselling.
**The Solution:** A Data Mesh node on Azure Databricks.

## 2. Medallion Architecture Implementation
* **Bronze:** Ingest raw inventory change logs.
* **Silver:** Deduplicate events (handling retries) and optimize storage (Z-Ordering).
* **Gold:** Aggregate changes to produce a real-time "Stock on Hand" snapshot for the website.

### Azure Architecture: Real-Time Inventory Mesh

### Azure Architecture: Real-Time Inventory Mesh

### System Context Diagram: Platform Modernization Blueprint

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'fontFamily': 'arial', 'fontSize': '14px'}}}%%
graph TD
    %% Definitions & Styling
    classDef enterprise fill:#E1D5E7,stroke:#9673A6,stroke-width:2px,color:#000,stroke-dasharray: 5 5;
    classDef system fill:#DAE8FC,stroke:#6C8EBF,stroke-width:2px,color:#000;
    classDef external fill:#FFF2CC,stroke:#D6B656,stroke-width:2px,color:#000;
    classDef person fill:#FFE6CC,stroke:#D79B00,stroke-width:2px,color:#000;

    subgraph Enterprise_Scope ["The Enterprise"]
        direction TB
        Analysts("Person: Data Analysts & Execs"):::person
        
        subgraph Platform_Boundary ["Modern Data Platform"]
            ThePlatform("System: Platform Modernization Blueprint"):::system
        end

        BiTools("System Ext: BI & Dashboards"):::external
        MLModels("System Ext: ML Recommendations"):::external
    end

    %% External Systems outside the Enterprise Boundary
    AdPlatforms("System Ext: Ad Platforms<br/>Meta/TikTok"):::external
    Ecomm("System Ext: E-commerce<br/>Shopify"):::external
    Mobile("System Ext: Mobile Apps & IoT"):::external

    %% Relationships
    AdPlatforms -->|"Streams Ad Signals"| ThePlatform
    Ecomm -->|"Sends Orders"| ThePlatform
    Mobile -->|"Emits Events"| ThePlatform

    ThePlatform -->|"Gold Data"| BiTools
    ThePlatform -->|"Feature Store"| MLModels
    
    BiTools -->|"Delivers Insights"| Analysts

    %% Apply Styles
    class Enterprise_Scope enterprise
```
Section 2
### Azure Architecture: Real-Time Inventory Mesh

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'fontFamily': 'arial', 'fontSize': '14px'}}}%%
graph TD
    %% Definitions & Styling
    classDef storage fill:#DAE8FC,stroke:#6C8EBF,stroke-width:2px,color:#000;
    classDef compute fill:#FFF2CC,stroke:#D6B656,stroke-width:2px,color:#000;
    classDef governance fill:#F8CECC,stroke:#B85450,stroke-width:2px,color:#000;
    classDef source fill:#E1D5E7,stroke:#9673A6,stroke-width:2px,color:#000;

    subgraph Sources ["Data Sources - Edge Locations"]
        POS["POS Systems<br/>Tokyo/NY/London"]:::source
        Warehouse["Warehouse IoT<br/>Scanners"]:::source
    end

    subgraph Ingestion ["Streaming Ingestion"]
        EventHubs["Azure Event Hubs<br/>Real-time Buffer"]:::compute
    end

    subgraph Processing ["Azure Databricks - Delta Engine"]
        SparkJob["Spark Structured Streaming<br/>(Medallion Logic)"]:::compute
    end

    subgraph Governance ["Governance & Lineage"]
        Unity["Unity Catalog<br/>ACLs & Lineage"]:::governance
    end

    subgraph Lakehouse ["ADLS Gen2 - Delta Lake"]
        Bronze[("Bronze Layer<br/>Raw Ingest")]:::storage
        Silver[("Silver Layer<br/>Deduped & Z-Ordered")]:::storage
        Gold[("Gold Layer<br/>Stock Snapshots")]:::storage
    end

    subgraph Serving ["Consumption Layer"]
        Synapse["Azure Synapse<br/>Serverless SQL"]:::compute
        PowerBI["Power BI<br/>Inventory Dashboards"]:::compute
    end

    %% Data Flow
    POS -->|"Stream Events"| EventHubs
    Warehouse -->|"Stream Scans"| EventHubs
    EventHubs -->|"Autoloader"| SparkJob

    %% Medallion Flow inside Databricks
    SparkJob --"1. Append Raw"--> Bronze
    Bronze --"2. Read Stream"--> SparkJob
    SparkJob --"3. Merge (Upsert)"--> Silver
    Silver --"4. Aggregation"--> SparkJob
    SparkJob --"5. Write State"--> Gold

    %% Governance Connections
    Bronze -.->|"Register"| Unity
    Silver -.->|"Register"| Unity
    Gold -.->|"Register"| Unity

    %% Serving
    Gold -->|"Query State"| Synapse
    Synapse -->|"Visuals"| PowerBI
    Unity -.->|"Policy Check"| SparkJob

    linkStyle 2,3,4,5,6,7 stroke:#007ACC,stroke-width:2px,fill:none;
```
## 3. How to Run
1.  `cd azure_implementation`
2.  `python databricks_delta_job.py`
