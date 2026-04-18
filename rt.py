#!/usr/bin/env python3
import re
import string
import sys
from collections import Counter
from pathlib import Path

RT_START_PATTERN = re.compile(r"rt_")
# Any punctuation run with length >= 3 is treated as a potential field separator.
SEPARATOR_RUN_PATTERN = re.compile(r"[^A-Za-z0-9\s]{3,}")
RT_ALLOWED_CHARS = set(string.ascii_letters + string.digits + "._-")
DEFAULT_OUTPUT_FILE = "output.txt"


def detect_repeated_separators(line: str) -> set[str]:
    # Detect the actual separator format used on this line instead of hardcoding
    # specific strings like `----` or `___`.
    counts = Counter(match.group(0) for match in SEPARATOR_RUN_PATTERN.finditer(line))
    return {separator for separator, count in counts.items() if count >= 2}


def normalize_repeated_separators(line: str) -> str:
    # Normalize the repeated separator formats that this line actually uses.
    normalized_line = line
    for separator in sorted(detect_repeated_separators(line), key=len, reverse=True):
        normalized_line = normalized_line.replace(separator, " ")
    return normalized_line


def extract_rts_from_line(line: str) -> list[str]:
    normalized_line = normalize_repeated_separators(line)
    separator_runs = {
        match.start(): match.group(0)
        for match in SEPARATOR_RUN_PATTERN.finditer(normalized_line)
    }
    results = []

    for match in RT_START_PATTERN.finditer(normalized_line):
        start = match.start()
        end = start

        while end < len(normalized_line):
            separator = separator_runs.get(end)
            if separator and end > start:
                # Even if a long separator only appears once on the line, it is
                # still very likely to be a field boundary rather than rt data.
                break

            if normalized_line[end] in RT_ALLOWED_CHARS:
                end += 1
                continue
            break

        token = normalized_line[start:end]
        if token != "rt_":
            results.append(token)

    return results


def extract_rts(text: str) -> list[str]:
    # Extract rt tokens line by line so per-line separator formats can be
    # detected dynamically.
    results = []
    for line in text.splitlines():
        results.extend(extract_rts_from_line(line))
    return results


def iter_input_files(input_path: Path, output_path: Path) -> list[Path]:
    output_resolved = output_path.resolve(strict=False)

    if input_path.is_file():
        return [input_path]

    if input_path.is_dir():
        files = []
        for file_path in sorted(path for path in input_path.rglob("*") if path.is_file()):
            if file_path.resolve(strict=False) != output_resolved:
                files.append(file_path)
        return files

    raise FileNotFoundError(f"Input path does not exist: {input_path}")


def resolve_output_path() -> Path:
    # If the caller does not provide an output path, write to output.txt
    # in the current working directory.
    if len(sys.argv) == 3:
        return Path(sys.argv[2])
    return Path(DEFAULT_OUTPUT_FILE)


def main():
    if len(sys.argv) not in (2, 3):
        script_name = Path(sys.argv[0]).name
        print(f"Usage: python3 {script_name} <input_file_or_dir> [output_file]")
        print(f"Example: python3 {script_name} data")
        print(f"Example: python3 {script_name} data {DEFAULT_OUTPUT_FILE}")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = resolve_output_path()

    try:
        input_files = iter_input_files(input_path, output_path)
    except FileNotFoundError as exc:
        print(exc)
        sys.exit(1)

    results = []
    for file_path in input_files:
        # Read file contents tolerantly so mixed encodings do not stop the batch.
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        results.extend(extract_rts(text))

    output_path.write_text("\n".join(results), encoding="utf-8")

    if input_path.is_dir():
        print(f"Extracted {len(results)} rt values from {len(input_files)} files to {output_path}")
    else:
        print(f"Extracted {len(results)} rt values to {output_path}")


if __name__ == "__main__":
    main()
