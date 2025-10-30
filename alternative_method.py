import csv
import pandas as pd
import unicodedata
import string
from itertools import combinations
from Levenshtein import ratio as sim
import os


def read_devs_from_csv(location, filename):
    """Read developers from a CSV file located at the specified location and filename.
    Expects the CSV to have a header row."""
    DEVS = []
    with open(os.path.join(location, filename), 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            DEVS.append(row)
    # First element is header, skip
    return DEVS[1:]

def process(dev):
    """Pre-process a developer's name and email to extract relevant components."""
    name: str = dev[0]

    # Remove punctuation
    trans = name.maketrans("", "", string.punctuation)
    name = name.translate(trans)
    # Remove accents, diacritics
    name = unicodedata.normalize('NFKD', name)
    name = ''.join([c for c in name if not unicodedata.combining(c)])
    # Lowercase
    name = name.casefold()
    # Strip whitespace
    name = " ".join(name.split())


    # Attempt to split name into firstname, lastname by space
    parts = name.split(" ")
    # Expected case
    if len(parts) == 2:
        first, last = parts
    # If there is no space, firstname is full name, lastname empty
    elif len(parts) == 1:
        first, last = name, ""
    # If there is more than 1 space, firstname is until first space, rest is lastname
    else:
        first, last = parts[0], " ".join(parts[1:])

    # Take initials of firstname and lastname if they are long enough
    i_first = first[0] if len(first) > 1 else ""
    i_last = last[0] if len(last) > 1 else ""

    # Determine email prefix
    email: str = dev[1]
    prefix = email.split("@")[0]

    return name, first, last, i_first, i_last, email, prefix

def c2_hit(prefix_a, prefix_b):
    """Compute c2 similarity, setting to 0.0 if either prefix is in BANNED set."""
    BANNED = {"github", "mail", "user", "test", "example"}
    if prefix_a in BANNED or prefix_b in BANNED:
        return 0.0
    else:
        return sim(prefix_b, prefix_a)

def substring_hit(i_initial, other_name, other_prefix):
    """Check if initial and other_name are substrings of other_prefix, requiring other_name to be longer than 2 characters."""
    return (i_initial != "") and (len(other_name) > 2) and (other_name in other_prefix) and (i_initial in other_prefix)

def is_accepted(c1, c2, c31, c32, c4, c5, c6, c7, t):
    """Determine if a pair is accepted based on the acceptance rule."""
    c1_check = (c1 >= t)
    c2_check = (c2 >= t)
    c3_check = (c31 >= t) and (c32 >= t)
    at_least_two = sum([c1_check, c3_check, c4, c5, c6, c7]) >= 2
    return c2_check or at_least_two

def compute_similarity(DEVS, t):
    SIMILARITY = []
    for dev_a, dev_b in combinations(DEVS, 2):
        # Pre-process both developers
        name_a, first_a, last_a, i_first_a, i_last_a, email_a, prefix_a = process(dev_a)
        name_b, first_b, last_b, i_first_b, i_last_b, email_b, prefix_b = process(dev_b)

        # Conditions of the heuristic
        c1 = sim(name_a, name_b)
        c2 = c2_hit(prefix_a, prefix_b)
        c31 = sim(first_a, first_b)
        c32 = sim(last_a, last_b)
        c4 = substring_hit(i_first_a, last_a, prefix_b)
        c5 = substring_hit(i_last_a, first_a, prefix_b)
        c6 = substring_hit(i_first_b, last_b, prefix_a)
        c7 = substring_hit(i_last_b, first_b, prefix_a)
        
        # Save similarity data for accepted conditions. Original names are saved
        if is_accepted(c1, c2, c31, c32, c4, c5, c6, c7, t):
            SIMILARITY.append([dev_a[0], email_a, dev_b[0], email_b, c1, c2, c31, c32, c4, c5, c6, c7])
    return SIMILARITY


def main():
    # Read csv file with name, dev columns
    DEVS = []
    DEVS = read_devs_from_csv("project1devs", "devs.csv")

    # Compute similarity for all possible pairs
    t=0.7  # Similarity threshold
    SIMILARITY = []
    SIMILARITY = compute_similarity(DEVS, t)
    
    # Save data in DataFrame
    cols = ["name_1", "email_1", "name_2", "email_2", "c1", "c2",
            "c3.1", "c3.2", "c4", "c5", "c6", "c7"]
    df = pd.DataFrame(SIMILARITY, columns=cols)
    # Save to CSV
    df.to_csv(os.path.join("project1devs", f"alternative_similarity_t={t}.csv"), index=False, header=True)

    print(f"Alternative method: {len(df)} similar pairs found with threshold {t}")


if __name__ == "__main__":
    main()
