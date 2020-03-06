import pytest
import math
import numpy as np

import sampler
import audits.bravo as bravo

seed = '12345678901234567890abcdefghijklmnopqrstuvwxyz😊'
risk_limit = .1


def test_expected_sample_sizes():
    # Test expected sample sizes computation

    true_asns = {
        'test1': 119,
        'test2': 22,
        'test3': -1,
        'test4': -1,
        'test5': 1000,
        'test6': 238,
        'test7': 101,
        'test8': 34,
        'test9': -1,
        'test10': 48,
    }

    margins = sampler.compute_margins(contests)

    computed_asns = bravo.get_expected_sample_sizes(risk_limit, contests, margins,
                                                    round0_sample_results)
    for contest in true_asns:
        expected = true_asns[contest]
        computed = computed_asns[contest]

        assert expected == computed, 'get_expected_sample_sizes failed in {}: got {}, expected {}'.format(
            contest, computed, expected)


def test_expected_sample_sizes_second_round():
    # Test expected sample sizes computation

    true_asns = {
        'test1': -12,
        'test2': 42,
        'test3': -1,
        'test4': -1,
        'test5': 1000,
        'test6': -2,
        'test7': -28,
        'test8': 14,
        'test9': -1,
        'test10': -52,
    }

    margins = sampler.compute_margins(contests)

    computed_asns = bravo.get_expected_sample_sizes(risk_limit, contests, margins,
                                                    round1_sample_results)
    for contest in true_asns:
        expected = true_asns[contest]
        computed = computed_asns[contest]

        assert expected == computed, 'get_expected_sample_sizes failed in {}: got {}, expected {}'.format(
            contest, computed, expected)


def test_bravo_sample_sizes():
    # Test bravo sample simulator
    # Test without sample
    expected_size1 = 1599
    r0_sample_win = 0
    r0_sample_rup = 0

    computed_size1 = math.ceil(
        bravo.bravo_sample_sizes(risk_limit=risk_limit,
                                 p_w=.4,
                                 p_r=.32,
                                 sample_w=r0_sample_win,
                                 sample_r=r0_sample_rup,
                                 p_completion=.9))
    delta = expected_size1 - computed_size1

    assert not delta, 'bravo_sample_sizes failed: got {}, expected {}'.format(
        computed_size1, expected_size1)

    expected_size1 = 6067

    computed_size1 = math.ceil(
        bravo.bravo_sample_sizes(risk_limit=risk_limit,
                                 p_w=.36,
                                 p_r=.32,
                                 sample_w=r0_sample_win,
                                 sample_r=r0_sample_rup,
                                 p_completion=.9))
    delta = expected_size1 - computed_size1

    assert not delta, 'bravo_sample_sizes failed: got {}, expected {}'.format(
        computed_size1, expected_size1)

    expected_size1 = 2475

    computed_size1 = math.ceil(
        bravo.bravo_sample_sizes(risk_limit=risk_limit,
                                 p_w=.36,
                                 p_r=.32,
                                 sample_w=r0_sample_win,
                                 sample_r=r0_sample_rup,
                                 p_completion=.6))
    delta = expected_size1 - computed_size1

    assert not delta, 'bravo_sample_sizes failed: got {}, expected {}'.format(
        computed_size1, expected_size1)

    expected_size1 = 5657

    computed_size1 = math.ceil(
        bravo.bravo_sample_sizes(risk_limit=risk_limit,
                                 p_w=.52,
                                 p_r=.47,
                                 sample_w=r0_sample_win,
                                 sample_r=r0_sample_rup,
                                 p_completion=.9))
    delta = expected_size1 - computed_size1

    assert not delta, 'bravo_sample_sizes failed: got {}, expected {}'.format(
        computed_size1, expected_size1)


