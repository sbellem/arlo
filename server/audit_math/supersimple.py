# pylint: disable=invalid-name
import math
from typing import Dict, Tuple
from decimal import Decimal, ROUND_CEILING

from .sampler_contest import Contest

l: Decimal = Decimal(0.5)
gamma: Decimal = Decimal(1.03905)  # This gamma is used in Stark's tool, AGI, and CORLA)

# This sets the expected number of one-vote misstatements at 1 in 1000
o1: Decimal = Decimal(0.001)
u1: Decimal = Decimal(0.001)

# This sets the expected two-vote misstatements at 1 in 10000
o2: Decimal = Decimal(0.0001)
u2: Decimal = Decimal(0.0001)


def nMin(
    alpha: Decimal,
    contest: Contest,
    o1: Decimal,
    o2: Decimal,
    u1: Decimal,
    u2: Decimal,
) -> Decimal:
    """
    Computes a sample size parameterized by expected under and overstatements
    and the margin.
    """
    return (o1 + o2 + u1 + u2).max(
        math.ceil(
            -2
            * gamma
            * (
                alpha.ln()
                + o1 * (1 - 1 / (2 * gamma)).ln()
                + o2 * (1 - 1 / gamma).ln()
                + u1 * (1 + 1 / (2 * gamma)).ln()
                + u2 * (1 + 1 / gamma).ln()
            )
            / Decimal(contest.diluted_margin)
        ),
    )


def get_sample_sizes(
    risk_limit: int, contest: Contest, sample_results: Dict[str, int],
) -> int:
    """
    Computes initial sample sizes parameterized by likelihood that the
    initial sample will confirm the election result, assuming no
    discrepancies.

    Inputs:
        total_ballots  - the total number of ballots cast in the election
        sample_results - if a sample has already been drawn, this will
                         contain its results, of the form:
                         {
                            'sample_size': n,
                            '1-under':     u1,
                            '1-over':      o1,
                            '2-under':     u2,
                            '2-over':      o2,
                         }

    Outputs:
        sample_size    - the sample size needed for this audit
    """

    alpha = Decimal(risk_limit) / 100
    assert alpha < 1

    obs_o1 = Decimal(sample_results["1-over"])
    obs_u1 = Decimal(sample_results["1-under"])
    obs_o2 = Decimal(sample_results["2-over"])
    obs_u2 = Decimal(sample_results["2-under"])
    num_sampled = Decimal(sample_results["sample_size"])

    if num_sampled:
        r1 = Decimal(obs_o1 / num_sampled)
        r2 = Decimal(obs_o2 / num_sampled)
        s1 = Decimal(obs_u1 / num_sampled)
        s2 = Decimal(obs_u2 / num_sampled)
    else:
        r1 = Decimal(o1)
        r2 = Decimal(o2)
        s1 = Decimal(u1)
        s2 = Decimal(u2)

    denom = (
        (1 - Decimal(contest.diluted_margin) / (2 * gamma)).ln()
        - r1 * (1 - 1 / (2 * gamma)).ln()
        - r2 * (1 - 1 / gamma).ln()
        - s1 * (1 + 1 / (2 * gamma)).ln()
        - s2 * (1 + 1 / gamma).ln()
    )

    if denom >= 0:
        return contest.ballots

    n0 = (alpha.ln() / denom).quantize(Decimal(1), rounding=ROUND_CEILING)

    # Round up one-vote differences.
    r1 = (r1 * n0).quantize(Decimal(1.0), rounding=ROUND_CEILING)
    s1 = (s1 * n0).quantize(Decimal(1.0), rounding=ROUND_CEILING)

    return int(nMin(alpha, contest, r1, r2, s1, s2))


# { ballot_id: { contest_id: { choice_id: 0 | 1 }}}
CVRS = Dict[str, Dict[str, Dict[str, int]]]


def compute_risk(
    risk_limit: int, contest: Contest, cvrs: CVRS, sample_cvr: CVRS,
) -> Tuple[float, bool]:
    """
    Computes the risk-value of <sample_results> based on results in <contest>.

    Inputs:
        contests       - the contests and results being audited
        cvrs           - mapping of ballot_id to votes:
                {
                    'ballot_id': {
                        'contest': {
                            'candidate1': 1,
                            'candidate2': 0,
                            ...
                        }
                    ...
                }

        sample_cvr - the CVR of the audited ballots
                {
                    'ballot_id': {
                        'contest': {
                            'candidate1': 1,
                            'candidate2': 0,
                            ...
                        }
                    ...
                }

    Outputs:
        measurements    - the p-value of the hypotheses that the election
                          result is correct based on the sample, for each winner-loser pair.
        confirmed       - a boolean indicating whether the audit can stop
    """

    alpha = Decimal(risk_limit) / 100
    assert alpha < 1

    p = Decimal(1.0)

    V = Decimal(contest.diluted_margin * len(cvrs))

    U = 2 * gamma / Decimal(contest.diluted_margin)

    result = False
    for ballot in sample_cvr:
        e_r = Decimal(0.0)

        if contest.name not in sample_cvr[ballot]:
            continue
        for winner in contest.winners:
            for loser in contest.losers:
                v_w = cvrs[ballot][contest.name][winner]
                a_w = sample_cvr[ballot][contest.name][winner]

                v_l = cvrs[ballot][contest.name][loser]
                a_l = sample_cvr[ballot][contest.name][loser]

                V_wl = Decimal(contest.candidates[winner] - contest.candidates[loser])

                e = Decimal((v_w - a_w) - (v_l - a_l)) / V_wl
                if e > e_r:
                    e_r = e

        denom = (2 * gamma) / V
        p_b = (1 - 1 / U) / (1 - (e_r / denom))
        p *= p_b

    if 0 < p < alpha:
        result = True

    return float(p), result
