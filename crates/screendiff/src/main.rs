//! screendiff BEFORE.png AFTER.png [--region x,y,w,h] [--threshold T]
//! Prints one JSON report to stdout; exits 2 on bad arguments or unreadable images.
use screendiff::gray::Region;
use screendiff::load::load_gray;
use screendiff::report::compare;
use std::path::PathBuf;
use std::process::ExitCode;

fn parse_region(s: &str) -> Result<Region, String> {
    let v: Vec<usize> = s.split(',').map(|p| p.trim().parse::<usize>()).collect::<Result<_, _>>()
        .map_err(|e| format!("bad --region {s}: {e}"))?;
    match v[..] {
        [x, y, w, h] => Ok(Region { x, y, w, h }),
        _ => Err(format!("--region needs x,y,w,h, got {s}")),
    }
}

fn run(args: Vec<String>) -> Result<String, String> {
    let mut paths = Vec::new();
    let (mut region, mut threshold) = (None, 8.0f32);
    let mut it = args.into_iter();
    while let Some(a) = it.next() {
        match a.as_str() {
            "--region" => region = Some(parse_region(&it.next().ok_or("--region needs a value")?)?),
            "--threshold" => threshold = it.next().ok_or("--threshold needs a value")?.parse()
                .map_err(|e| format!("bad --threshold: {e}"))?,
            _ => paths.push(PathBuf::from(a)),
        }
    }
    let [before, after] = <[PathBuf; 2]>::try_from(paths).map_err(|_| "need exactly two images".to_string())?;
    let a = load_gray(&before).map_err(|e| format!("{}: {e}", before.display()))?;
    let b = load_gray(&after).map_err(|e| format!("{}: {e}", after.display()))?;
    let report = compare(&a, &b, region, threshold).map_err(|_| "images differ in size".to_string())?;
    serde_json::to_string(&report).map_err(|e| e.to_string())
}

fn main() -> ExitCode {
    match run(std::env::args().skip(1).collect()) {
        Ok(json) => {
            println!("{json}");
            ExitCode::SUCCESS
        }
        Err(e) => {
            eprintln!("screendiff: {e}");
            ExitCode::from(2)
        }
    }
}
