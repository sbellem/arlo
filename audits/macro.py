"""

An implemenation of MACRO for batch comparison audits.

MACRO was developed by Philip Stark
(see https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1443314 for the publication).


"""

import math
from typing import Dict


def compute_max_error(contest, batch_results, margins):
    """
    Computes the maximum possible error in this batch

    Inputs:
        contest - the contest we want the error for
        batch_results - the results for this batch
        margins - the margins for this contest

    Outputs:
        the maximum possible overstatement for batch p
    """

    error = 0

    for winner in margins[contest]['winners']:
        for loser in margins[contest]['losers']:
            v_wp = batch_results[contest][winner]
            v_lp = batch_results[contest][loser]

            b_cp = batch_results[contest]['ballots']

            V_wl = contest[winner] - contest[loser]

            u_pwl = ((v_wp - v_lp) + b_cp) / V_wl

            if u_pwl > error:
                error = u_pwl

    return error


def compute_U(reported_results, targeted_contests, margins):
    """
    Computes U, the sum of the batch-wise relative overstatement limits,
    i.e. the maximum amount of possible overstatement in a given election.
    """

    U = 0
    for batch in reported_results:

        U += compute_max_error(reported_results[batch], targeted_contests, margins)

    return U


def compute_error(batch_name, contests, margins, reported_results, sampled_results):
    """
    Computes the error in this batch

    Inputs:
        contests - the contests in the election
        margins - the margins for the election
        reported_results - the reported votes in this batch
        sampled_results - the actual votes in this batch after auditing

    Outputs:
        the maximum across-contest relative overstatement for batch p
    """

    error = 0
    for contest in reported_results[batch_name]:
        for winner in margins[contest]['winners']:
            for loser in margins[contest]['losers']:
                v_wp = reported_results[batch_name][contest][winner]
                v_lp = reported_results[batch_name][contest][loser]

                a_wp = sampled_results[contest][winner]
                a_lp = sampled_results[contest][loser]

                V_wl = contests[contest][winner] - contests[contest][loser]

                e_pwl = ((v_wp - v_lp) - (a_wp - a_lp)) / V_wl

                if e_pwl > error:
                    error = e_pwl

    return error


def get_sample_sizes(risk_limit, reported_results, targeted_contests, margins):
    """
    Computes initial sample sizes parameterized by likelihood that the
    initial sample will confirm the election result, assuming no
    discrepancies.

    Inputs:
        sample_results - if a sample has already been drawn, this will
                         contain its results.

    Outputs:
        samples - dictionary mapping confirmation likelihood to sample size:
                {
                   contest1:  {
                        likelihood1: sample_size,
                        likelihood2: sample_size,
                        ...
                    },
                    ...
                }
    """

    U = self.compute_U(reported_results, targeted_contests, margins)

    return math.ceil(math.log(risk_limit) / (math.log(1 - (1 / U))))


def compute_risk(risk_limit, contest, margins, sample_results):
    """
    Computes the risk-value of <sample_results> based on results in <contest>.

    Inputs:
        margins        - the margins for the contest being audited
        sample_results - mapping of candidates to votes in the (cumulative)
                         sample:

                {
                    candidate1: sampled_votes,
                    candidate2: sampled_votes,
                    ...
                }

    Outputs:
        measurements    - the p-value of the hypotheses that the election
                          result is correct based on the sample, for each winner-loser pair.
        confirmed       - a boolean indicating whether the audit can stop
    """

    p = 1

    U = self.compute_U(contests, margins)

    for batch in sample_results:
        e_p = self.compute_error(batch, \
                                 contest, \
                                 margins,  \
                                 sample_results[batch])

        u_p = self.compute_max_error(batch, contests, margins)

        taint = e_p / u_p

        p *= (1 - 1 / U) / (1 - taint)

        if p < self.risk_limit:
            return p, True

    return p, p < self.risk_limit
