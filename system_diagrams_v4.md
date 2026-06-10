# ConstructAI Construction Plan Cost & Material Estimation — System Diagrams

This document contains the system architecture diagrams for the ConstructAI platform, including the Context Diagram (DFD Level 0), Data Flow Diagram (DFD Level 1), Use Case Diagram, Entity Relationship Diagram (ERD), and Pipeline Flowchart. All diagrams are designed to adhere strictly to formal modeling rules.

---

## 1. DATA FLOW DIAGRAMS (DFD)

### DFD Rules Applied:
* **No External Entity to Data Store**: External entities (e.g., Quantity Surveyor, Admin) must never write directly to or read directly from data stores. All interactions are routed through a Process.
* **No External Entity to External Entity**: External entities do not directly communicate with each other inside the system boundary.
* **No Data Store to Data Store**: Data stores cannot exchange data directly; they must interact through processes.
* **Balanced Inputs/Outputs**: Every process must have at least one input and one output (no "black holes" or "miracles").
* **Naming Conventions**: Processes are labeled with action verbs; external entities and data stores are labeled with nouns.

---

### A. Level 0 DFD (Context Diagram)

The Context Diagram establishes the scope of the system, showing the main system boundary, the external entities that interact with it, and the high-level inputs and outputs.

```mermaid
flowchart TD
    %% External Entities
    QS((👤 Quantity Surveyor))
    ADMIN((🛡️ Admin))

    %% System Process
    P0["Process 0\n🏗️ ConstructAI Construction Plan Cost\n& Material Estimation System"]

    %% Data Flows
    QS -->|"Construction Plan PDF/Image\n+ Scaling Factor"| P0
    QS -->|"Manual Wall Dimensions\n& Overrides"| P0
    P0 -->|"BOQ Reports (Excel/PDF)\n+ Project Narrative Summary"| QS
    P0 -->|"Confidence Alert\n& Human Intervention Request"| QS

    ADMIN -->|"Updated Material/Labor\nRates & Regional Pricing"| P0
    P0 -->|"System Activity Log\n& Usage Reports"| ADMIN
```

---

### B. Level 1 DFD (Decomposed System Processes)

The Level 1 DFD decomposes the system into detailed functional processes, identifying the data stores and internal data routes.

```mermaid
flowchart TD
    %% ─── External Entities ───
    QS((👤 Quantity Surveyor))
    ADMIN((🛡️ Admin))

    %% ─── Processes ───
    P1["Process 1\n📤 Upload & Project\nCreation"]
    P2["Process 2\n🔍 OCR & Image\nProcessing"]
    P3["Process 3\n🧠 Semantic Wall\nInterpretation"]
    P4["Process 4\n📐 Hybrid Data\nFusion"]
    P5["Process 5\n🧱 Cost & Material\nEstimation"]
    P6["Process 6\n✅ Validation & Readiness\nAssessment"]
    P7["Process 7\n📄 Narrative &\nExport Generation"]
    P8["Process 8\n⚙️ Pricing & System\nAdministration"]

    %% ─── Data Stores ───
    DS1[(D1\nUploads\nDirectory)]
    DS2[(D2\nOCR Text\nCache)]
    DS3[(D3\nPostgreSQL\nDatabase)]
    DS4[(D4\nGenerated\nExports)]

    %% ─── Data Flows ───
    
    %% QS Interactions
    QS -->|"Plan File + Scale"| P1
    QS -->|"Manual Wall Overrides"| P4
    P7 -->|"BOQ Excel, PDF,\n& Narrative Report"| QS

    %% Admin Interactions
    ADMIN -->|"Pricing updates"| P8
    P8 -->|"Usage & Audit Reports"| ADMIN

    %% Process 1
    P1 -->|"Save plan file"| DS1
    P1 -->|"Project ID, scale\n& upload notification"| P2

    %% Process 2
    DS1 -->|"Read file for OCR\n& image analysis"| P2
    P2 -->|"Save raw text"| DS2
    P2 -->|"Raw text, labels\n& wall geometries"| P3

    %% Process 3
    DS2 -->|"Retrieve cached text"| P3
    P3 -->|"Structured wall list\n& dimensions"| P4

    %% Process 4
    P4 -->|"Fused wall dimensions\n(manual overrides prioritized)"| P5

    %% Process 5
    DS3 -->|"Fetch material unit rates"| P5
    P5 -->|"Save project, wall,\n& estimation records"| DS3
    P5 -->|"Physical quantities\n& calculated costs"| P6

    %% Process 6
    P6 -->|"Calculated readiness score\n& warnings list"| P7

    %% Process 7
    P7 -->|"Save generated Excel,\nPDF, & narrative reports"| DS4

    %% Process 8
    P8 -->|"Insert/Update pricing rates"| DS3
    DS3 -->|"Read usage logs\n& activity database"| P8
```

