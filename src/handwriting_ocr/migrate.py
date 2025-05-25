import pandas as pd
from os.path import expandvars
from pathlib import Path


# %%
diary_dir = Path(expandvars("$DIARY_DIR"))


# %%
events = pd.read_table(expandvars("$DIARY_DIR/data/atracker.tsv"))
events = events.loc[events.category == "journal"]
events["start"] = pd.to_datetime(events.start, utc=True).dt.tz_convert("Europe/London")
events = events.set_index("start")


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

    print("\nATracker events:\n")
    day_events = events.loc[date_str:date_str]
    candidates = []
    for event in day_events.reset_index().itertuples():
        file = (
            diary_dir
            / f"entries/{year}/{month}/{day}/diary-{event.start.hour:02d}-{event.start.minute:02d}.md"
        )
        if not file.exists():
            candidates.append(file)
        print(
            event.start,
            event.duration,
            file.relative_to(diary_dir),
            ("Exists" if file.exists() else ""),
        )

    print("\nExisting entries:\n")
    for entry in diary_dir.glob(f"entries/{year}/{month}/{day}/diary-*-*.md"):
        print(entry.relative_to(diary_dir))
    print()

    print("\nCandidate moves:\n")
    for i, file in enumerate(candidates):
        print(
            f"({i + 1}) {tscript.relative_to(diary_dir)} -> {file.relative_to(diary_dir)}"
        )

    print("\n\n")

    choice = input("Choose an option: ")
    if choice.isdigit():
        index = int(choice) - 1
        if not (0 <= index < len(candidates)):
            raise Exception("Invalid choice")
        migrate(tscript, candidates[index])

    print("\n\n\n")
