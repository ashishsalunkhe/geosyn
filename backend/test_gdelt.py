from app.ingestion.gdelt_gkg_provider import GDELTGKGProvider

p = GDELTGKGProvider()
print("Testing fetch_raw_docs...")
docs = p.fetch_raw_docs(query="Red Sea Conflict", limit=5)
print(f"Found {len(docs)} docs")
if docs:
    print("Sample doc date:", docs[0].get("seendate"))
    print("Sample doc source:", docs[0].get("source"))