---

## 2. USE CASE DIAGRAM

The Use Case Diagram describes the system functionality from the perspective of the primary actors (Quantity Surveyor and Administrator), defining actions executed within the system boundary.

```mermaid
flowchart LR
    %% Actors
    subgraph Actors
        QS["👤 Quantity Surveyor\n(User)"]
        ADMIN["🛡️ System Admin"]
    end

    %% System Boundary
    subgraph System ["System: ConstructAI Construction Estimation Engine"]
        direction TB
        
        %% Use Cases for QS
        UC1(["Upload Plan File\n(PDF / Image)"])
        UC2(["Configure Scale\n& Measurements"])
        UC3(["View Visual AI\nWall Detection"])
        UC4(["Input Manual Wall\nOverrides"])
        UC5(["Execute Cost & Material\nEstimation"])
        UC6(["Review Readiness\n& Confidence Report"])
        UC7(["Export BOQ Reports\n(Excel / PDF)"])
        
        %% Use Cases for Admin
        UC8(["Update Material &\nLabor Pricing Rates"])
        UC9(["Audit System Usage\n& Project Logs"])
    end

    %% Associations
    QS --> UC1
    QS --> UC2
    QS --> UC3
    QS --> UC4
    QS --> UC5
    QS --> UC6
    QS --> UC7

    ADMIN --> UC8
    ADMIN --> UC9
```

---

## 3. ENTITY RELATIONSHIP DIAGRAM (ERD)

This ERD represents the relational database schema implemented in the PostgreSQL database. It identifies fields, keys, data types, and cardinality constraints.

```mermaid
erDiagram
    User ||--o{ Project : "creates"
    User ||--o{ PasswordResetToken : "requests"
    Project ||--o{ Wall : "contains"
    Project ||--o{ Estimation : "has"
    Project ||--o{ BuildingSummaryRecord : "summarizes"
    Estimation ||--o{ EstimationPhase : "broken_into"

    User {
        int id PK
        string email UK
        string hashed_password
        string name
        boolean is_google_user
        datetime created_at
    }

    PasswordResetToken {
        int id PK
        string email FK
        string token UK
        datetime expires_at
        boolean used
    }

    Project {
        int id PK
        int user_id FK "nullable"
        string filename
        string scale
        datetime created_at
    }

    Wall {
        int id PK
        int project_id FK
        string wall_id
        float length_m
        float height_m
        float thickness_mm
        float openings_area_m2
        string wall_type
        float classification_confidence
        string reasoning
    }

    Estimation {
        int id PK
        int project_id FK
        int total_bricks
        float total_mortar_volume
        float total_cost
        float grand_total
        string boq_excel_path
        string boq_pdf_path
        datetime created_at
    }

    EstimationPhase {
        int id PK
        int estimation_id FK
        string phase_name
        float cost
        datetime created_at
    }

    BuildingSummaryRecord {
        int id PK
        int project_id FK
        int rooms
        int bedrooms
        int bathrooms
        int kitchens
        int walls
        int doors
        int windows
        int columns
        int beams
        int stairs
        float confidence
        datetime created_at
    }
```

---

## 4. PIPELINE EXECUTION FLOWCHART

### Flowchart Rules Applied:
* **Terminal Symbols**: Oval/Capsule shapes (`([Start / End])`) denote execution entry/exit boundaries.
* **Process Steps**: Rectangles (`["Process Name"]`) represent computational or system operations.
* **Decision Nodes**: Diamonds (`{"Condition?"}`) represent branching tests with explicit label routes.
* **Input / Output Nodes**: Parallelograms (`[/Data I/O/]`) represent data ingestion and file delivery points.

