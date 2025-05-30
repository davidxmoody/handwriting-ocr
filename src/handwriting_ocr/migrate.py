from os.path import expandvars
from pathlib import Path
import re


# %%
diary_dir = Path(expandvars("$DIARY_DIR"))


# %%
tscripts = sorted(
    diary_dir.glob("transcripts/*/*/*/transcript-*.md"),
    reverse=True,
)


# %%
def migrate(source: Path, dest: Path):
    if dest.exists():
        raise Exception("Destination already exists")

    dest.parent.mkdir(parents=True, exist_ok=True)
    source.rename(dest)

    try:
        source.parent.rmdir()
        source.parent.parent.rmdir()
        source.parent.parent.parent.rmdir()
    except OSError:
        pass

    scanned_meta_dir = Path(str(source.parent).replace("transcripts", "scanned-meta"))

    for sm in scanned_meta_dir.glob("scanned-*.*.json"):
        sm.unlink()

    try:
        scanned_meta_dir.rmdir()
        scanned_meta_dir.parent.rmdir()
        scanned_meta_dir.parent.parent.rmdir()
    except OSError:
        pass

    scanned_dir = Path(str(source.parent).replace("transcripts", "scanned"))

    old_scanned_dir = Path(str(scanned_dir).replace("scanned/", "old-scanned/"))
    old_scanned_dir.parent.mkdir(parents=True, exist_ok=True)
    scanned_dir.rename(old_scanned_dir)

    try:
        scanned_dir.parent.rmdir()
        scanned_dir.parent.parent.rmdir()
    except OSError:
        pass


# %%
for tscript in tscripts:
    day = tscript.parent.name
    month = tscript.parent.parent.name
    year = tscript.parent.parent.parent.name

    date_str = f"{year}-{month}-{day}"

    print(f"{date_str}   -----------------------------------------------")

    existing_entries = list(
        diary_dir.glob(f"entries/{year}/{month}/{day}/diary-*-*.md")
    )
    if existing_entries:
        print("Existing entries:")
        for entry in existing_entries:
            print(entry.relative_to(diary_dir))
        print("\n")
    else:
        print("No existing entries\n")

    choice = input("Enter time (HH-MM format or leave blank for 00-00): ")
    if choice == "":
        choice = "00-00"

    if re.match(r"^\d{2}-\d{2}$", choice):
        migrate(tscript, diary_dir / f"entries/{year}/{month}/{day}/diary-{choice}.md")
    else:
        raise Exception("Invalid match")

    print("\n\n")
