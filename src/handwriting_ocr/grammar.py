from pathlib import Path
import language_tool_python
import re
from os.path import expandvars


# %%
def remove_code_blocks_and_inline(text: str) -> str:
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"`[^`]+`", "", text)
    return text


def check_grammar_in_file(
    file_path: Path, tool: language_tool_python.LanguageTool, allowed_words: set[str]
):
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
    except Exception as e:
        print(f"Failed to read {file_path}: {e}")
        return

    for i, line in enumerate(lines, 1):
        cleaned_line = remove_code_blocks_and_inline(line)
        matches = tool.check(cleaned_line)
        for match in matches:
            # Skip if all suggested replacements are in allowed words
            if all(word in allowed_words for word in match.replacements):
                continue

            # Skip if the error itself is about an allowed word
            if (
                match.context[match.offset : match.offset + match.errorLength]
                in allowed_words
            ):
                continue

            print(f"{file_path}:{i}")
            print(f"  Issue: {match.message}")
            print(f"  Suggestion: {match.replacements}")
            print(f"  Context: {match.context}")
            print()


def load_custom_words(spellfile_path: Path) -> set[str]:
    try:
        return set(
            word.strip()
            for word in spellfile_path.read_text(encoding="utf-8").splitlines()
            if word.strip() and not word.startswith("#")
        )
    except Exception as e:
        print(f"Failed to load spellfile '{spellfile_path}': {e}")
        return set()


# %%
tool = language_tool_python.LanguageTool("en-GB")
paths = list(Path(expandvars("$DIARY_DIR")).glob("entries/2025/06/*/diary-*.md"))
allowed_words = load_custom_words(Path(expandvars("$VIM_SPELLFILE")))


# %%
for path in paths:
    check_grammar_in_file(path, tool, allowed_words)
