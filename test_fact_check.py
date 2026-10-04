import sys
import json

# Ensure UTF-8 output on Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from ai_engine.services.fact_check_service import verify_note_accuracy

test_sample = """
Photosynthesis is an essential biological process.
In plant cells, photosynthesis occurs directly inside the mitochondria where chlorophyll absorbs sunlight.
The Earth revolves around the Sun once every 365.25 days.
"""

print("\n==========================================")
print("TESTING AI NOTE FACT-CHECKING SERVICE")
print("==========================================")
print("Note Content:")
print(test_sample.strip())
print("------------------------------------------")

result = verify_note_accuracy(test_sample, "Cell Biology Notes")

print("\n--- AI Assessment Result ---")
print(json.dumps(result, indent=2, ensure_ascii=False))

discrepancies = result.get("discrepancies", [])
if discrepancies:
    print(f"\n✅ SUCCESS: Detected {len(discrepancies)} discrepancy/discrepancies as expected:")
    for i, issue in enumerate(discrepancies, start=1):
        print(f"  [{i}] ⚠️ {issue.get('prompt_message')}")
        print(f"      Claim in note: \"{issue.get('claim_text')}\"")
        print(f"      Why to review: {issue.get('reason')}")
        print(f"      Factual Truth: {issue.get('suggestion')}\n")
else:
    print("\nNote assessed as accurate without issues.")
