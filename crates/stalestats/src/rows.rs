//! Read result JSONL rows. Only the fields the statistics need are kept; other fields are ignored.
use serde::Deserialize;
use std::path::Path;

#[derive(Debug, Clone, Deserialize)]
pub struct Row {
    pub scenario_id: String,
    pub guard: String,
    pub outcome: String,
}

impl Row {
    pub fn success(&self) -> bool {
        self.outcome == "success"
    }
}

pub fn parse_jsonl(text: &str) -> Result<Vec<Row>, String> {
    text.lines()
        .enumerate()
        .filter(|(_, l)| !l.trim().is_empty())
        .map(|(i, l)| serde_json::from_str(l).map_err(|e| format!("line {}: {e}", i + 1)))
        .collect()
}

pub fn read_jsonl(path: &Path) -> Result<Vec<Row>, String> {
    let text = std::fs::read_to_string(path).map_err(|e| format!("{}: {e}", path.display()))?;
    parse_jsonl(&text).map_err(|e| format!("{}: {e}", path.display()))
}

/// The rows of one arm, picked by guard name.
pub fn arm(rows: &[Row], guard: &str) -> Vec<Row> {
    rows.iter().filter(|r| r.guard == guard).cloned().collect()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn skips_blank_lines_and_extra_fields() {
        let rows = parse_jsonl(
            "{\"scenario_id\":\"a-L1\",\"guard\":\"none\",\"outcome\":\"stale\",\"fired\":0}\n\n",
        )
        .unwrap();
        assert_eq!(rows.len(), 1);
        assert!(!rows[0].success());
    }

    #[test]
    fn reports_the_bad_line() {
        let err =
            parse_jsonl("{\"scenario_id\":\"a\",\"guard\":\"g\",\"outcome\":\"success\"}\n{oops")
                .unwrap_err();
        assert!(err.starts_with("line 2"), "{err}");
    }
}
