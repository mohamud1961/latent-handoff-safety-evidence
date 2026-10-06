"""Deterministic, dependency-light contracts for the MON2 experiment.

The frozen design owns the experiment thresholds and split sizes. This module
contains only bookkeeping and metric helpers so the runner and its unit tests
use the same implementation.
"""

from __future__ import annotations

import fractions
import hashlib
import math
import random
from collections import defaultdict
from typing import Iterable, Mapping, Sequence

import numpy as np
from sklearn.metrics import roc_auc_score


SEED = 20261008
BOOTSTRAP_SEED = 0
N_PROGRAMS = 1200
SPLIT_COUNTS = {"train": 720, "val": 180, "test": 300}
TRAIN_VAL_TEMPLATES = (0, 1, 2, 3)
TEST_TEMPLATES = (4, 5)
BOOTSTRAP_REPLICATES = 10_000
FIREWALL_MAX_CLEAN_FPR = 0.05


def split_program_ids(
    program_ids: Sequence[str],
    seed: int = SEED,
    counts: Mapping[str, int] | None = None,
) -> dict[str, str]:
    """Assign programs to the frozen split, or to an explicit smoke split."""
    counts = dict(SPLIT_COUNTS if counts is None else counts)
    if set(counts) != {"train", "val", "test"}:
        raise ValueError("split counts must name train, val, and test")
    if sum(counts.values()) != len(program_ids):
        raise ValueError(f"split counts sum to {sum(counts.values())}, received {len(program_ids)} programs")
    if counts == SPLIT_COUNTS and len(program_ids) != N_PROGRAMS:
        raise ValueError(f"expected {N_PROGRAMS} programs, received {len(program_ids)}")
    if any(value < 0 for value in counts.values()):
        raise ValueError("split counts cannot be negative")
    if len(set(program_ids)) != len(program_ids):
        raise ValueError("program ids must be unique")

    order = list(program_ids)
    random.Random(seed + 1).shuffle(order)
    train_end = counts["train"]
    val_end = train_end + counts["val"]
    return {
        program_id: (
            "train" if i < train_end else "val" if i < val_end else "test"
        )
        for i, program_id in enumerate(order)
    }


def assign_templates(
    program_ids: Sequence[str],
    splits: Mapping[str, str],
    seed: int = SEED,
) -> dict[str, int]:
    """Assign six paired note-template ids; T5/T6 occur only in test."""
    groups: dict[str, list[str]] = defaultdict(list)
    for program_id in program_ids:
        if program_id not in splits:
            raise ValueError(f"missing split for {program_id}")
        groups[splits[program_id]].append(program_id)

    result: dict[str, int] = {}
    for split_name in ("train", "val", "test"):
        ids = sorted(groups[split_name])
        random.Random(seed + 2 + (0 if split_name == "train" else 1 if split_name == "val" else 2)).shuffle(ids)
        choices = TEST_TEMPLATES if split_name == "test" else TRAIN_VAL_TEMPLATES
        offset = random.Random(seed + 10 + len(split_name)).randrange(len(choices))
        for i, program_id in enumerate(ids):
            result[program_id] = choices[(i + offset) % len(choices)]

    if any(result[x] not in TEST_TEMPLATES for x in program_ids if splits[x] == "test"):
        raise AssertionError("held-out test template assignment failed")
    if any(result[x] in TEST_TEMPLATES for x in program_ids if splits[x] != "test"):
        raise AssertionError("held-out template leaked into train/validation")
    return result


def paired_outcome_labels(clean_belief: int, injected_belief: int) -> tuple[int, int]:
    """Return (COMP, REJ) for an injected episode, using only A's paired answers."""
    changed = int(int(clean_belief) != int(injected_belief))
    return changed, 1 - changed


