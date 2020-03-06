import pytest
import sampler

seed = '12345678901234567890abcdefghijklmnopqrstuvwxyz😊'
risk_limit = .1


@pytest.fixture
def macro_batches():
    batches = {}

    # 10 batches will have max error of .08
    for i in range(10):
        batches['pct {}'.format(i)] = {'test1': {'cand1': 40, 'cand2': 10, 'ballots': 50}}
        # 10 batches will have max error of .04
    for i in range(11, 20):
        batches['pct {}'.format(i)] = {'test1': {'cand1': 20, 'cand2': 30, 'ballots': 50}}

    yield batches


def test_draw_sample():
    # Test getting a sample
    manifest = {
        'pct 1': 25,
        'pct 2': 25,
        'pct 3': 25,
        'pct 4': 25,
    }

    sample = sampler.draw_sample(seed, 'BRAVO', bravo_contests, manifest, 20)

    for i, item in enumerate(sample):
        expected = expected_sample[i]
        assert item == expected, 'Draw sample failed: got {}, expected {}'.format(item, expected)


def test_draw_more_samples():
    # Test getting a sample
    manifest = {
        'pct 1': 25,
        'pct 2': 25,
        'pct 3': 25,
        'pct 4': 25,
    }

    samp_size = 10
    sample = sampler.draw_sample(seed, 'BRAVO', bravo_contests, manifest, 10)
    assert samp_size == len(sample), 'Received sample of size {}, expected {}'.format(
        samp_size, len(sample))

    for i, item in enumerate(sample):
        expected = expected_first_sample[i]
        assert item == expected, 'Draw sample failed: got {}, expected {}'.format(item, expected)

    samp_size = 10
    sample = sampler.draw_sample(seed, 'BRAVO', bravo_contests, manifest, 10, num_sampled=10)
    assert samp_size == len(sample), 'Received sample of size {}, expected {}'.format(
        samp_size, len(sample))
    for i, item in enumerate(sample):
        expected = expected_second_sample[i]
        assert item == expected, 'Draw sample failed: got {}, expected {}'.format(item, expected)


def test_draw_macro_sample(macro_batches):
    # Test getting a sample
    sample = sampler.draw_sample(seed, 'MACRO', macro_contests, {}, 10, batch_results=macro_batches)

    for i, item in enumerate(sample):
        expected = expected_macro_sample[i]
        assert item == expected, 'Draw sample failed: got {}, expected {}'.format(item, expected)


def test_draw_more_macro_sample(macro_batches):
    # Test getting a sample
    samp_size = 5
    sample = sampler.draw_sample(seed,
                                 'MACRO',
                                 macro_contests, {},
                                 samp_size,
                                 batch_results=macro_batches)
    assert samp_size == len(sample), 'Received sample of size {}, expected {}'.format(
        samp_size, len(sample))

    for i, item in enumerate(sample):
        expected = expected_first_macro_sample[i]
        assert item == expected, 'Draw sample failed: got {}, expected {}'.format(item, expected)

    samp_size = 5
    sample = sampler.draw_sample(seed,
                                 'MACRO',
                                 macro_contests, {},
                                 samp_size,
                                 num_sampled=5,
                                 batch_results=macro_batches)
    assert samp_size == len(sample), 'Received sample of size {}, expected {}'.format(
        samp_size, len(sample))
    for i, item in enumerate(sample):
        expected = expected_second_macro_sample[i]
        assert item == expected, 'Draw sample failed: got {}, expected {}'.format(item, expected)


