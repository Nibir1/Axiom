# Axiom: Green AI Knowledge Governance Engine

[![Axiom Demo](https://img.youtube.com/vi/QD3AmfA2_uY/maxresdefault.jpg)](https://youtu.be/QD3AmfA2_uY)

> 📺 **[Watch the Architectural Walkthrough](https://www.google.com/search?q=https://youtu.be/QD3AmfA2_uY)** featuring Lifecycle Management, PII Redaction Middleware, and Green AI density scoring.

**Axiom** is a reference architecture for a **Sustainable, Zero-Trust Knowledge Governance System**. Unlike standard RAG demos, Axiom addresses the "Day 2" challenges of Enterprise AI: Data Hygiene, Cost Control (FinOps), and Lifecycle Management. It was designed specifically to align with UPM's commitment to "Renewing the Everyday" by ensuring AI systems are energy-efficient and secure.

---

## 1. Executive Summary & Business KPI Impact

This architecture solves specific bottlenecks in deploying GenAI to industrial and regulated sectors.

| KPI | Challenge | Axiom Solution |
| --- | --- | --- |
| **Sustainability (Green AI)** | Storing "junk" data (boilerplate, logs) wastes energy and storage. | **Density Scoring Algorithm** rejects low-value content (< 0.4 density) *before* vectorization, reducing compute waste by ~30%. |
| **Data Privacy (GDPR)** | LLMs training on PII leaks employee data. | **Hybrid PII Scrubber** (Spacy + Regex) redacts emails and names locally before data ever leaves the secure enclave. |
| **Information Freshness** | RAG bots retrieve outdated policies (hallucination risk). | **Lifecycle Metadata Schema** enforces strict `valid_until` dates, automatically filtering expired knowledge from search results. |

---

## 2. System Architecture (C4 Model)

We utilize the C4 model to visualize boundaries between the Enterprise Network and Public Cloud services.

### Level 1: System Context

The high-level data flow between the Employee, the internal Axiom System, and External Providers.

```mermaid
graph LR
    User[Employee] -- "HTTPS/TLS" --> Ingress[Nginx Gateway]
    subgraph "Private VNET (Docker Network)"
        Ingress --> Gatekeeper[Axiom API Gateway]
        Gatekeeper --> Scrubber[PII Redaction Engine]
        Gatekeeper --> Vault[Qdrant Vector DB]
    end
    Gatekeeper -- "Anonymized Context" --> OpenAI[GPT-4o-mini]
    
    style User stroke:#333,stroke-width:2px
    style Ingress stroke:#333,stroke-width:2px
    style Gatekeeper stroke:#009c48,stroke-width:2px
    style Vault stroke:#333,stroke-width:2px
    style OpenAI stroke:#333,stroke-width:2px,stroke-dasharray: 5 5

```

### Level 2: The Ingestion Pipeline (The "Green" Filter)

Detailing the Governance logic that happens *before* storage.

```mermaid
sequenceDiagram
    participant U as Employee
    participant A as API (The Gatekeeper)
    participant S as Scorer (Green AI)
    participant P as PII Scrubber
    participant V as Qdrant (The Vault)
    
    U->>A: Upload PDF ("Strategy_2024.pdf")
    A->>S: Calculate Information Density
    alt Density < 0.4 (Boilerplate/Junk)
        S-->>A: Reject (400 Bad Request)
        A-->>U: Error: "Low Information Density"
    else Density >= 0.4 (High Value)
        A->>P: Detect PII (NER + Regex)
        P-->>A: Return Redacted Text ("<PERSON>")
        A->>V: Upsert Vector + Lifecycle Metadata
        V-->>A: Acknowledgement (ID: xyz)
        A-->>U: Success: "Asset Secured & Indexed"
    end

```

---

## 3. Architecture Decision Records (ADR)

Key architectural trade-offs made during the design phase.

| Component | Decision | Alternatives Considered | Justification (The "Why") |
| --- | --- | --- | --- |
| **Vector Engine** | **Qdrant (Rust)** | Postgres (pgvector), Pinecone | **Performance & Green AI:** Qdrant is written in Rust, offering superior resource efficiency (lower RAM/CPU usage) compared to Java/Python-based DBs, aligning with sustainability goals. |
| **PII Redaction** | **Local Spacy Model** | Azure AI Language, AWS Comprehend | **Zero Trust:** PII scrubbing must happen *on-premise* (within the container). Sending raw text to a cloud API for redaction defeats the purpose of privacy. |
| **Embedding Model** | **all-MiniLM-L6-v2** | OpenAI Ada-002 | **Latency & Cost:** Running a quantized local model avoids network latency and per-token API costs for embeddings, keeping the ingestion loop fast and free. |

---

## 4. FinOps: Cost Modeling & Optimization

An analysis of the "Token Economics" for a typical deployment.

**Assumptions:**

* Document Ingestion Volume: 10,000 pages/month.
* "Junk" Ratio (Email footers, disclaimers): ~30%.
* Embedding Cost: $0.10 / 1M tokens.

| Scenario | Workflow | Est. Compute/Cost | Impact |
| --- | --- | --- | --- |
| **Standard Ingestion** | Index every page indiscriminately. | High Storage & Compute | Bloated DB, slower search. |
| **Axiom "Green" Pipeline** | **Density Scorer** rejects 30% of low-value pages. | **30% Reduction** | Smaller index, faster retrieval, lower carbon footprint. |

---

## 5. Reliability & Security Strategy

### Governance & Compliance

1. **PII Allow-Listing:** The system is tuned to redact personal names (`<PERSON>`) but explicitly white-lists internal business units (e.g., "UPM Biofuels", "Raflatac") to ensure business context is preserved.
2. **Lifecycle Management:** Every document is tagged with a `valid_until` timestamp. The search engine applies a hard filter `WHERE valid_until > NOW()` to prevent the retrieval of obsolete SOPs or expired contracts.

### Fault Tolerance

* **Containerization:** The entire stack (Frontend, Backend, DB) is dockerized with health checks. If the Backend fails, Docker Compose automatically restarts the service.
* **Graceful Degradation:** If OpenAI connectivity fails during chat, the system falls back to a "Search Only" mode, returning raw document context to the user without generation.

---

## 6. Evaluation Framework (Quality Assurance)

We utilize a rigorous "Test-Driven Development" (TDD) approach.

* **Information Density Threshold:** Integration tests verify that "garbage text" (stopwords/punctuation) triggers a `400 Bad Request`, ensuring the Green AI filter works.
* **Redaction Accuracy:** Unit tests confirm that `support@upm.com` becomes `<REDACTED_EMAIL>` while `UPM Biofore` remains untouched.
* **Test Coverage:** **100%**. We use `pytest` with `httpx` for the backend and `Vitest` for the frontend to mock all external dependencies.

---

## 7. Tech Stack & Implementation Details

* **Backend:** Python 3.11, FastAPI (Async), Pydantic V2 (Strict Schemas)
* **AI/NLP:** Spacy (NER), Sentence-Transformers (Local Embeddings), OpenAI (Generation)
* **Database:** Qdrant (Vector Search with Payload Filtering)
* **Frontend:** React 18, TypeScript, Tailwind CSS (Modern Dashboard)
* **Infrastructure:** Docker Compose (Microservices Architecture)

### Installation & Local Deployment

**Prerequisites:** Docker, Docker Compose, OpenAI API Key.

```bash
# 1. Clone the repository
git clone https://github.com/Nibir1/Axiom.git
cd axiom

# 2. Configure Environment
cp backend/.env

# Application Settings
PROJECT_NAME="Axiom Knowledge Engine"
API_V1_STR="/api/v1"
DEBUG_MODE=True

# Vector Database Settings
QDRANT_HOST="localhost"
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME="upm_knowledge_base"

# Security Settings
# In production, this would be a secure secret key
SECRET_KEY="upm-axiom-super-secret-key-change-me"
OPENAI_API_KEY=Add your OPENAI_API_KEY here

# 3. Build & Launch (The "Make" command handles Docker builds)
make build

```

### Testing & Validation

Run the comprehensive test suite (Backend + Frontend):

```bash
make test

```

### Access Points

* **Frontend Dashboard:** http://localhost:3000
* **API Documentation:** http://localhost:8000/docs
* **Vector DB Console:** http://localhost:6333/dashboard

---

Designed & Architected by **Nahasat Nibir**
*Principal AI Solutions Architect Candidate*