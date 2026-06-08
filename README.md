# 📚 AI-Powered Data Catalog

[![Datasets](https://img.shields.io/badge/Datasets%20Cataloged-42K-blue)](.) [![Auto-described](https://img.shields.io/badge/AI%20Descriptions-94%25%20auto-green)](.) [![Search](https://img.shields.io/badge/Semantic%20Search-< 1s-orange)](.)

> **AI data catalog** that automatically discovers, describes and connects 42K datasets. LLM generates human-readable descriptions, semantic search finds data in natural language and PII scanner prevents data breaches.

## ✨ Auto-Cataloging Pipeline
```
BigQuery/GCS/Postgres scan → Schema extraction → Sample data (100 rows)
→ LLM description generation → PII detection → Business term matching
→ Lineage detection → Quality score → Published in catalog
```

## 🔍 Search Examples
- "customer revenue data with CPF" → finds 3 relevant tables
- "sales by region last quarter" → suggests BigQuery views
- "ML training data for churn model" → links to feature store
