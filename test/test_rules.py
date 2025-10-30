import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import alternative_method as file_to_test


def test_substring_gating_requires_len_3():
    """Test that substring checks (c4,c5,c6,c7) only trigger if the relevant name part is longer than 2 characters."""
    # Test too short last name (not allowed)
    i_first_a = "e"  # Example initial of first name
    last_a_short = "ku"  # Example last name
    prefix_b = "ekulmala20"
    c4_when_short = file_to_test.substring_hit(i_first_a, last_a_short, prefix_b)
    assert c4_when_short is False

    # Test longer last name (allowed)
    last_a_long = "kulmala"
    prefix_b2 = "ekulmala20"
    c4_when_long = file_to_test.substring_hit(i_first_a, last_a_long, prefix_b2)
    assert c4_when_long is True

def test_c2_prefixes():
    """Test that c2 similarity is set to 0.0 if either email prefix is in the BANNED set.
    If prefixes are not in BANNED set, similarity is computed normally."""
    
    # Test BANNED prefixes:
    pa = "github"
    pb = "github"
    c2 = file_to_test.c2_hit(pa, pb)
    assert c2 == 0.0
    pa = "mail"
    pb = "mail"
    c2 = file_to_test.c2_hit(pa, pb)
    assert c2 == 0.0
    pa = "user"
    pb = "user"
    c2 = file_to_test.c2_hit(pa, pb)
    assert c2 == 0.0
    pa = "github"
    pb = "eemil.kulmala"
    c2 = file_to_test.c2_hit(pa, pb)
    assert c2 == 0.0
    pa = "eemil.kulmala"
    pb = "mail"
    c2 = file_to_test.c2_hit(pa, pb)
    assert c2 == 0.0

    # Test non-BANNED prefix:
    pa = "eemil.kulmala"
    pb = "eemil.kulmala"
    c2 = file_to_test.c2_hit(pa, pb)
    assert c2 == 1.0

def test_t3_acceptance_rule_variants():
    """Test different scenarios of the acceptance rule."""

    # Single C2 true -> accepted
    assert file_to_test.is_accepted(c1=0.4,
                                    c2=1.0,
                                    c31=0.4,
                                    c32=0.4,
                                    c4=False,
                                    c5=False,
                                    c6=False,
                                    c7=False,
                                    t=0.7) is True

    # Single non-C2 true -> rejected
    assert file_to_test.is_accepted(c1=1.0,
                                    c2=0.0,
                                    c31=0.4,
                                    c32=0.4,
                                    c4=False,
                                    c5=False,
                                    c6=False,
                                    c7=False,
                                    t=0.7) is False

    # Two conditions (C1 and C3) true -> accepted
    assert file_to_test.is_accepted(c1=1.0,
                                    c2=0.2,
                                    c31=0.8,
                                    c32=0.9,
                                    c4=False,
                                    c5=False,
                                    c6=False,
                                    c7=False,
                                    t=0.7) is True

    # Using two substring booleans -> accepted
    assert file_to_test.is_accepted(c1=0.4,
                                    c2=0.0,
                                    c31=0.4,
                                    c32=0.4,
                                    c4=True,
                                    c5=False,
                                    c6=True,
                                    c7=False,
                                    t=0.7) is True
