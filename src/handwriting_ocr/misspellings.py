from os.path import expandvars
from pathlib import Path
from collections import Counter
from spellchecker import SpellChecker
import re
import sys

diary_dir = Path(expandvars("$DIARY_DIR"))


def get_markdown_files():
    return list(diary_dir.glob("transcripts/*/*/*/transcript-*.md"))


def extract_words(text: str):
    return re.findall(r"\b[a-zA-Z']+\b", text)


def count_words_in_files(files):
    word_counter = Counter()
    for file in files:
        try:
            text = file.read_text(encoding="utf-8")
            words = extract_words(text)
            word_counter.update(word for word in words)
        except Exception as e:
            print(f"Failed to read {file}: {e}", file=sys.stderr)
    return word_counter


def find_misspellings(word_counter, spellchecker):
    misspelled = {}
    for word, count in word_counter.items():
        if not spellchecker.known([word]):
            misspelled[word] = count
    return sorted(misspelled.items(), key=lambda x: x[1], reverse=True)


def main():
    files = get_markdown_files()
    print(f"Found {len(files)} markdown files.")

    word_counts = count_words_in_files(files)

    spell = SpellChecker()
    misspelled_words = find_misspellings(word_counts, spell)

    print("\nMisspelled Words by Frequency:")
    for word, freq in misspelled_words:
        print(f"{word}: {freq}")


if __name__ == "__main__":
    main()
