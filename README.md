# Crossword Tools

Command line tools for solving cryptic crosswords:

- **Crossword solver**: given a pattern of known letters and wildcards, find matching words
- **Anagram finder**: given a set of letters, find all exact anagrams

Words are sourced from `/usr/share/dict/words`.

## Usage

```
cw [-s] [-n COLS] <pattern>   # fill-blanks mode (default)
cw -a [-n COLS] <letters>     # anagram mode
```

Results are printed in columns (default: 5). Use `-n` to change the number of columns:

```bash
cw -n 3 '?u??t???'   # 3 columns
cw -n 1 -a uqsoteni  # one word per line
```

### Fill-blanks mode (`-s` or no flag)

Supply a pattern where known letters are given literally and each unknown position is marked with `?` or `*`. Results are printed alphabetically.

```bash
cw '?u??t???'       # finds "question", "duration", etc.
cw -s 'c?t'         # finds "cat", "cut", "cot", etc.
```

### Anagram mode (`-a`)

Supply a collection of letters (spaces are ignored). Prints every dictionary word that uses all of those letters exactly once.

```bash
cw -a uqsoteni      # finds "question"
cw -a 'e l a s t'   # finds "least", "slate", "stale", etc.
```

## Installation

### Prerequisites

- Python 3.12

### Development setup


### Installing the `cw` command

Run the provided install script to create a `cw` command in `~/.local/bin`:

```bash
bash install.sh
```

The script will:
- Locate the project venv's Python (falling back to system `python3`)
- Check that `~/.local/bin` exists, offering to create it if not
- Warn if `~/.local/bin` is not on your `PATH`
- Prompt before overwriting any existing `cw` command

If `~/.local/bin` is not yet on your `PATH`, add this to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## License

MIT
