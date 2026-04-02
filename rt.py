#!/usr/bin/env python3
import re
import sys
from pathlib import Path

PATTERN = re.compile(r"rt_[A-Za-z0-9._-]+")
DEFAULT_OUTPUT_FILE = "output.txt"


def extract_rts(text: str) -> list[str]:
    # Extract every rt_* token from the given text.
    return PATTERN.findall(text)


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
