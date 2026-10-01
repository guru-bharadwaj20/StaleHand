//! Port of `stalehand/metrics/stats.py`. Keep the two in step: the shared fixture test checks they agree.
use crate::mt::PyRandom;
use crate::rows::Row;
use serde::Serialize;
use std::collections::{BTreeMap, BTreeSet};

fn ln_factorial(n: u64) -> f64 {
    (2..=n).map(|i| (i as f64).ln()).sum()
}

/// Two-sided exact McNemar test: binomial test of the discordant pairs (b, c) against p = 0.5.
pub fn mcnemar_exact(b: u64, c: u64) -> f64 {
    let n = b + c;
    if n == 0 {
        return 1.0;
    }
    let k = b.min(c);
    let ln_n = ln_factorial(n);
    // log-space sum keeps large n finite
    let logs: Vec<f64> = (0..=k)
        .map(|i| ln_n - ln_factorial(i) - ln_factorial(n - i) - n as f64 * 2f64.ln())
        .collect();
    let top = logs.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let tail = top.exp() * logs.iter().map(|v| (v - top).exp()).sum::<f64>();
    (2.0 * tail).min(1.0)
}

/// Scenarios built from the same first screen share a template: the id without its variant suffix.
pub fn template_of(scenario_id: &str) -> &str {
    scenario_id.rsplit_once('-').map_or(scenario_id, |(t, _)| t)
}

/// One scenario both arms ran: (id, a succeeded, b succeeded).
pub type Pair = (String, bool, bool);

/// Match two arms by scenario id, sorted by id; also count ids only one arm has.
pub fn pair(a: &[Row], b: &[Row]) -> Result<(Vec<Pair>, usize, usize), String> {
    fn index(rows: &[Row]) -> Result<BTreeMap<&str, &Row>, String> {
        let mut out = BTreeMap::new();
        for r in rows {
            if out.insert(r.scenario_id.as_str(), r).is_some() {
                return Err(format!(
                    "scenario {} appears twice in one arm",
                    r.scenario_id
                ));
            }
        }
        Ok(out)
    }
    let (ia, ib) = (index(a)?, index(b)?);
    let ka: BTreeSet<&str> = ia.keys().copied().collect();
    let kb: BTreeSet<&str> = ib.keys().copied().collect();
    let pairs = ka
        .intersection(&kb)
        .map(|k| (k.to_string(), ia[k].success(), ib[k].success()))
        .collect();
    Ok((
        pairs,
        ka.difference(&kb).count(),
        kb.difference(&ka).count(),
    ))
}

/// Percentile interval for stat(units), resampling whole clusters with replacement.
pub fn cluster_bootstrap<T: Clone>(
    units: &[T],
    stat: impl Fn(&[T]) -> f64,
    cluster_of: impl Fn(&T) -> String,
    n_boot: usize,
    seed: u64,
    alpha: f64,
) -> (f64, f64) {
    let mut clusters: BTreeMap<String, Vec<T>> = BTreeMap::new();
    for u in units {
        clusters.entry(cluster_of(u)).or_default().push(u.clone());
    }
    let groups: Vec<Vec<T>> = clusters.into_values().collect();
    let mut rng = PyRandom::new(seed);
    let mut values: Vec<f64> = (0..n_boot)
        .map(|_| {
            let mut sample = Vec::new();
            for _ in 0..groups.len() {
                sample.extend_from_slice(&groups[rng.randbelow(groups.len() as u32) as usize]);
            }
            stat(&sample)
        })
        .collect();
    values.sort_by(f64::total_cmp);
    let lo = values[(alpha / 2.0 * (n_boot - 1) as f64).floor() as usize];
    let hi = values[((1.0 - alpha / 2.0) * (n_boot - 1) as f64).ceil() as usize];
    (lo, hi)
}