def test_bravo_sample_sizes_round1_finish():
    # Guarantee that the audit should have finished
    r0_sample_win = 10000
    r0_sample_rup = 0
    expected_size1 = 0

    computed_size1 = math.ceil(
        bravo.bravo_sample_sizes(risk_limit,
                                 p_w=.52,
                                 p_r=.47,
                                 sample_w=r0_sample_win,
                                 sample_r=r0_sample_rup,
                                 p_completion=.9))
    delta = expected_size1 - computed_size1

    assert not delta, 'bravo_sample_sizes failed: got {}, expected {}'.format(
        computed_size1, expected_size1)


def test_bravo_sample_sizes_round1_incomplete():
    expected_size1 = 2636
    r0_sample_win = 2923
    r0_sample_rup = 2735

    computed_size1 = math.ceil(
        bravo.bravo_sample_sizes(risk_limit,
                                 p_w=.52,
                                 p_r=.47,
                                 sample_w=r0_sample_win,
                                 sample_r=r0_sample_rup,
                                 p_completion=.9))
    delta = expected_size1 - computed_size1

    assert not delta, 'bravo_sample_sizes failed: got {}, expected {}'.format(
        computed_size1, expected_size1)


def test_bravo_expected_prob():
    # Test bravo sample simulator
    # Test without sample
    expected_prob1 = .52
    r0_sample_win = round0_sample_results['test1']['cand1']
    r0_sample_rup = round0_sample_results['test1']['cand2']

    computed_prob1 = round(
        bravo.expected_prob(risk_limit,
                            p_w=.6,
                            p_r=.4,
                            sample_w=r0_sample_win,
                            sample_r=r0_sample_rup,
                            asn=119), 2)
    delta = expected_prob1 - computed_prob1

    assert not delta, 'bravo_simulator failed: got {}, expected {}'.format(
        computed_prob1, expected_prob1)


def test_compute_risk():
    # Test computing sample
    expected_Ts = {
        'test1': {
            ('cand1', 'cand2'): .07
        },
        'test2': {
            ('cand1', 'cand2'): 10.38,
            ('cand1', 'cand3'): 0,
        },
        'test3': {
            ('cand1', ): 1
        },
        'test4': {
            ('cand1', ): 1
        },
        'test5': {
            ('cand1', 'cand2'): 1
        },
        'test6': {
            ('cand1', 'cand2'): 0.08,
            ('cand1', 'cand3'): 0.08,
        },
        'test7': {
            ('cand1', 'cand3'): 0.01,
            ('cand2', 'cand3'): 0.04,
        },
        'test8': {
            ('cand1', 'cand3'): 0.0,
            ('cand2', 'cand3'): 0.22,
        },
        'test9': {
            ('cand1', ): 1,
            ('cand2', ): 1,
        },
        'test10': {
            ('cand1', 'cand3'): 0,
            ('cand2', 'cand3'): 0.01,
        },
    }

    expected_decisions = {
        'test1': True,
        'test2': False,
        'test3': False,
        'test4': False,
        'test5': False,
        'test6': True,
        'test7': True,
        'test8': False,
        'test9': False,
        'test10': True,
    }

    margins = sampler.compute_margins(contests)
    for contest, sample in round1_sample_results.items():
        T, decision = bravo.compute_risk(risk_limit, margins[contest], sample)
        expected_T = expected_Ts[contest]
        for pair in expected_T:
            diff = T[pair] - expected_T[pair]
            assert abs(diff) < .01, 'Risk compute for {} failed! Expected {}, got {}'.format(
                contest, expected_Ts[contest][pair], T[pair])

        expected_decision = expected_decisions[contest]
        assert decision == expected_decision, 'Risk decision for {} failed! Expected {}, got{}'.format(
            contest, expected_decision, decision)


