"""AI data catalog indexer."""
from google.cloud import bigquery, datacatalog_v1
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from typing import Dict, List
import re, json

PII_PATTERNS = {
    "CPF": r"\d{3}\.\d{3}\.\d{3}-\d{2}",
    "CNPJ": r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}",
    "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "phone": r"\(\d{2}\)\s?\d{4,5}-\d{4}",
    "credit_card": r"\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",
}

class AIDataCatalog:
    def __init__(self, project_id: str):
        self.bq = bigquery.Client(project=project_id)
        self.llm = ChatVertexAI(model_name="gemini-1.5-flash-002")
        self.embedder = VertexAIEmbeddings(model_name="text-embedding-004")
        self.index = {}  # name -> embedding

    def describe_table(self, dataset: str, table: str) -> str:
        t = self.bq.get_table(f"{dataset}.{table}")
        schema_str = ", ".join([f"{f.name} ({f.field_type})" for f in t.schema])
        # Sample 5 rows
        try:
            sample = list(self.bq.query(f"SELECT * FROM {dataset}.{table} LIMIT 5").result())
            sample_str = str([dict(row) for row in sample])[:500]
        except: sample_str = "N/A"
        prompt = f"""Gere uma descricao clara e util em portugues para esta tabela do BigQuery:
Tabela: {dataset}.{table}
Colunas: {schema_str}
Dados exemplo: {sample_str}
Descreva: o que a tabela contem, para que serve, granularidade, atualizacoes.
Maximo 3 paragrafos."""
        return self.llm.invoke(prompt).content

    def detect_pii(self, sample_data: str) -> List[str]:
        found = []
        for pii_type, pattern in PII_PATTERNS.items():
            if re.search(pattern, sample_data): found.append(pii_type)
        return found

    def index_table(self, dataset: str, table: str):
        description = self.describe_table(dataset, table)
        embedding = self.embedder.embed_query(description)
        self.index[f"{dataset}.{table}"] = {"description": description, "embedding": embedding}
        return description

    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict]:
        import numpy as np
        q_emb = self.embedder.embed_query(query)
        scores = []
        for name, data in self.index.items():
            sim = np.dot(q_emb, data["embedding"]) / (np.linalg.norm(q_emb) * np.linalg.norm(data["embedding"]))
            scores.append({"table": name, "score": float(sim), "description": data["description"][:200]})
        return sorted(scores, key=lambda x: x["score"], reverse=True)[:top_k]
