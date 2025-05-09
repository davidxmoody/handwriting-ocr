from os.path import expandvars
from pathlib import Path
from symspellpy import SymSpell
import importlib.resources


# %%
spell = SymSpell(max_dictionary_edit_distance=2)
dictionary_path = (
    importlib.resources.files("symspellpy") / "frequency_dictionary_en_82_765.txt"
)
spell.load_dictionary(str(dictionary_path), term_index=0, count_index=1)
# print(spell.lookup_compound("ths is a smple txt", max_edit_distance=2)[0].term)


# %%
diary_dir = Path(expandvars("$DIARY_DIR"))
pattern = "transcripts/[0-9][0-9][0-9][0-9]/[0-9][0-9]/[0-9][0-9]/transcript-*.md"
tscripts = sorted(diary_dir.glob(pattern), reverse=True)


# %%
text = ""
for tscript in tscripts:
    text = tscript.read_text()
    break


# %%
def fix(line: str):
    return spell.lookup_compound(
        line,
        max_edit_distance=2,
        transfer_casing=True,
        ignore_non_words=True,
        ignore_term_with_digits=True,
    )[0].term


for line in text.splitlines():
    print(f"{line:>80} {fix(line):>80}")