```mermaid
flowchart TD

    START([START\nUser runs estimation pipeline]) --> A1{File & scale\nprovided?}
    
    A1 -- No --> A_ERR([Error: Missing inputs])
    A1 -- Yes --> B1[/Upload Plan PDF/Image\nPOST /upload/plan/]
    
    B1 --> B2{File Format\nSupported?}
    B2 -- No --> B_ERR([Error: Unsupported file format])
    B2 -- Yes --> C1["Create Project Record in DB\n(projects table)"]
    
    C1 --> D1{Is file a PDF?}
    D1 -- Yes --> D_A["Convert PDF to Images\n(pdf2image library)"] --> D2{Success?}
    D1 -- No --> D_B["Use image directly"] --> E1["Preprocess Image\n(Binarize & Deskew)"]
    
    D2 -- No --> D_ERR([Pipeline Failed])
    D2 -- Yes --> E1
    
    E1 --> E2["Run OCR on Image\n(pytesseract)"]
    E2 --> E3["Clean OCR Text & Extract\nLabels / Dimensions"]
    E3 --> E4[/Save raw OCR text\noutputs/ocr_text/cache/]
    
    E4 --> F1["Classify Drawing Type\n(Floor Plan / Section / Elevation)"]
    F1 --> F2{Suitable for\nwall extraction?}
    F2 -- No --> F_WARN["Add Low Suitability Warning"] --> G1["Extract Semantics & Wall IDs\n(ai_interpreter.py)"]
    F2 -- Yes --> G1
    
    G1 --> G2["Detect Geometric Wall Lines\n(OpenCV)"]
    G2 --> G3["Detect Openings\n(Doors & Windows)"]
    G3 --> G4["Normalize Wall Thickness"]
    G4 --> G5["Classify Masonry Type\n(Brick / Block)"]
    
    G5 --> H1{Any walls\ndetected?}
    H1 -- No --> H_WARN["Set intervention_needed = True\nFlag missing data alert"] --> I1["Evaluate Pipeline path\n(confidence_service)"]
    H1 -- Yes --> I1
    
    I1 --> I2{OCR Confidence\nScore?}
    I2 -- "< 0.3" --> I_FAIL([Pipeline Blocked:\nManual Entry Required])
    I2 -- "0.3 - 0.7" --> I_SEMI["Path: SEMI-AUTO\nPre-fill UI, flag review"] --> J1["Calculate physical wall volume\n(area & height calculations)"]
    I2 -- "> 0.7" --> I_AUTO["Path: FULL-AUTO\nProceed automatically"] --> J1
    
    J1 --> K1{Manual Overrides\nprovided by user?}
    K1 -- Yes --> K_A["Fuse AI & Manual Data\n(Manual overrides take priority)"] --> L1["Calculate Material Volume\n(Bricks & Mortar components)"]
    K1 -- No --> K_B["Use AI-extracted wall data"] --> L1
    
    L1 --> M1["Compute costs utilizing\nmaterial rate database"]
    M1 --> N1[/Write results to DB\nestimations & walls tables/]
    
    N1 --> N2{Save\nSuccessful?}
    N2 -- No --> N_WARN["Log Database Warning"] --> O1["Assess overall project readiness\n(readiness_service)"]
    N2 -- Yes --> O1
    
    O1 --> O2{Readiness\nScore Status?}
    O2 -- "LOW" --> O_LO["Flag for strict human review\nintervention_needed = True"] --> P1["Execute pipeline failure analysis\n(classify pipeline errors)"]
    O2 -- "MEDIUM" --> O_ME["Mark ready with warnings\nallow override"] --> P1
    O2 -- "HIGH" --> O_HI["Mark project as ready"] --> P1
    
    P1 --> Q1["Log engineering assumptions\n& defaults utilized"]
    Q1 --> R1["Generate Narrative report\n(engineer summary)"]
    
    R1 --> R2[/Export BOQ to Excel\n(openpyxl)/]
    R2 --> R3[/Export BOQ to PDF\n(reportlab)/]
    
    R3 --> S1["Link evidence attribution\n(data source mapping)"]
    S1 --> T1["Generate pipeline trace audit trail"]
    
    T1 --> V1[/Assemble final JSON response\nDeliver success payload/]
    V1 --> END([END: Render estimation to client])
