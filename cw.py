import argparse
import re
from collections import Counter

DICT = "/usr/share/dict/words"


def load_words() -> list[str]:
    """Load all alphabetic words from the system dictionary.

    Returns:
        list[str]: Lowercase words containing only alphabetic characters.
    """
    with open(DICT) as dict_file:
        return [word.strip().lower() for word in dict_file if word.strip().isalpha()]


def crossword_solver(pattern: str) -> list[str]:
    """Find dictionary words matching a pattern with wildcard characters.

    Each '?' or '*' in the pattern matches exactly one unknown letter.
    Known letters must match exactly.

    Args:
        pattern (str): A mix of letters and wildcard characters ('?' or '*'),
            e.g. '?u??t???' to find 8-letter words with 'u' second and 't' fifth.

    Returns:
        list[str]: Words from the dictionary that match the pattern.
    """
    regex = "^" + re.sub(r"[?*]", ".", pattern.lower()) + "$"
    return [word for word in load_words() if re.match(regex, word)]


def anagram(letters: str) -> list[str]:
    """Find dictionary words that are anagrams of the given letters.

    Spaces are ignored. The result contains only words that use every
    supplied letter exactly once.

    Args:
        letters (str): A collection of letters, optionally separated by spaces,
            e.g. 'uqsoteni' or 'u q s o t e n i'.

    Returns:
        list[str]: Words from the dictionary that are exact anagrams of the input.
    """
    letters = letters.replace(" ", "").lower()
    counts = Counter(letters)
    length = len(letters)
    return [word for word in load_words() if len(word) == length and Counter(word) == counts]


def main() -> None:
    """Parse arguments and run the selected crossword helper mode.

    With -a, treats the input as a set of letters and prints anagrams.
    With -s or no flag, treats the input as a pattern and prints matching words.
    Results are printed in alphabetical order, five words per line.
    """
    parser = argparse.ArgumentParser(description="Crossword helper")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", action="store_true", help="anagram mode")
    group.add_argument("-s", action="store_true", help="fill-blanks mode (default)")
    parser.add_argument(
        "-n", type=int, default=5, metavar="COLS", help="number of columns (default: 5)"
    )
    parser.add_argument("input", nargs="+")
    args = parser.parse_args()

    text = " ".join(args.input)

    if args.a:
        results = anagram(text)
    else:
        results = crossword_solver(text)

    words = sorted(results)
    col_width = max((len(word) for word in words), default=0) + 2
    for index, word in enumerate(words):
        end = "\n" if index % args.n == args.n - 1 or index == len(words) - 1 else ""
        print(word.ljust(col_width), end=end)


if __name__ == "__main__":
    main()
