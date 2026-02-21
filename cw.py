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
        seen: set[str] = set()
        words: list[str] = []
        for word in dict_file:
            word = word.strip().lower()
            if word.isalpha() and word not in seen:
                seen.add(word)
                words.append(word)
        return words


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


def _backtrack(
    slot_idx: int,
    remaining: Counter,
    chosen: list[str],
    min_idx: int,
    sorted_lengths: list[int],
    words_by_length: dict[int, list[tuple[Counter, str]]],
    results: list[tuple[str, ...]],
) -> None:
    if slot_idx == len(sorted_lengths):
        results.append(tuple(chosen))
        return

    length = sorted_lengths[slot_idx]
    next_same_length = slot_idx + 1 < len(sorted_lengths) and sorted_lengths[slot_idx + 1] == length

    for idx in range(min_idx, len(words_by_length[length])):
        candidate_counter, candidate = words_by_length[length][idx]
        if candidate_counter <= remaining:
            chosen.append(candidate)
            _backtrack(
                slot_idx + 1,
                remaining - candidate_counter,
                chosen,
                idx + 1 if next_same_length else 0,
                sorted_lengths,
                words_by_length,
                results,
            )
            chosen.pop()


def multianagram(letters: str, lengths: list[int]) -> list[tuple[str, ...]]:
    """Find all combinations of dictionary words that together anagram the given letters.

    Each result is a tuple containing one word per entry in `lengths`, where the
    word at position i has exactly `lengths[i]` characters. Taken together, the
    words in each tuple use every supplied letter exactly once.

    Algorithm:
        Pre-filtering: Before backtracking starts, every word in the dictionary is
        tested against two cheap conditions: its length must appear in `lengths`, and
        its per-letter counts must all be within the original letter pool (Counter
        subset test). This eliminates the vast majority of dictionary entries upfront,
        keeping the candidate lists small.

        Sorting for deduplication: `lengths` is sorted so that equal values are
        adjacent. When two or more consecutive slots share the same required length,
        later slots are only allowed to choose from words at a higher list index than
        the word chosen by the earlier slot. This enforces an implicit ordering that
        guarantees each unordered combination appears exactly once — ("cat", "dog")
        and ("dog", "cat") are not both emitted.

        Backtracking with Counter arithmetic: the algorithm fills one slot per
        recursive call. It subtracts the chosen word's Counter from the remaining
        letter pool before recursing, and restores it on backtrack. Counter's `<=`
        operator (subset check) and `-` operator both run in O(alphabet size),
        so candidate testing and pool updates are cheap regardless of word length.
        Any branch where no word of the required length fits the remaining pool is
        pruned immediately without generating further candidates.

    Args:
        letters (str): The full set of letters to use, optionally space-separated.
        lengths (list[int]): Word lengths to partition the letters into. Must sum to
            the number of non-space letters. e.g. [3, 5] finds all pairs of a
            3-letter and a 5-letter word that together use every letter exactly once.

    Returns:
        list[tuple[str, ...]]: Each tuple contains one word per entry in `lengths`
            (ordered by ascending length) that together anagram the input letters.

    Raises:
        ValueError: If ``sum(lengths)`` does not equal the number of letters.
    """
    letters = letters.replace(" ", "").lower()
    total = sum(lengths)
    if total != len(letters):
        raise ValueError(
            f"Lengths {lengths} sum to {total}, but {len(letters)} letters were given."
        )

    pool = Counter(letters)
    needed_lengths = set(lengths)
    sorted_lengths = sorted(lengths)

    # Pre-filter: only keep words of a needed length whose letters all fit in the pool.
    words_by_length: dict[int, list[tuple[Counter, str]]] = {
        length: [] for length in needed_lengths
    }
    for word in load_words():
        if len(word) in needed_lengths:
            word_counter = Counter(word)
            if word_counter <= pool:
                words_by_length[len(word)].append((word_counter, word))

    results: list[tuple[str, ...]] = []
    _backtrack(0, pool, [], 0, sorted_lengths, words_by_length, results)
    return results


def main() -> None:
    """Parse arguments and run the selected crossword helper mode.

    With -a, treats the input as a set of letters and prints anagrams.
    With -m LENGTHS, treats the input as letters and finds multi-word anagrams.
    With -s or no flag, treats the input as a pattern and prints matching words.
    Single-word results are printed in alphabetical order in multiple columns.
    Multi-word results are printed one combination per line.
    """
    parser = argparse.ArgumentParser(description="Crossword helper")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-a", action="store_true", help="anagram mode")
    group.add_argument("-s", action="store_true", help="fill-blanks mode (default)")
    group.add_argument(
        "-m",
        metavar="LENGTHS",
        help="multi-anagram mode: comma-separated word lengths, e.g. -m 3,5",
    )
    parser.add_argument(
        "-n", type=int, default=5, metavar="COLS", help="number of columns (default: 5)"
    )
    parser.add_argument("input", nargs="+")
    args = parser.parse_args()

    text = " ".join(args.input)

    if args.m:
        lengths = [int(x) for x in args.m.split(",")]
        for combo in sorted(multianagram(text, lengths)):
            print(" ".join(combo))
    else:
        results = anagram(text) if args.a else crossword_solver(text)
        words = sorted(results)
        col_width = max((len(word) for word in words), default=0) + 2
        for index, word in enumerate(words):
            end = "\n" if index % args.n == args.n - 1 or index == len(words) - 1 else ""
            print(word.ljust(col_width), end=end)


if __name__ == "__main__":
    main()
