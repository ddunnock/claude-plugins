# Knowledge MCP: Vector Storage Options Analysis

## Cloudflare vs Qdrant for Your SE Knowledge Base

**Date**: January 15, 2026
**Use Case**: Semantic search over ~47MB of systems engineering reference documents (~4,000 chunks estimated)

---

## Executive Summary

| Option | Best For | Est. Monthly Cost | Complexity |
|--------|----------|-------------------|------------|
| **Cloudflare Vectorize** | Full Cloudflare stack, edge performance | $0-5/mo | Low |
| **Qdrant Cloud (Free)** | Quick start, 1GB free forever | $0 | Low |
| **Qdrant Cloud (Paid)** | Production scale, hybrid search | $10-50/mo | Low |
| **Qdrant on Cloudflare Workers** | Hybrid: CF edge + Qdrant backend | $5-20/mo | Medium |
| **Qdrant Self-Hosted (CF VPS)** | Full control, cost optimization | $5-10/mo | High |

**My Recommendation**: Start with **Qdrant Cloud Free Tier** for development, then either:
- Scale to **Qdrant Cloud Paid** for production simplicity, OR
- Use **Cloudflare Vectorize** if you want full CF stack integration

---

## Option 1: Cloudflare Vectorize (Native)

### Overview
[Cloudflare Vectorize](https://developers.cloudflare.com/vectorize/) is Cloudflare's native vector database, running at the edge across their global network.

### Pricing

| Tier | Queried Dimensions/mo | Stored Dimensions | Cost |
|------|----------------------|-------------------|------|
| **Free** | 30 million | 5 million | $0 |
| **Paid** | 50 million included | 10 million included | $5/mo base |
| **Overage** | $0.01/million | $0.05/100 million | Variable |

### Your Use Case Estimate
- **~4,000 chunks × 1,536 dimensions** = 6.1 million stored dimensions
- **~1,000 queries/month × 4,000 vectors** = 4 billion queried dimensions (worst case)

**Free Tier**: Would exceed stored limit (need paid)
**Paid Tier**: ~$0.50-2/month depending on query patterns

### Limits

| Limit | Free | Paid |
|-------|------|------|
| Indexes per account | 100 | 50,000 |
| Vectors per index | 5,000,000 | 5,000,000 |
| Max dimensions | 1,536 | 1,536 |
| Namespaces per index | 1,000 | 50,000 |
| Metadata per vector | 10 KB | 10 KB |

### Pros
- ✅ Native Cloudflare integration (Workers, R2, D1, KV)
- ✅ Edge deployment (low latency globally)
- ✅ No infrastructure management
- ✅ Pay-per-use pricing
- ✅ Workers AI integration for embeddings

### Cons
- ❌ **Max 1,536 dimensions** (can't use text-embedding-3-large's 3,072)
- ❌ No full-text/hybrid search
- ❌ Limited metadata indexing (10 indexes max)
- ❌ Newer product, less mature
- ❌ Vendor lock-in to Cloudflare ecosystem

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare Edge                           │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────┐  ┌───────────────┐  ┌─────────────────┐ │
│  │ Workers AI    │  │  Vectorize    │  │      R2         │ │
│  │ (embeddings)  │──│  (vectors)    │──│ (source docs)   │ │
│  └───────────────┘  └───────────────┘  └─────────────────┘ │
│         │                   │                               │
│         └─────────┬─────────┘                               │
│                   ▼                                         │
│         ┌─────────────────┐                                 │
│         │ Knowledge MCP   │                                 │
│         │ (Worker)        │                                 │
│         └─────────────────┘                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Option 2: Qdrant Cloud

### Overview
[Qdrant Cloud](https://qdrant.tech/cloud/) is the managed offering of the popular open-source vector database.

### Pricing

| Tier | Resources | Cost |
|------|-----------|------|
| **Free Forever** | 1 GB cluster | $0 |
| **Starter** | Pay-per-use | ~$0.014/hour |
| **Enterprise** | Custom | Contact sales |

### Your Use Case Estimate
- **~4,000 chunks × 1,536 dimensions × 4 bytes** = ~24 MB vectors
- **+ metadata** = ~50-100 MB total
- **Well within 1 GB free tier** ✅

### Pros
- ✅ **1 GB free forever** (no credit card)
- ✅ **Hybrid search** (dense + sparse vectors)
- ✅ **Full-text search** capability
- ✅ **Rich filtering** on metadata
- ✅ Mature, battle-tested product
- ✅ [Official MCP server](https://github.com/qdrant/mcp-server-qdrant) available
- ✅ Supports any embedding dimension
- ✅ AWS/GCP/Azure marketplace billing

### Cons
- ❌ Not edge-deployed (single region)
- ❌ Latency higher than CF edge (~50-200ms vs ~10-50ms)
- ❌ Separate service from your CF infrastructure

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Your Infrastructure                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────────┐        ┌───────────────────────────────┐ │
│  │ Knowledge MCP │        │        Qdrant Cloud           │ │
│  │ (local/CF)    │◀──────▶│  (managed, single region)     │ │
│  └───────────────┘  REST  │  - AWS/GCP/Azure              │ │
│         │                 │  - 1GB free tier              │ │
│         │                 └───────────────────────────────┘ │
│         ▼                                                    │
│  ┌───────────────┐                                          │
│  │ OpenAI API    │                                          │
│  │ (embeddings)  │                                          │
│  └───────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Option 3: Qdrant + Cloudflare Workers (Hybrid)

### Overview
Run your MCP server as a Cloudflare Worker that connects to Qdrant Cloud. This gives you edge compute with Qdrant's powerful features.

There's an [existing demo](https://github.com/elithrar/qdrant-workers-demo) showing this pattern.

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare Edge                           │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Knowledge MCP Worker                      │  │
│  │  - Receives query                                      │  │
│  │  - Calls OpenAI for embedding                          │  │
│  │  - Queries Qdrant Cloud                                │  │
│  │  - Returns results                                     │  │
│  └───────────────────────────────────────────────────────┘  │
│              │                          │                    │
└──────────────┼──────────────────────────┼────────────────────┘
               │                          │
               ▼                          ▼
       ┌───────────────┐         ┌───────────────┐
       │  OpenAI API   │         │ Qdrant Cloud  │
       │ (embeddings)  │         │   (vectors)   │
       └───────────────┘         └───────────────┘
```

### Pros
- ✅ Edge compute (CF Workers global)
- ✅ Qdrant's full feature set
- ✅ Best of both worlds
- ✅ Can use other CF services (R2, KV, D1)

### Cons
- ❌ Two external calls per query (OpenAI + Qdrant)
- ❌ More complex deployment
- ❌ Qdrant latency not at edge

### Cost Estimate
- **Workers Paid**: $5/month base
- **Qdrant Cloud Free**: $0
- **OpenAI**: ~$0.01-0.05/month for queries
- **Total**: ~$5/month

---

## Option 4: Self-Hosted Qdrant on Cloudflare

### Overview
Cloudflare doesn't offer persistent compute for databases, but you can:
1. Run Qdrant on a VPS (Hetzner, DigitalOcean, etc.)
2. Connect via Cloudflare Tunnel for security
3. Use CF Workers as the frontend

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare Edge                           │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Knowledge MCP Worker                      │  │
│  └───────────────────────────────────────────────────────┘  │
│              │                                               │
│              │ Cloudflare Tunnel                             │
└──────────────┼───────────────────────────────────────────────┘
               │
               ▼
       ┌───────────────────────────────────────┐
       │      VPS (Hetzner/DO/etc.)            │
       │  ┌─────────────────────────────────┐  │
       │  │    Qdrant (Docker)              │  │
       │  │    - Self-managed               │  │
       │  │    - Full control               │  │
       │  └─────────────────────────────────┘  │
       └───────────────────────────────────────┘
```

### Pros
- ✅ **70%+ cost savings** vs managed
- ✅ Full control over data
- ✅ No vendor lock-in
- ✅ Can run on cheap VPS ($5-10/mo)

### Cons
- ❌ You manage updates, backups, scaling
- ❌ Single point of failure (unless clustered)
- ❌ More DevOps work

### Cost Estimate
- **Hetzner VPS (CX22)**: €4.51/month (2 vCPU, 4GB RAM)
- **Workers Paid**: $5/month
- **Total**: ~$10/month

---

## Option 5: Cloudflare + Workers AI (Full CF Stack)

### Overview
Use Cloudflare's entire AI stack:
- **Workers AI**: Generate embeddings (no OpenAI needed!)
- **Vectorize**: Store vectors
- **R2**: Store source documents
- **D1**: Store metadata/chunks

### Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare Edge                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────────┐   │
│  │ Workers AI  │   │  Vectorize  │   │       R2        │   │
│  │ @cf/baai/   │──▶│  (vectors)  │   │  (source PDFs)  │   │
│  │ bge-base-en │   └──────┬──────┘   └─────────────────┘   │
│  └─────────────┘          │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                Knowledge MCP Worker                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                     D1 Database                      │   │
│  │           (chunk metadata, full text)                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Workers AI Embedding Models
| Model | Dimensions | Quality |
|-------|-----------|---------|
| `@cf/baai/bge-base-en-v1.5` | 768 | Good |
| `@cf/baai/bge-small-en-v1.5` | 384 | Fast |
| `@cf/baai/bge-large-en-v1.5` | 1024 | Best |

### Pros
- ✅ **No external API calls** (all on CF)
- ✅ Lowest latency possible
- ✅ Single billing (Cloudflare)
- ✅ Workers AI has free tier

### Cons
- ❌ Workers AI embeddings may be lower quality than OpenAI
- ❌ Vectorize 1,536 dimension limit
- ❌ No hybrid search
- ❌ Full vendor lock-in

### Cost Estimate (Workers Paid)
- **Workers AI**: ~$0.01/100K embeddings
- **Vectorize**: Included in $5 base (for your scale)
- **R2**: ~$0.015/GB stored
- **D1**: ~$0.001/million reads
- **Total**: ~$5-7/month

---

## Recommendation Matrix

### For Your Use Case (47MB SE docs, ~4K chunks)

| If You Want... | Choose | Why |
|----------------|--------|-----|
| **Simplest start** | Qdrant Cloud Free | 1GB free, no setup, official MCP |
| **Full Cloudflare stack** | Option 5 (CF + Workers AI) | Single vendor, edge everything |
| **Best search quality** | Qdrant Cloud + OpenAI | Hybrid search, best embeddings |
| **Lowest cost production** | Self-hosted Qdrant | ~$10/mo total |
| **Enterprise scale** | Qdrant Hybrid Cloud | Bring your own infra |

### My Recommendation

**Phase 1 (Now)**: Start with **Qdrant Cloud Free Tier**
- 1GB is plenty for your ~50-100MB knowledge base
- No credit card needed
- Use OpenAI embeddings for quality
- Can use existing [Qdrant MCP server](https://github.com/qdrant/mcp-server-qdrant) as reference

**Phase 2 (If scaling)**: Evaluate based on needs:
- High query volume → Cloudflare Vectorize (edge)
- Complex search needs → Qdrant Cloud Paid (hybrid search)
- Cost optimization → Self-hosted Qdrant

---

## Implementation Approach for Qdrant Cloud

### 1. Update `.env.example`

```bash
# Vector Store
VECTOR_STORE=qdrant

# Qdrant Cloud (Free Tier)
QDRANT_URL=https://your-cluster-id.us-east4-0.gcp.cloud.qdrant.io
QDRANT_API_KEY=your-api-key-here
QDRANT_COLLECTION=se_knowledge_base
```

### 2. Qdrant Store Implementation

```python
# src/knowledge_mcp/store/qdrant_store.py
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue
)

class QdrantStore:
    def __init__(self, config):
        self.client = QdrantClient(
            url=config.qdrant_url,
            api_key=config.qdrant_api_key,
        )
        self.collection = config.qdrant_collection
        self._ensure_collection(config.embedding_dimensions)

    def _ensure_collection(self, dimensions: int):
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection for c in collections):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(
                    size=dimensions,
                    distance=Distance.COSINE
                )
            )

    def add_chunks(self, chunks: list) -> int:
        points = [
            PointStruct(
                id=chunk.id,
                vector=chunk.embedding,
                payload={
                    "content": chunk.content,
                    "document_id": chunk.document_id,
                    "document_title": chunk.document_title,
                    "section_title": chunk.section_title,
                    "chunk_type": chunk.chunk_type,
                    "normative": chunk.normative,
                    "clause_number": chunk.clause_number,
                }
            )
            for chunk in chunks
        ]
        self.client.upsert(
            collection_name=self.collection,
            points=points
        )
        return len(points)

    def search(self, query_embedding, n_results=10, filter_dict=None):
        query_filter = None
        if filter_dict:
            conditions = [
                FieldCondition(key=k, match=MatchValue(value=v))
                for k, v in filter_dict.items()
            ]
            query_filter = Filter(must=conditions)

        results = self.client.search(
            collection_name=self.collection,
            query_vector=query_embedding,
            limit=n_results,
            query_filter=query_filter,
            with_payload=True
        )

        return [
            {
                "id": r.id,
                "content": r.payload.get("content", ""),
                "metadata": r.payload,
                "score": r.score
            }
            for r in results
        ]
```

---

## Sources

- [Cloudflare Vectorize Pricing](https://developers.cloudflare.com/vectorize/platform/pricing/)
- [Cloudflare Vectorize Limits](https://developers.cloudflare.com/vectorize/platform/limits/)
- [Qdrant Cloud Pricing](https://qdrant.tech/pricing/)
- [Qdrant MCP Server](https://github.com/qdrant/mcp-server-qdrant)
- [Qdrant + Cloudflare Workers Demo](https://github.com/elithrar/qdrant-workers-demo)
- [Qdrant Edge (Beta)](https://qdrant.tech/edge/)
- [Self-hosting Qdrant](https://sliplane.io/blog/self-hosting-qdrant-the-easy-way)
- [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/)
