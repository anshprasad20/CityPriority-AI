"""Stage 1 check: load the real dataset and print a validation + quality report."""
from core import config
from core.loader import load_data
from core.quality import run_quality_checks

d = load_data()
print(f"\n*** {config.DATA_LABEL} ***\n")
print(f"locations : {len(d.locations):>6,}")
print(f"incidents : {len(d.incidents):>6,}")
print(f"complaints: {len(d.complaints):>6,}")
print("\nValidation issues:", d.issues if d.issues else "none")
print("\nData-quality findings")
print("-" * 70)
for f in run_quality_checks(d):
    amt = f"{f.count:,}/{f.total:,} ({f.share:.1%})" if f.total > 1 else ("yes" if f.count else "no")
    print(f"[{f.level.upper():8}] {f.check}: {amt}")
    print(f"           {f.note}\n           Next: {f.next_step}")
