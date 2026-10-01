//! stalestats RESULTS.jsonl GUARD_A GUARD_B [--n-boot N] [--seed S]
//! Compares two guards on the scenarios both ran and prints one JSON object (the same fields as the Python
//! `stats.compare`); exits 2 on bad arguments or unreadable input.
use stalestats::rows::{arm, read_jsonl};
use stalestats::stats::compare;
use std::path::PathBuf;
use std::process::ExitCode;

fn run(args: Vec<String>) -> Result<String, String> {
    let mut positional = Vec::new();
    let (mut n_boot, mut seed) = (10_000usize, 0u64);
    let mut it = args.into_iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--n-boot" => {
                n_boot = it
                    .next()
                    .ok_or("--n-boot needs a value")?
                    .parse()
                    .map_err(|e| format!("bad --n-boot: {e}"))?
            }
            "--seed" => {
                seed = it
                    .next()
                    .ok_or("--seed needs a value")?
                    .parse()
                    .map_err(|e| format!("bad --seed: {e}"))?
            }
            _ => positional.push(a),
        }
    }
    let [path, guard_a, guard_b] = <[String; 3]>::try_from(positional).map_err(|_| {
        "usage: stalestats RESULTS.jsonl GUARD_A GUARD_B [--n-boot N] [--seed S]".to_string()
    })?;
    if n_boot == 0 {
        return Err("--n-boot must be positive".into());
    }
    let rows = read_jsonl(&PathBuf::from(path))?;
    let result = compare(&arm(&rows, &guard_a), &arm(&rows, &guard_b), n_boot, seed)?;
    serde_json::to_string(&result).map_err(|e| e.to_string())
}

fn main() -> ExitCode {
    match run(std::env::args().skip(1).collect()) {
        Ok(json) => {
            println!("{json}");
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("stalestats: {e}");
            ExitCode::from(2)
        }
    }
}
