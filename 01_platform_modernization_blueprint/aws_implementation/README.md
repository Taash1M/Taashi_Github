
# AWS Module: Global Omni-Channel Attribution Lakehouse

## 1. Executive Summary & Problem Statement
**The Challenge:** Marketing data is "messy" and high-velocity, while financial data is strict and transactional. Bridging this gap to calculate Real-Time ROAS (Return on Ad Spend) is difficult.
**The Solution:** A Serverless Attribution Lakehouse using AWS Glue.

## 2. Medallion Architecture Implementation
* **Bronze:** Raw ingestion of Ad Impressions and Orders from S3.
* **Silver:** Type enforcement (Timestamps) and Data Quality checks (Null SKU removal).
* **Gold:** Stateful temporal join to link specific Ad Impressions to Orders, aggregated by Campaign ID.

### System Context Diagram: Platform Modernization Blueprint

```mermaid
%%{init: {'theme': 'neutral', 'themeVariables': { 'fontFamily': 'arial', 'fontSize': '14px'}}}%%
graph TD
    %% Definitions & Styling
    classDef enterprise fill:#E1D5E7,stroke:#9673A6,stroke-width:2px,color:#000,stroke-dasharray: 5 5;
    classDef system fill:#DAE8FC,stroke:#6C8EBF,stroke-width:2px,color:#000;
    classDef external fill:#FFF2CC,stroke:#D6B656,stroke-width:2px,color:#000;
    classDef person fill:#FFE6CC,stroke:#D79B00,stroke-width:2px,color:#000;

    subgraph Enterprise_Scope [The Enterprise]
        direction TB
        Analysts(Person: Data Analysts & Execs):::person
        
        subgraph Platform_Boundary [Modern Data Platform]
            ThePlatform(System: Platform Modernization Blueprint):::system
        end

        BiTools(System Ext: BI & Dashboards):::external
        MLModels(System Ext: ML Recommendations):::external
    end

    %% External Systems outside the Enterprise Boundary
    AdPlatforms(System Ext: Ad Platforms<br/>Meta/TikTok):::external
    Ecomm(System Ext: E-commerce<br/>Shopify):::external
    Mobile(System Ext: Mobile Apps & IoT):::external

    %% Relationships
    AdPlatforms -->|Streams Ad Signals| ThePlatform
    Ecomm -->|Sends Orders| ThePlatform
    Mobile -->|Emits Events| ThePlatform

    ThePlatform -->|Gold Data| BiTools
    ThePlatform -->|Feature Store| MLModels
    
    BiTools -->|Delivers Insights| Analysts

    %% Apply Styles
    class Enterprise_Scope enterprise
```
## 3. How to Run
1.  `cd aws_implementation`
2.  `python glue_etl_job.py`
