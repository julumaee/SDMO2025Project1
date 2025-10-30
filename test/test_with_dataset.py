import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import csv
import os
import pandas as pd
import alternative_method as file_to_test


def write_devs_csv(base_dir):
    """
    Create test_data/test_devs.csv with a small dataset.
    """
    data_dir = os.path.join(base_dir, "test_data")
    os.makedirs(data_dir, exist_ok=True)
    path = os.path.join(data_dir, "test_devs.csv")

    rows = [
        ["name", "email"],

        # 1. Only c2 will pass
        ["julumaee", "ekulmala20@student.oulu.fi"],
        ["Eemil Kulmala", "ekulmala20@oulu.fi"],

        # 2. Conditions c1 and c3 will pass
        ["Matteo Esposito", "teacher@x.com"],
        ["Matteo Esposito", "despasito@y.com"],

        # 3. Short token substring -> should NOT be accepted
        ["Ja Mi", "joujou@x.com"],
        ["Janne Mikkonen", "jamikkonen@x.com"],

        # 4) Banned prefix in C2: -> c2 must be 0.0, do not accept
        ["Test User", "github@foo.com"],
        ["Another Guy", "github@example.com"],

        # 5) Multiple conditions true -> should be accepted
        ["Alexander Bakhtin", "alexbakh@matteo.com"],
        ["Alex Bakhtin", "bakhtinal@esposito.fi"],     
    ]

    with open(path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(rows)

    return data_dir

def test_with_dataset(tmp_path):
    """
    End-to-end test of the alternative method on a small dataset.
    """
    # Create test data
    base_dir = str(tmp_path)
    data_dir = write_devs_csv(base_dir)

    # Run the algorithm with the test data
    DEVS = []
    DEVS = file_to_test.read_devs_from_csv(data_dir, "test_devs.csv")
    t=0.7  # Similarity threshold
    SIMILARITY = []
    SIMILARITY = file_to_test.compute_similarity(DEVS, t)

    # Save data in DataFrame
    cols = ["name_1", "email_1", "name_2", "email_2", "c1", "c2",
            "c3.1", "c3.2", "c4", "c5", "c6", "c7"]
    df = pd.DataFrame(SIMILARITY, columns=cols)
    # Save to CSV
    df.to_csv(os.path.join(data_dir, "test_similarity.csv"), index=False, header=True)

    # Load output and check
    out_path = os.path.join(data_dir, "test_similarity.csv")
    assert os.path.exists(out_path), f"Expected output CSV not found: {out_path}"

    # Load the output CSV
    df = pd.read_csv(out_path)

    def contains_pair(name1, prefix1, name2, prefix2):
        # pairs are unordered - check both directions
        cond1 = (df["name_1"] == name1) & (df["email_1"] == prefix1) & (df["name_2"] == name2) & (df["email_2"] == prefix2)
        cond2 = (df["name_1"] == name2) & (df["email_1"] == prefix2) & (df["name_2"] == name1) & (df["email_2"] == prefix1)
        return bool((cond1 | cond2).any())

    # 1) Only c2 passess -> should be accepted
    assert contains_pair("julumaee", "ekulmala20@student.oulu.fi",
                         "Eemil Kulmala",  "ekulmala20@oulu.fi"), \
           "C2-only pair should be accepted but was not found."

    # 2) c1 and c3 pass -> should be accepted
    assert contains_pair("Matteo Esposito", "teacher@x.com",
                         "Matteo Esposito", "despasito@y.com"), \
           "C1 and C3 pair should be accepted but was not found."
    
    # 3) Short token substring -> should NOT be accepted
    assert not contains_pair("Ja Mi", "joujou@x.com",
                             "Janne Mikkonen", "jamikkonen@x.com"), \
           "Short token substring pair should NOT be accepted but was found."

    # 4) Banned prefix in C2: -> c2 must be 0.0, do not accept
    assert not contains_pair("Test User", "github@foo.com",
                             "Another Guy",  "github@example.com"), \
           "Banned prefix pair should NOT be accepted but was found."

    # 5) Multiple conditions true -> should be accepted
    assert contains_pair("Alexander Bakhtin", "alexbakh@matteo.com",
                         "Alex Bakhtin", "bakhtinal@esposito.fi"), \
           "Multiple conditions pair should be accepted but was not found."
