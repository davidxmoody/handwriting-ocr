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
%%capture cap --no-stderr
for tscript in tscripts:
    day = tscript.parent.name
    month = tscript.parent.parent.name
    year = tscript.parent.parent.parent.name

    date_str = f"{year}-{month}-{day}"

    if date_str < "2021-05-05":
        break

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
    for file in candidates:
        print(f"mv {tscript.relative_to(diary_dir)} {file.relative_to(diary_dir)}")

    print("\n\n\n")


# %%
with open("output.txt", "w") as f:
    f.write(cap.stdout)
