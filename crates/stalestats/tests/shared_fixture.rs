//! The Rust statistics must agree with the Python ones on the shared fixture (scripts/make_stats_fixture.py).
use serde_json::Value;
use stalestats::rows::{arm, read_jsonl};
use stalestats::stats::compare;
use std::path::PathBuf;

fn fixtures() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../schema/fixtures")
}

#[test]
fn matches_python_on_shared_fixture() {
    let rows = read_jsonl(&fixtures().join("results_pair.jsonl")).unwrap();
    let text = std::fs::read_to_string(fixtures().join("results_pair.expected.json")).unwrap();
    let want: Value = serde_json::from_str(&text).unwrap();
    let n_boot = want["n_boot"].as_u64().unwrap() as usize;
    let seed = want["seed"].as_u64().unwrap();
    let got = serde_json::to_value(
        compare(
            &arm(&rows, "rule_subtask"),
            &arm(&rows, "none"),
            n_boot,
            seed,
        )
        .unwrap(),
    )
    .unwrap();
    for (key, w) in want.as_object().unwrap() {
        let g = &got[key];
        match w {
            Value::Array(ws) => {
                for (wi, gi) in ws.iter().zip(g.as_array().unwrap()) {
                    assert!(
                        (wi.as_f64().unwrap() - gi.as_f64().unwrap()).abs() < 1e-12,
                        "{key}: {w} vs {g}"
                    );
                }
            }
            // p comes from lgamma in Python and summed logs here: equal to many digits, not bit for bit
            _ => assert!(
                (w.as_f64().unwrap() - g.as_f64().unwrap()).abs()
                    <= 1e-9 * w.as_f64().unwrap().abs().max(1e-300),
                "{key}: {w} vs {g}"
            ),
        }
    }
}