def test_compute_margins():
    margins = sampler.compute_margins(bravo_contests)
    for contest in margins:
        true_margins_for_contest = true_margins[contest]
        computed_margins_for_contest = margins[contest]

        for winner in true_margins_for_contest['winners']:
            expected = round(true_margins_for_contest['winners'][winner]['p_w'], 5)
            computed = round(computed_margins_for_contest['winners'][winner]['p_w'], 5)
            assert expected == computed, '{} p_w failed: got {}, expected {}'.format(
                contest, computed, expected)

            expected = round(true_margins_for_contest['winners'][winner]['s_w'], 5)
            computed = round(computed_margins_for_contest['winners'][winner]['s_w'], 5)
            assert expected == computed, '{} s_w failed: got {}, expected {}'.format(
                contest, computed, expected)

            for cand in true_margins_for_contest['winners'][winner]['swl']:
                expected = round(true_margins_for_contest['winners'][winner]['swl'][cand], 5)
                computed = round(computed_margins_for_contest['winners'][winner]['swl'][cand], 5)
                assert expected == computed, '{} swl failed: got {}, expected {}'.format(
                    contest, computed, expected)

        for loser in true_margins_for_contest['losers']:
            expected = round(true_margins_for_contest['losers'][loser]['p_l'], 5)
            computed = round(computed_margins_for_contest['losers'][loser]['p_l'], 5)
            assert expected == computed, '{} p_l failed: got {}, expected {}'.format(
                contest, computed, expected)

            expected = round(true_margins_for_contest['losers'][loser]['s_l'], 5)
            computed = round(computed_margins_for_contest['losers'][loser]['s_l'], 5)
            assert expected == computed, '{} s_l failed: got {}, expected {}'.format(
                contest, computed, expected)


