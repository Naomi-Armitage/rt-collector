# rt-collector

A small Python utility for extracting `rt_*` tokens from a single file or every file in a directory.

## Features

- Extracts all `rt_*` values from text content
- Supports a single input file or a whole directory
- Recursively scans files under a directory
- Writes to `output.txt` by default when no output path is provided

## Usage

```bash
python3 rt.py <input_file_or_dir> [output_file]
```

Examples:

```bash
python3 rt.py data
python3 rt.py data result.txt
python3 rt.py input.txt output.txt
```

## License

MIT
