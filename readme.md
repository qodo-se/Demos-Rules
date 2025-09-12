# Qodo SE :: Demos

Demos for Qodo SEs

## Agent Execution

### E2E & API Test Gen

```bash
qodo --agent-file=./Sri/agents-library/01_demo_e2e_tests.toml --yes --ci
```

### Report Generation

```bash
# Report generation on Qodo Gen VSCode extension repository
./Sri/agents-demo/qodo-gen-vscode-report.sh
```

### Compliance

```bash
# All
qodo --agent-file=./Sri/agents-library/01_demo_pr_compliance_toml --yes --ci

# GPDR
qodo --agent-file=./Sri/agents-library/01_demo_pr_compliance_gdpr.toml --yes --ci

# HIPAA
qodo --agent-file=./Sri/agents-library/01_demo_pr_compliance_hipaa.toml --yes --ci

# OWASP
qodo --agent-file=./Sri/agents-library/01_demo_pr_compliance_owasp.toml --yes --ci

# PCI-DSS
qodo --agent-file=./Sri/agents-library/01_demo_pr_compliance_pcidss.toml --yes --ci

# SOC2 Type 2
qodo --agent-file=./Sri/agents-library/01_demo_pr_compliance_soc2type2.toml --yes --ci
```

---

## On-prem

### Qodo Aware

```mermaid
flowchart TB
  %% External dependencies
  subgraph External
    GP[Git Providers<br/>GitHub / GitLab / Bitbucket DC]
    LLM[Model Gateway<br/> - gpt-5, claude-4.1-opius]
    MCPClients[Non-Qodo MCP Clients<br/> - optional]
    QMerge[Qodo Merge / Qodo Gen]
  end

  %% Data layer
  subgraph Data Layer
    PG[(PostgreSQL 17<br/>pgvector enabled<br/>TCP 5432)]
    subgraph PGDBs[PostgreSQL Databases]
      RAGDB[(rag-indexer DB)]
      METADB[(metadata DB)]
    end
    PG --- RAGDB
    PG --- METADB
  end

  %% Kubernetes namespace
  subgraph K8s[Your Kubernetes Cluster<br/>single namespace recommended]
    direction TB

    subgraph Secrets[Secrets & Config]
      QS[(qodo-aware-secrets Secret)]
      CM1[(ConfigMaps)]
    end

    MSvc[metadata-service<br/>NodePort 8000]
    IDX[rag-indexer<br/>NodePort 3000<br/>+ CronJob: reindex]
    CR[context-retriever<br/>NodePort 8001]
    CRMCP[context-retriever-mcp<br/>Ingress /mcp<br/>NodePort 8001<br/>optional]

    %% mounts
    QS --> MSvc
    QS --> IDX
    QS --> CR
    QS --> CRMCP
    CM1 --> CR
    CM1 --> CRMCP
  end

  %% Flows
  GP -- clone/list/repos --> IDX
  IDX -- embeddings + chunks --> RAGDB
  MSvc -- repo/org metadata --> METADB

  CR -- retrieve context --> RAGDB
  CR -- read metadata --> METADB
  CR -- context API (8001) --> QMerge

  CRMCP -- MCP server (/mcp) --> MCPClients

  %% Model dependency (outbound)
  CR -.-> LLM
  IDX -.-> LLM

  %% Admin ops
  Admin[Admin/Helm] -->|Install order:<br/>1 metadata-service<br/>2 rag-indexer<br/>3 context-retriever<br/>4 context-retriever-mcp| K8s
```

### Qodo Gen

```mermaid
flowchart TB
  %% Clients
  subgraph IDEs[Developer IDEs]
    VS[VS Code Extension]
    JB[JetBrains Plugin]
  end

  %% Platform
  subgraph Platform[Kubernetes or Embedded Cluster, Replicated]
    direction TB

    subgraph QGen[Qodo Gen Backend]
      API[Gen API / Services]
      Jobs[Helm Jobs:<br/>• db-migration - alembic<br/>• db-partition-create-init]
      Crons[CronJobs:<br/>• db-partition-create - daily 01:00<br/>• db-partition-delete - daily 01:00]
      Flags[Feature Flags via Secret/env:<br/>agentic_support<br/>lean_agent_enabled<br/>custom_mcp_enabled<br/>apply_flow_on<br/>test_flow_on<br/>langgraph_checkpointer=postgres]
    end

    Admin[Cluster Admin / Helm<br/>or Replicated Admin UI]
  end

  %% Data layer
  subgraph Data[Data Layer]
    PG[(PostgreSQL 17+<br/>agentic DB<br/>TCP 5432)]
  end

  %% Flows
  VS -->|chat, tasks, tool calls| API
  JB -->|chat, tasks, tool calls| API

  API -->|read/write| PG
  Jobs -->|migrations/partition init| PG
  Crons -->|daily maintenance| PG

  Admin -->|Helm upgrade/values<br/>OR Replicated config & license| Platform
  Flags --> API
```

### Qodo Merge

```mermaid
flowchart TB
  subgraph Dev[Development Workflow]
    PR[Pull Request Event]
    CommentCMD["/review, /describe" comment]
    MergeBot[Qodo Merge Bot - Git webhook]
  end

  subgraph K8s[Your Kubernetes Cluster]
    subgraph Agent[Qodo Merge Backend - pr_agent]
      Webhook[Webhook / PR listener]
      RequestHandler[Request processing & tool orchestration]
      LLMgateway[LLM Gateway - external]
      AwareSvc[Context Retrieval - optional, via Qodo Aware service]
      Analytics[Analytics sidecar or sink]
    end

    Ingress[Ingress / LoadBalancer]
    SecretStore[.secrets.toml secret or external secret backend]
    ConfigMap[ConfigMaps - env, feature flags]
  end

  subgraph GitProv[Git Provider]
    GitHub[GitHub or GitLab, Bitbucket]
  end

  PR -->|webhook event| MergeBot
  CommentCMD -.-> MergeBot

  MergeBot --> Webhook
  Webhook --> RequestHandler

  RequestHandler -->|context if RAG enabled| AwareSvc
  RequestHandler -->|prompt & instructions| LLMgateway
  RequestHandler -->|post back to PR| GitProv

  Agent --> Analytics

  Ingress --> MergeBot
  SecretStore --> Agent
  ConfigMap --> Agent

  Admin[Cluster Admin / Helm] -->|helm upgrade/install| Agent
```