#[derive(Debug, Serialize, PartialEq)]
pub struct Comparison {
    pub n: usize,
    pub only_a: usize,
    pub only_b: usize,
    pub a_rate: f64,
    pub b_rate: f64,
    pub diff: f64,
    pub diff_ci: [f64; 2],
    pub a_only: u64,
    pub b_only: u64,
    pub p: f64,
    pub n_boot: usize,
    pub seed: u64,
}

fn rate(pairs: &[Pair], arm: impl Fn(&Pair) -> bool) -> f64 {
    pairs.iter().filter(|p| arm(p)).count() as f64 / pairs.len() as f64
}

fn diff(pairs: &[Pair]) -> f64 {
    let a = pairs.iter().filter(|p| p.1).count() as i64;
    let b = pairs.iter().filter(|p| p.2).count() as i64;
    (a - b) as f64 / pairs.len() as f64
}

/// Paired comparison of two arms on the same scenarios (a minus b).
pub fn compare(a: &[Row], b: &[Row], n_boot: usize, seed: u64) -> Result<Comparison, String> {
    let (pairs, only_a, only_b) = pair(a, b)?;
    if pairs.is_empty() {
        return Err("the two arms share no scenarios".into());
    }
    let a_only = pairs.iter().filter(|p| p.1 && !p.2).count() as u64;
    let b_only = pairs.iter().filter(|p| p.2 && !p.1).count() as u64;
    let (lo, hi) = cluster_bootstrap(
        &pairs,
        diff,
        |p| template_of(&p.0).to_string(),
        n_boot,
        seed,
        0.05,
    );
    Ok(Comparison {
        n: pairs.len(),
        only_a,
        only_b,
        a_rate: rate(&pairs, |p| p.1),
        b_rate: rate(&pairs, |p| p.2),
        diff: diff(&pairs),
        diff_ci: [lo, hi],
        a_only,
        b_only,
        p: mcnemar_exact(a_only, b_only),
        n_boot,
        seed,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    fn row(id: &str, guard: &str, ok: bool) -> Row {
        Row {
            scenario_id: id.into(),
            guard: guard.into(),
            outcome: if ok { "success" } else { "stale" }.into(),
        }
    }

    #[test]
    fn mcnemar_known_values() {
        assert_eq!(mcnemar_exact(0, 0), 1.0);
        assert!((mcnemar_exact(0, 5) - 0.0625).abs() < 1e-12);
        assert!((mcnemar_exact(3, 3) - 1.0).abs() < 1e-12);
        assert!((mcnemar_exact(2, 10) - 0.038_574_218_75).abs() < 1e-12);
    }

    #[test]
    fn template_strips_the_variant() {
        assert_eq!(template_of("inbox-relative-003-L1"), "inbox-relative-003");
        assert_eq!(template_of("plain"), "plain");
    }

    #[test]
    fn pairs_by_id_and_counts_missing() {
        let a = [
            row("t-1-L0", "g", true),
            row("t-1-L1", "g", false),
            row("t-2-L0", "g", true),
        ];
        let b = [row("t-1-L0", "n", false), row("t-1-L1", "n", false)];
        let (pairs, only_a, only_b) = pair(&a, &b).unwrap();
        assert_eq!(
            pairs,
            vec![
                ("t-1-L0".into(), true, false),
                ("t-1-L1".into(), false, false)
            ]
        );
        assert_eq!((only_a, only_b), (1, 0));
    }

    #[test]
    fn duplicate_ids_are_rejected() {
        let a = [row("x-L0", "g", true), row("x-L0", "g", false)];
        assert!(pair(&a, &a).is_err());
    }

    #[test]
    fn disjoint_arms_are_rejected() {
        assert!(compare(&[row("a-L0", "g", true)], &[row("b-L0", "n", true)], 10, 0).is_err());
    }

    #[test]
    fn single_cluster_interval_is_a_point() {
        let units = vec![1.0, 2.0, 3.0];
        let mean = |u: &[f64]| u.iter().sum::<f64>() / u.len() as f64;
        assert_eq!(
            cluster_bootstrap(&units, mean, |_| "one".into(), 200, 0, 0.05),
            (2.0, 2.0)
        );
    }
}
