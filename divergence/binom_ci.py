#!/usr/bin/env python3
"""
BINOM CI — DIVERGENCE
Clopper-Pearson exact binomial confidence intervals. Standard library
only (math.lgamma for the regularized incomplete beta function, bisection
to invert it) -- same philosophy as every other script in this project,
deliberately not a scipy dependency for one report's worth of numbers.

Small-n proportions in this project (3 of 4 planted defects caught; 3 of
8 runs where anything survived node 5's attack) get quoted as bare
percentages that imply more precision than four or eight trials can
support. This computes the honest interval instead.

    python binom_ci.py 3 4        # k successes, n trials, 95% CI
    python binom_ci.py 3 4 --alpha 0.10

    from binom_ci import clopper_pearson
    lo, hi = clopper_pearson(3, 4)   # (0.194, 0.994) at 95%
"""

import sys
import math
import argparse


def _betacf(a, b, x):
    """Continued fraction for the incomplete beta function (Lentz's
    method) -- the standard numerical-recipes algorithm."""
    MAXIT, EPS, FPMIN = 200, 3e-14, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN:
        d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN:
            d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN:
            c = FPMIN
        d = 1.0 / d
        de = d * c
        h *= de
        if abs(de - 1.0) < EPS:
            break
    return h


def _betai(a, b, x):
    """Regularized incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                   + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def _beta_inv(p, a, b, tol=1e-12, maxit=200):
    """Invert _betai by bisection -- monotonic in x, so this is safe and
    exact to `tol` without needing a derivative."""
    lo, hi = 0.0, 1.0
    for _ in range(maxit):
        mid = (lo + hi) / 2.0
        if _betai(a, b, mid) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < tol:
            break
    return (lo + hi) / 2.0


def clopper_pearson(k, n, alpha=0.05):
    """Exact (Clopper-Pearson) two-sided (1-alpha) confidence interval
    for a binomial proportion k/n. Exact in the sense of guaranteed
    coverage >= 1-alpha, not approximated by a normal/Wilson interval --
    the right choice at n this small."""
    if not (0 <= k <= n):
        raise ValueError(f"k={k} must be between 0 and n={n}")
    lower = 0.0 if k == 0 else _beta_inv(alpha / 2.0, k, n - k + 1)
    upper = 1.0 if k == n else _beta_inv(1.0 - alpha / 2.0, k + 1, n - k)
    return lower, upper


def main():
    ap = argparse.ArgumentParser(description="Clopper-Pearson exact binomial CI")
    ap.add_argument("k", type=int, help="successes")
    ap.add_argument("n", type=int, help="trials")
    ap.add_argument("--alpha", type=float, default=0.05, help="default 0.05 -> 95%% CI")
    a = ap.parse_args()

    lo, hi = clopper_pearson(a.k, a.n, a.alpha)
    pct = 100.0 * (1.0 - a.alpha)
    point = a.k / a.n
    print(f"\n  {a.k}/{a.n} = {point:.1%}   {pct:.0f}% Clopper-Pearson CI: "
          f"[{lo:.1%}, {hi:.1%}]\n")


if __name__ == "__main__":
    main()
