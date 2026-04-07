# OpenReview API Guide

## Authentication

Guest access works for most public venues. For private venues or higher rate limits:

```python
client = openreview.api.OpenReviewClient(
    baseurl="https://api2.openreview.net",
    username="your@email.com",
    password="your_password",
)
```

**Caution:** Use half-width `!` in passwords — full-width `！` (U+FF01) causes silent auth failure.

## Determining API Version

| Venue | Years | API | Base URL |
|-------|-------|-----|----------|
| ICLR | 2022-2023 | v1 | `api.openreview.net` |
| ICLR | 2024+ | v2 | `api2.openreview.net` |
| NeurIPS | 2021-2022 | v1 | `api.openreview.net` |
| NeurIPS | 2023+ | v2 | `api2.openreview.net` |
| ICML | 2023+ | v2 | `api2.openreview.net` |
| EMNLP | 2023+ | v2 | `api2.openreview.net` |
| ACL | 2024+ | v2 | `api2.openreview.net` |

**General rule:** If `openreview.api.OpenReviewClient` + `content.venueid` returns no results, try `openreview.Client` + `content.venue`.

## Querying Rejected Papers

### v2 Example (ICLR 2024)

```python
import openreview

client = openreview.api.OpenReviewClient(baseurl="https://api2.openreview.net")

# Get all rejected submissions
rejected = client.get_all_notes(
    content={"venueid": "ICLR.cc/2024/Conference/Rejected_Submission"},
)

for paper in rejected:
    title = paper.content["title"]["value"]
    abstract = paper.content.get("abstract", {}).get("value", "")
    keywords = paper.content.get("keywords", {}).get("value", [])
    authors = paper.content.get("authors", {}).get("value", [])
```

### v1 Example (ICLR 2023)

```python
client = openreview.Client(baseurl="https://api.openreview.net")

all_submissions = list(openreview.tools.iterget_notes(
    client,
    invitation="ICLR.cc/2023/Conference/-/Blind_Submission",
))

rejected = []
for paper in all_submissions:
    venue = paper.content.get("venue", "")
    if "Submitted to" in venue:  # Not accepted → rejected
        rejected.append(paper)
    
    title = paper.content.get("title", "")
    abstract = paper.content.get("abstract", "")
    keywords = paper.content.get("keywords", [])
```

## Fetching Reviews

### v2

```python
# Method 1: Direct query
reviews = client.get_all_notes(
    forum=paper.forum,
    signature="ICLR.cc/2024/Conference/Paper.*/Reviewer_.*",
)

# Method 2: Filter by invitation
all_replies = client.get_all_notes(forum=paper.forum)
reviews = [
    r for r in all_replies
    if any("Official_Review" in inv for inv in (r.invitations or []))
]

# Extract review fields (v2)
for review in reviews:
    rating = review.content.get("rating", {}).get("value", "")
    confidence = review.content.get("confidence", {}).get("value", "")
    soundness = review.content.get("soundness", {}).get("value", "")
    presentation = review.content.get("presentation", {}).get("value", "")
    contribution = review.content.get("contribution", {}).get("value", "")
    summary = review.content.get("summary", {}).get("value", "")
    strengths = review.content.get("strengths", {}).get("value", "")
    weaknesses = review.content.get("weaknesses", {}).get("value", "")
```

### v1

```python
replies = client.get_notes(forum=paper.forum)
reviews = [
    r for r in replies
    if r.invitation and "Official_Review" in r.invitation
]

# Extract review fields (v1) — direct string access
for review in reviews:
    rating = review.content.get("rating", "")
    confidence = review.content.get("confidence", "")
    # soundness/presentation/contribution may not exist in v1
```

**Key Bug to Avoid:** v2 reviews use `invitations` (plural, list), not `invitation` (singular, string). Checking `review.invitation` on a v2 note returns an empty string. Always check `review.invitations`.

## Venue ID Patterns

### Constructing Venue IDs

Pattern: `{ORG}.cc/{YEAR}/{TYPE}/{STATUS}`

```python
def build_venue_id(venue, year, status="Rejected_Submission"):
    """Build OpenReview v2 venue ID."""
    org_map = {
        "ICLR": "ICLR.cc",
        "NeurIPS": "NeurIPS.cc",
        "ICML": "ICML.cc",
        "EMNLP": "EMNLP.cc",
        "ACL": "aclweb.org/ACL",
    }
    org = org_map.get(venue, f"{venue}.cc")
    return f"{org}/{year}/Conference/{status}"
```

### Known Status Strings

| Status | Meaning |
|--------|---------|
| (none) | Accepted (camera-ready) |
| `Rejected_Submission` | Rejected after review |
| `Withdrawn_Submission` | Withdrawn by authors |
| `Desk_Rejected_Submission` | Desk rejected (no review) |

## Error Handling

```python
import time

def safe_api_call(fn, *args, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return fn(*args, **kwargs)
        except openreview.OpenReviewException as e:
            if "429" in str(e) or "TooMany" in str(e):
                wait = 60 * (attempt + 1)
                time.sleep(wait)
            elif "404" in str(e):
                return None  # Paper/review not found
            else:
                raise
    return None
```

## Extending to New Venues

To add a new venue:

1. Find the venue's OpenReview group: browse `https://openreview.net/group?id=VENUE.cc/YEAR/Conference`
2. Check which API version: try v2 first, fall back to v1
3. Determine the venue ID for rejected papers (check the venueid on a known rejected paper)
4. Add to your topic config and run collection