bravo_contests = {
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

macro_contests = {
    'test1': {
        'cand1': 600,
        'cand2': 400,
        'ballots': 1000,
        'numWinners': 1
    },
}

expected_sample = [('0.000617786', ('pct 2', 3), 1), ('0.002991631', ('pct 3', 24), 1),
                   ('0.017930028', ('pct 4', 19), 1), ('0.025599454', ('pct 3', 15), 1),
                   ('0.045351055', ('pct 1', 7), 1), ('0.063913979', ('pct 1', 8), 1),
                   ('0.064553852', ('pct 1', 22), 1), ('0.078998835', ('pct 1', 20), 1),
                   ('0.090240829', ('pct 3', 12), 1), ('0.096136506', ('pct 1', 20), 2),
                   ('0.104280162', ('pct 4', 17), 1), ('0.111195681', ('pct 1', 4), 1),
                   ('0.114438612', ('pct 4', 3), 1), ('0.130457464', ('pct 2', 1), 1),
                   ('0.133484785', ('pct 1', 12), 1), ('0.134519219', ('pct 3', 20), 1),
                   ('0.135840440', ('pct 3', 10), 1), ('0.138772253', ('pct 4', 20), 1),
                   ('0.145377629', ('pct 2', 9), 1), ('0.146681466', ('pct 1', 20), 3)]

expected_macro_sample = [('0.003875995', 'pct 16', 1), ('0.011835450', 'pct 2', 1),
                         ('0.022865957', 'pct 2', 2), ('0.035732442', 'pct 3', 1),
                         ('0.125751540', 'pct 2', 3), ('0.136070319', 'pct 18', 1),
                         ('0.150306323', 'pct 6', 1), ('0.176060218', 'pct 4', 1),
                         ('0.183200120', 'pct 13', 1), ('0.191343085', 'pct 18', 2)]

expected_first_sample = [
    ('0.000617786', ('pct 2', 3), 1),
    ('0.002991631', ('pct 3', 24), 1),
    ('0.017930028', ('pct 4', 19), 1),
    ('0.025599454', ('pct 3', 15), 1),
    ('0.045351055', ('pct 1', 7), 1),
    ('0.063913979', ('pct 1', 8), 1),
    ('0.064553852', ('pct 1', 22), 1),
    ('0.078998835', ('pct 1', 20), 1),
    ('0.090240829', ('pct 3', 12), 1),
    ('0.096136506', ('pct 1', 20), 2),
]

expected_second_sample = [('0.104280162', ('pct 4', 17), 1), ('0.111195681', ('pct 1', 4), 1),
                          ('0.114438612', ('pct 4', 3), 1), ('0.130457464', ('pct 2', 1), 1),
                          ('0.133484785', ('pct 1', 12), 1), ('0.134519219', ('pct 3', 20), 1),
                          ('0.135840440', ('pct 3', 10), 1), ('0.138772253', ('pct 4', 20), 1),
                          ('0.145377629', ('pct 2', 9), 1), ('0.146681466', ('pct 1', 20), 3)]

expected_first_macro_sample = [
    ('0.003875995', 'pct 16', 1),
    ('0.011835450', 'pct 2', 1),
    ('0.022865957', 'pct 2', 2),
    ('0.035732442', 'pct 3', 1),
    ('0.125751540', 'pct 2', 3),
]

expected_second_macro_sample = [('0.136070319', 'pct 18', 1), ('0.150306323', 'pct 6', 1),
                                ('0.176060218', 'pct 4', 1), ('0.183200120', 'pct 13', 1),
                                ('0.191343085', 'pct 18', 2)]

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

true_margins = {
    'test1': {
        'winners': {
            'cand1': {
                'p_w': .6,
                's_w': .6,
                'swl': {
                    'cand2': .6
                }
            }
        },
        'losers': {
            'cand2': {
                'p_l': .4,
                's_l': .4
            }
        }
    },
    'test2': {
        'winners': {
            'cand1': {
                'p_w': 2 / 3,
                's_w': 2 / 3,
                'swl': {
                    'cand2': 6 / 8,
                    'cand3': 6 / 7
                }
            }
        },
        'losers': {
            'cand2': {
                'p_l': 2 / 9,
                's_l': 2 / 9
            },
            'cand3': {
                'p_l': 1 / 9,
                's_l': 1 / 9
            }
        }
    },
    'test3': {
        'winners': {
            'cand1': {
                'p_w': 1,
                's_w': 1,
                'swl': {}
            }
        },
        'losers': {}
    },
    'test4': {
        'winners': {
            'cand1': {
                'p_w': 1,
                's_w': 1,
                'swl': {}
            }
        },
        'losers': {}
    },
    'test5': {
        'winners': {
            'cand1': {
                'p_w': .5,
                's_w': .5,
                'swl': {
                    'cand2': .5
                }
            }
        },
        'losers': {
            'cand2': {
                'p_l': .5,
                's_l': .5
            }
        }
    },
    'test6': {
        'winners': {
            'cand1': {
                'p_w': .3,
                's_w': 300 / 700,
                'swl': {
                    'cand2': 300 / (300 + 200),
                    'cand3': 300 / (300 + 200)
                }
            }
        },
        'losers': {
            'cand2': {
                'p_l': .2,
                's_l': 200 / 700
            },
            'cand3': {
                'p_l': .2,
                's_l': 200 / 700
            }
        }
    },
    'test7': {
        'winners': {
            'cand1': {
                'p_w': 300 / 700,
                's_w': 300 / 600,
                'swl': {
                    'cand3': 300 / (300 + 100)
                }
            },
            'cand2': {
                'p_w': 200 / 700,
                's_w': 200 / 600,
                'swl': {
                    'cand3': 200 / (200 + 100)
                }
            }
        },
        'losers': {
            'cand3': {
                'p_l': 100 / 700,
                's_l': 100 / 600
            }
        }
    },
    'test8': {
        'winners': {
            'cand1': {
                'p_w': 300 / 700,
                's_w': 300 / 700,
                'swl': {
                    'cand3': 300 / (300 + 100)
                }
            },
            'cand2': {
                'p_w': 300 / 700,
                's_w': 300 / 700,
                'swl': {
                    'cand3': 300 / (300 + 100)
                }
            }
        },
        'losers': {
            'cand3': {
                'p_l': 100 / 700,
                's_l': 100 / 700
            }
        }
    },
    'test9': {
        'winners': {
            'cand1': {
                'p_w': 300 / 700,
                's_w': 300 / 500,
                'swl': {}
            },
            'cand2': {
                'p_w': 200 / 700,
                's_w': 200 / 500,
                'swl': {}
            }
        },
        'losers': {}
    },
    'test10': {
        'winners': {
            'cand1': {
                'p_w': 600 / 1000,
                's_w': 600 / 1000,
                'swl': {
                    'cand3': 600 / 700
                }
            },
            'cand2': {
                'p_w': 300 / 1000,
                's_w': 300 / 1000,
                'swl': {
                    'cand3': 300 / 400
                }
            }
        },
        'losers': {
            'cand3': {
                'p_l': 100 / 1000,
                's_l': 100 / 1000
            }
        }
    }
}