contests = {
    'test1': {
        'cand1': 600,
        'cand2': 400,
        'ballots': 1000,
        'numWinners': 1
    },
    'test2': {
        'cand1': 600,
        'cand2': 200,
        'cand3': 100,
        'ballots': 900,
        'numWinners': 1
    },
    'test3': {
        'cand1': 100,
        'ballots': 100,
        'numWinners': 1
    },
    'test4': {
        'cand1': 100,
        'ballots': 100,
        'numWinners': 1
    },
    'test5': {
        'cand1': 500,
        'cand2': 500,
        'ballots': 1000,
        'numWinners': 1
    },
    'test6': {
        'cand1': 300,
        'cand2': 200,
        'cand3': 200,
        'ballots': 1000,
        'numWinners': 1
    },
    'test7': {
        'cand1': 300,
        'cand2': 200,
        'cand3': 100,
        'ballots': 700,
        'numWinners': 2
    },
    'test7': {
        'cand1': 300,
        'cand2': 200,
        'cand3': 100,
        'ballots': 700,
        'numWinners': 2
    },
    'test8': {
        'cand1': 300,
        'cand2': 300,
        'cand3': 100,
        'ballots': 700,
        'numWinners': 2
    },
    'test9': {
        'cand1': 300,
        'cand2': 200,
        'ballots': 700,
        'numWinners': 2
    },
    'test10': {
        'cand1': 600,
        'cand2': 300,
        'cand3': 100,
        'ballots': 1000,
        'numWinners': 2
    },
}

# Useful test data
round0_sample_results = {
    'test1': {
        'cand1': 0,
        'cand2': 0,
    },
    'test2': {
        'cand1': 0,
        'cand2': 0,
        'cand3': 0,
    },
    'test3': {
        'cand1': 0,
    },
    'test4': {
        'cand1': 0,
    },
    'test5': {
        'cand1': 0,
        'cand2': 0,
    },
    'test6': {
        'cand1': 0,
        'cand2': 0,
        'cand3': 0
    },
    'test7': {
        'cand1': 0,
        'cand2': 0,
        'cand3': 0
    },
    'test8': {
        'cand1': 0,
        'cand2': 0,
        'cand3': 0
    },
    'test9': {
        'cand1': 0,
        'cand2': 0,
        'cand3': 0
    },
    'test10': {
        'cand1': 0,
        'cand2': 0,
        'cand3': 0
    },
}

round1_sample_results = {
    'test1': {
        'cand1': 72,
        'cand2': 47
    },
    'test2': {
        'cand1': 25,
        'cand2': 18,
        'cand3': 5,
    },
    'test3': {
        'cand1': 0
    },
    'test4': {
        'cand1': 100
    },
    'test5': {
        'cand1': 500,
        'cand2': 500,
    },
    'test6': {
        'cand1': 72,
        'cand2': 48,
        'cand3': 48
    },
    'test7': {
        'cand1': 30,
        'cand2': 25,
        'cand3': 10
    },
    'test8': {
        'cand1': 72,
        'cand2': 55,
        'cand3': 30
    },
    'test9': {
        'cand1': 1,
        'cand2': 1,
    },
    'test10': {
        'cand1': 60,
        'cand2': 30,
        'cand3': 10
    },
}

true_sample_sizes = {
    'test1': {
        'asn': {
            'size': 119,
            'prob': .52
        },
        .7: 184,
        .8: 244,
        .9: 351,
    },
    'test2': {
        'asn': {
            'size': 22,
            'prob': .6
        },
        .7: 32,
        .8: 41,
        .9: 57,
    },
    'test3': {
        'asn': {
            'size': -1,
            'prob': -1
        },
        .7: -1,
        .8: -1,
        .9: -1,
    },
    'test4': {
        'asn': {
            'size': -1,
            'prob': -1
        },
        .7: -1,
        .8: -1,
        .9: -1,
    },
    'test5': {
        'asn': {
            'size': 1000,
            'prob': 1
        },
        .7: 1000,
        .8: 1000,
        .9: 1000
    },
    'test6': {
        'asn': {
            'size': 238,
            'prob': .79
        },
        .7: 368,
        .8: 488,
        .9: 702
    },
    'test7': {
        'asn': {
            'size': 101,
            'prob': None,
        },
    },
    'test8': {
        'asn': {
            'size': 59,
            'prob': None,
        },
    },
    'test9': {
        'asn': {
            'size': -1,
            'prob': None,
        },
    },
    'test10': {
        'asn': {
            'size': 48,
            'prob': None,
        },
    },
}
