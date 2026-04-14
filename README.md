# Natural Language to CloudFormation Generator

> **Describe your AWS infrastructure in plain English, get a production-ready CloudFormation YAML in seconds.** Eliminates the hours teams spend writing verbose, error-prone CFN templates by delegating generation to an LLM with strict YAML validation and CFN intrinsic function support.

---

## The Problem This Solves

CloudFormation templates are notoriously verbose. A simple ECS Fargate service with ALB and auto-scaling requires 300+ lines of YAML with precise resource references. This tool reduces that to a one-liner.

```bash
# Before: 2 hours of CFN YAML wrangling
# After:
python main.py --scenarios ecs_fargate eks_cluster
```

---

## Supported Infrastructure Scenarios

| Scenario | AWS Services | Key Features |
|----------|-------------|-------------------------------------------|
| `ecs_fargate` | ECS, ALB, Auto Scaling | CloudWatch logging, IAM roles, target groups |
| `eks_cluster` | EKS, EC2, IAM | Managed node groups, OIDC provider, RBAC |
| `s3_static_site` | S3, CloudFront, ACM | HTTPS, OAI, cache policies, CORS |
| `rds_postgres` | RDS, Secrets Manager, VPC | Private subnet, encryption, automated backups |

---

## Architecture

```
Plain-English infrastructure request
        |
        v
  prompts.py  ──── System prompt + context-aware user message
        |
        v
  generator.py  ── LLM call (Ollama/GPT-4)
        |
        +── Validate: AWSTemplateFormatVersion + Resources keys present
        +── CloudFormationLoader: parses !Ref !Sub !GetAtt !Join !If !Select
        +── Loop detection + exponential backoff retry
        |
        v
  output_writer.py  ── Save CFN YAML to output/<scenario>/template.yaml
        |
        v
  output/<scenario>/template.yaml  (deploy-ready)
```

---

## What Makes This Production-Quality

| Feature | Implementation |
|---------|---------------|
| CFN intrinsic functions | Custom `CloudFormationLoader` handles `!Ref`, `!Sub`, `!GetAtt`, `!Join`, `!If`, `!Select`, `!Split`, `!Equals` |
| Template validation | Checks `AWSTemplateFormatVersion` + `Resources` keys before saving |
| Config management | `config.py` — all settings via env vars with typed defaults |
| Structured logging | Python `logging` — timestamp, level, module name |
| Retry logic | Exponential backoff (2^n seconds), max 3 retries |
| Loop detection | Deduplicates identical LLM outputs |
| CLI interface | `argparse` — `--scenarios`, `--output-json` |
| Error isolation | Per-scenario try/except, continues on individual failures |
| LLM-agnostic | Swap Ollama → GPT-4 or Claude via two env vars |

---

## Quick Start

### 1. Install Ollama + model
```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama run llama3.2
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate templates
```bash
# All scenarios
python main.py

# Specific scenarios
python main.py --scenarios ecs_fargate rds_postgres

# Export results to JSON
python main.py --output-json results.json
```

### 4. Optional env vars
```bash
export BASE_URL=http://localhost:11434/v1
export MODEL=llama3.2
export LOG_LEVEL=DEBUG
export OUTPUT_DIR=./generated-templates
```

---

## Project Structure

```
natural-language-to-cloudformation/
├── main.py             # CLI entry point — argparse, orchestration
├── generator.py        # LLM call, CFN YAML validation, retry + loop detection
├── prompts.py          # System prompt + context-aware user message builder
├── config.py           # Centralized config with env var overrides
├── mock_requests.py    # Simulated infrastructure requests per scenario
├── output_writer.py    # Save generated templates to output directory
└── requirements.txt    # openai, pyyaml
```

---

## Why This Matters (Resume Context)

This project demonstrates IaC automation with LLMs for a real DevOps pain point:
- **Domain-specific validation**: validates CFN-specific YAML structure (not just generic YAML) — the custom loader handles 8 CloudFormation intrinsic functions
- **Prompt engineering for IaC**: system prompt produces YAML with correct `!Ref`, `!Sub`, resource ARN chaining — not just syntactically valid YAML but semantically correct CFN
- **Production safety**: retry with backoff, loop detection, per-scenario error isolation — same patterns used in production ML pipelines
- **Real cloud knowledge**: generated templates use actual AWS resource types, IAM policies, VPC subnet references
- **LLM-agnostic design**: swap Ollama → OpenAI GPT-4 or Anthropic Claude via two env vars
