# Paper Collection Sources

## Source 1: OpenAlex (Primary for Accepted Papers)

**API:** `https://api.openalex.org/works`

**Why OpenAlex:**
- Free, no API key required (polite pool with email in User-Agent gets higher rate limits)
- Broadest coverage of CS venues
- Returns structured metadata including citation counts

**Query Strategy:**
```python
import requests

params = {
    "search": "your topic keywords",
    "filter": "publication_year:2022-2026,type:article",
    "sort": "cited_by_count:desc",
    "per_page": 50,
    "page": 1,
}
headers = {"User-Agent": "mailto:your@email.com"}
r = requests.get("https://api.openalex.org/works", params=params, headers=headers)
```

**Rate Limiting:** 10 req/s (polite pool), 100K req/day

**Venue Filtering Caveat:** OpenAlex venue names are fragmented (e.g., "Neural Information Processing Systems" vs "NeurIPS"). Best to search broadly and post-filter by keyword matching.

## Source 2: Semantic Scholar (Fallback)

**API:** `https://api.semanticscholar.org/graph/v1/paper/search`

**Usage:**
```python
params = {
    "query": "topic keywords",
    "year": "2022-2026",
    "fields": "title,abstract,authors,venue,year,citationCount,externalIds",
    "limit": 100,
    "offset": 0,
}
r = requests.get(
    "https://api.semanticscholar.org/graph/v1/paper/search",
    params=params,
)
```

**Rate Limiting:** 100 req/5min without API key, 1 req/s with key

**Best For:** Papers with DOIs, clean venue metadata

## Source 3: OpenReview (Rejected Papers + Accepted with Reviews)

**API:** `openreview-py` Python package

### v2 API (ICLR 2024+, NeurIPS 2023+)

```python
import openreview

client = openreview.api.OpenReviewClient(
    baseurl="https://api2.openreview.net"
)

# Rejected papers
papers = client.get_all_notes(
    content={"venueid": "ICLR.cc/2024/Conference/Rejected_Submission"},
    details="replies",
)

# Reviews for a paper
reviews = client.get_all_notes(
    forum=paper.forum,
    signature="ICLR.cc/2024/Conference/Paper.*/Reviewer_.*",
)
```

**Venue ID patterns (v2):**
| Venue | Accepted | Rejected |
|-------|----------|----------|
| ICLR 2024 | `ICLR.cc/2024/Conference` | `ICLR.cc/2024/Conference/Rejected_Submission` |
| NeurIPS 2024 | `NeurIPS.cc/2024/Conference` | `NeurIPS.cc/2024/Conference/Rejected_Submission` |
| NeurIPS 2023 | `NeurIPS.cc/2023/Conference` | `NeurIPS.cc/2023/Conference/Rejected_Submission` |

### v1 API (ICLR 2022-2023)

```python
client = openreview.Client(baseurl="https://api.openreview.net")

papers = list(openreview.tools.iterget_notes(
    client,
    invitation="ICLR.cc/2023/Conference/-/Blind_Submission",
    details="replies",
))
# Filter by content.venue == "Submitted to ICLR 2023" (rejected)
rejected = [p for p in papers if "Submitted to" in p.content.get("venue", "")]
```

**Critical v1/v2 Differences:**
| Aspect | v1 | v2 |
|--------|----|----|
| Client | `openreview.Client` | `openreview.api.OpenReviewClient` |
| Base URL | `api.openreview.net` | `api2.openreview.net` |
| Content access | `note.content["title"]` | `note.content["title"]["value"]` |
| Review detection | `note.invitation` contains `"Official_Review"` | `note.invitations` list contains `"Official_Review"` |
| Venue filter | `content.venue` string | `content.venueid` string |
| PDF download | `client.get_pdf(forum)` → bytes | Same |

### PDF Download Strategy

```python
import signal, fitz  # PyMuPDF

def download_pdf(client, forum_id, timeout=90):
    """Download and extract text from OpenReview PDF."""
    signal.alarm(timeout)
    try:
        pdf_bytes = client.get_pdf(forum_id)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
            if len(text) > 60000:
                break
        return text[:60000]
    except Exception:
        return None
    finally:
        signal.alarm(0)
```

### Rate Limiting Best Practices

- Sleep 0.5-2s between requests
- On HTTP 429: wait 60s and retry (max 3 retries)
- Checkpoint saves every 10 papers
- Use `--workers 4` for parallel PDF downloads (not metadata)

## Deduplication

Papers from multiple sources are deduped by normalized title matching:

```python
def normalize(title):
    return re.sub(r"[^a-z0-9]", "", title.lower())
```

Papers with matching `paper_id` or identical normalized titles are merged (prefer the source with more metadata).
