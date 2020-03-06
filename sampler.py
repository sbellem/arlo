# Handles generating sample sizes and taking samples
import math
import numpy as np
from scipy import stats
import consistent_sampler
import operator

import audits.macro as macro


def compute_margins(contests):
    """
    Method that computes all margins for the contests in <contests>, and
    returns a mapping of contest name to margin info.

    Input:
        contests - dictionary of targeted contests. Maps:
                    {
                        contest: {
                            candidate1: votes,
                            candidate2: votes,
                            ...
                            'ballots': ballots,
                            'winners': winners
                        }
                        ...
                    }
    Output:
        margins - dictionary of diluted margin info:
                    {
                        contest: {
                            'winners': {
                                winner1: {
                                          'p_w': p_w,     # Proportion of ballots for this winner
                                          's_w': 's_w'    # proportion of votes for this winner
                                          'swl': {      # fraction of votes for w among (w, l)
                                                'loser1':  s_w/(s_w + s_l1),
                                                ...,
                                                'losern':  s_w/(s_w + s_ln)
                                            }
                                          },
                                ...,
                                winnern: {...} ]
                            'losers': {
                                loser1: {
                                          'p_l': p_l,     # Proportion of votes for this loser
                                          's_l': s_l,     # Proportion of ballots for this loser
                                          },
                                ...,
                                losern: {...} ]

                        }
                    }

    """

    margins = {}
    for contest in contests:
        margins[contest] = {'winners': {}, 'losers': {}}

        print(contests)
        cand_vec = sorted([(cand, contests[contest][cand])
                           for cand in contests[contest] if cand not in ['numWinners', 'ballots']],
                          key=operator.itemgetter(1),
                          reverse=True)

        if 'numWinners' not in contests[contest]:
            num_winners = 1
        else:
            num_winners = contests[contest]['numWinners']
        winners = cand_vec[:num_winners]
        losers = cand_vec[num_winners:]

        ballots = contests[contest]['ballots']

        v_wl = sum([c[1] for c in winners + losers])

        margins[contest]['winners']: {}
        margins[contest]['losers']: {}

        for loser in losers:
            margins[contest]['losers'][loser[0]] = {
                'p_l': loser[1] / ballots,
                's_l': loser[1] / v_wl
            }

        for winner in winners:
            s_w = winner[1] / v_wl

            swl = {}
            for loser in margins[contest]['losers']:
                s_l = margins[contest]['losers'][loser]['s_l']
                swl[loser] = s_w / (s_w + s_l)

            margins[contest]['winners'][winner[0]] = {
                'p_w': winner[1] / ballots,
                's_w': s_w,
                'swl': swl
            }

    return margins


def draw_sample(seed,
                audit_type,
                targeted_contests,
                manifest,
                sample_size,
                num_sampled=0,
                batch_results=None):
    """
    Draws uniform random sample with replacement of size <sample_size> from the
    provided ballot manifest.

    Inputs:
        sample_size - number of ballots to randomly draw
        num_sampled - number of ballots that have already been sampled
        manifest - mapping of batches to the ballots they contain:
                    {
                        batch1: num_balots,
                        batch2: num_ballots,
                        ...
                    }

    Outputs:
        sample - list of 'tickets', consisting of:
                [
                    (
                        '0.235789114', # ticket number
                        (<batch>, <ballot number>), # id, here a tuple (batch, ballot)
                        1                           # number of times this item has been picked
                    ),
                    ...
                ]
    """

    margins = compute_margins(targeted_contests)
    if audit_type == 'MACRO':
        # Here we do PPEB.

        assert batch_results, 'Must have batch-level results to use MACRO'

        U = macro.compute_U(batch_results, targeted_contests, margins)

        # Map each batch to its weighted probability of being picked
        batch_to_prob = {}
        min_prob = 1
        # Get u_ps
        for batch in batch_results:
            error = macro.compute_max_error(batch_results[batch], targeted_contests, margins)

            # Probability of being picked is directly related to how much this
            # batch contributes to the overall possible error
            batch_to_prob[batch] = error / U

            if error / U < min_prob:
                min_prob = error / U

        sample_from = []
        # Now build faux list of batches, where each batch appears a number of
        # times proportional to its prob
        for batch in batch_to_prob:
            times = int(batch_to_prob[batch] / min_prob)

            for i in range(times):
                # We have to create "unique" records for the sampler, so we add
                # a '.n' to the batch name so we know which duplicate it is.
                sample_from.append('{}.{}'.format(batch, i))

        # Now draw the sample
        faux_sample = list(
            consistent_sampler.sampler(sample_from,
                                       seed=seed,
                                       take=sample_size + num_sampled,
                                       with_replacement=True,
                                       output='tuple'))[num_sampled:]

        # here we take off the decimals.
        sample = []
        for i in faux_sample:
            sample.append((i[0], i[1].split('.')[0], i[2]))
    else:
        ballots = []
        # First build a faux list of ballots
        for batch in manifest:
            for i in range(manifest[batch]):
                ballots.append((batch, i))

        sample = list(
            consistent_sampler.sampler(ballots,
                                       seed=seed,
                                       take=sample_size + num_sampled,
                                       with_replacement=True,
                                       output='tuple'))[num_sampled:]

    return sample