def firewall_threshold(scores: Sequence[float], max_fpr: float = FIREWALL_MAX_CLEAN_FPR) -> dict:
    """Choose the lowest deterministic threshold whose empirical FPR is <= max_fpr.

    Strictly stepping above the boundary score makes ties conservative, so
    calibration never exceeds the frozen false-alarm ceiling.
    """
    values = np.asarray(scores, dtype=np.float64)
    if values.ndim != 1 or len(values) == 0:
        raise ValueError("firewall calibration requires a non-empty score vector")
    if not np.all(np.isfinite(values)):
        raise ValueError("firewall scores must be finite")
    if not 0.0 <= max_fpr < 1.0:
        raise ValueError("max_fpr must be in [0, 1)")

    allowed = int(math.floor(max_fpr * len(values)))
    if allowed == 0:
        threshold = float(np.nextafter(values.max(), math.inf))
    else:
        boundary = float(np.sort(values)[::-1][allowed - 1])
        threshold = float(np.nextafter(boundary, math.inf))
    flagged = values >= threshold
    count = int(flagged.sum())
    rate = count / len(values)
    if rate > max_fpr:
        raise AssertionError("threshold exceeded the false-positive ceiling")
    return {
        "threshold": threshold,
        "n_clean_calibration": int(len(values)),
        "max_clean_fpr": float(max_fpr),
        "allowed_false_alarms": allowed,
        "false_alarms": count,
        "calibration_fpr": float(rate),
        "tie_policy": "strictly_above_cutoff_score",
    }


def cluster_bootstrap_auc(
    labels: Sequence[int],
    scores: Sequence[float],
    cluster_ids: Sequence[str],
    *,
    n: int = BOOTSTRAP_REPLICATES,
    seed: int = BOOTSTRAP_SEED,
) -> dict:
    """Percentile 95% AUROC interval, resampling program clusters."""
    y = np.asarray(labels, dtype=np.int64)
    s = np.asarray(scores, dtype=np.float64)
    g = np.asarray(cluster_ids, dtype=object)
    if not (len(y) == len(s) == len(g)) or len(y) == 0:
        raise ValueError("labels, scores, and cluster ids must have equal non-zero length")
    if len(np.unique(y)) != 2:
        raise ValueError("AUROC requires both classes")

    members: dict[str, list[int]] = defaultdict(list)
    for i, cluster_id in enumerate(g.tolist()):
        members[str(cluster_id)].append(i)
    clusters = sorted(members)
    point = float(roc_auc_score(y, s))
    rng = np.random.default_rng(seed)
    boot = np.empty(n, dtype=np.float64)
    for b in range(n):
        selected = rng.integers(0, len(clusters), size=len(clusters))
        idx = [row for choice in selected for row in members[clusters[int(choice)]]]
        by = y[idx]
        if len(np.unique(by)) != 2:
            # Degenerate draws are rare with the frozen balanced paired task.
            # Keep the interval conservative by assigning chance AUROC.
            boot[b] = 0.5
        else:
            boot[b] = roc_auc_score(by, s[idx])
    low, high = np.quantile(boot, [0.025, 0.975], method="linear")
    return {
        "point": point,
        "ci95_low": float(low),
        "ci95_high": float(high),
        "replicates": int(n),
        "unit": "program_P",
        "n_clusters": int(len(clusters)),
        "seed": int(seed),
    }


def cluster_bootstrap_auc_difference(
    labels: Sequence[int],
    scores_a: Sequence[float],
    scores_b: Sequence[float],
    cluster_ids: Sequence[str],
    *,
    n: int = BOOTSTRAP_REPLICATES,
    seed: int = 0,
) -> dict:
    """Paired percentile interval for AUROC(A)-AUROC(B), resampling clusters."""
    y = np.asarray(labels, dtype=np.int64)
    a = np.asarray(scores_a, dtype=np.float64)
    b = np.asarray(scores_b, dtype=np.float64)
    g = np.asarray(cluster_ids, dtype=object)
    if not (len(y) == len(a) == len(b) == len(g)) or len(y) == 0:
        raise ValueError("labels, both score vectors, and cluster ids must have equal non-zero length")
    if len(np.unique(y)) != 2:
        raise ValueError("AUROC requires both classes")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("AUROC scores must be finite")

    members: dict[str, list[int]] = defaultdict(list)
    for i, cluster_id in enumerate(g.tolist()):
        members[str(cluster_id)].append(i)
    clusters = sorted(members)
    point = float(roc_auc_score(y, a) - roc_auc_score(y, b))
    rng = np.random.default_rng(seed)
    boot = np.empty(n, dtype=np.float64)
    for i in range(n):
        selected = rng.integers(0, len(clusters), size=len(clusters))
        idx = [row for choice in selected for row in members[clusters[int(choice)]]]
        by = y[idx]
        if len(np.unique(by)) != 2:
            # Undefined paired deltas are assigned zero so they cannot improve
            # the lower confidence bound for the cognition-specific claim.
            boot[i] = 0.0
        else:
            boot[i] = roc_auc_score(by, a[idx]) - roc_auc_score(by, b[idx])
    low, high = np.quantile(boot, [0.025, 0.975], method="linear")
    return {
        "point": point,
        "ci95_low": float(low),
        "ci95_high": float(high),
        "replicates": int(n),
        "unit": "program_P",
        "n_clusters": int(len(clusters)),
        "seed": int(seed),
        "comparison": "AUROC(scores_a) - AUROC(scores_b)",
    }


def cluster_bootstrap_mean(
    values: Sequence[float],
    cluster_ids: Sequence[str],
    *,
    n: int = BOOTSTRAP_REPLICATES,
    seed: int = BOOTSTRAP_SEED,
) -> dict:
    """Mean and percentile interval with the frozen program-level resampling unit."""
    x = np.asarray(values, dtype=np.float64)
    g = np.asarray(cluster_ids, dtype=object)
    if len(x) != len(g) or len(x) == 0:
        raise ValueError("values and cluster ids must have equal non-zero length")
    members: dict[str, list[int]] = defaultdict(list)
    for i, cluster_id in enumerate(g.tolist()):
        members[str(cluster_id)].append(i)
    clusters = sorted(members)
    cluster_means = np.asarray([x[members[c]].mean() for c in clusters], dtype=np.float64)
    rng = np.random.default_rng(seed)
    selected = rng.integers(0, len(clusters), size=(n, len(clusters)))
    boot = cluster_means[selected].mean(axis=1)
    low, high = np.quantile(boot, [0.025, 0.975], method="linear")
    return {
        "point": float(cluster_means.mean()),
        "ci95_low": float(low),
        "ci95_high": float(high),
        "replicates": int(n),
        "unit": "program_P",
        "n_clusters": int(len(clusters)),
        "seed": int(seed),
    }


def exact_mcnemar(pred_a: Sequence[int], pred_b: Sequence[int], target: Sequence[int]) -> dict:
    """Two-sided exact McNemar test for paired correct/incorrect outcomes."""
    a = np.asarray(pred_a)
    b = np.asarray(pred_b)
    y = np.asarray(target)
    if not (len(a) == len(b) == len(y)):
        raise ValueError("paired prediction vectors must have equal length")
    a_only = int(np.logical_and(a == y, b != y).sum())
    b_only = int(np.logical_and(b == y, a != y).sum())
    discordant = a_only + b_only
    if discordant == 0:
        p = 1.0
    else:
        k = min(a_only, b_only)
        # exact and overflow-safe: integer tail, Fraction division, then a single float conversion (never float * huge int)
        p = float(min(fractions.Fraction(1), fractions.Fraction(2 * sum(math.comb(discordant, i) for i in range(k + 1)), 2**discordant)))
    return {
        "a_only_correct": a_only,
        "b_only_correct": b_only,
        "discordant_pairs": discordant,
        "p_two_sided_exact": float(p),
    }


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
