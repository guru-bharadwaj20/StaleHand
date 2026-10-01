//! Paired statistics over StaleHand result JSONL: exact McNemar and a template-clustered bootstrap. The output
//! must equal `stalehand.metrics.stats.compare` on the same rows, so the bootstrap reuses Python's generator.
pub mod mt;
pub mod rows;
pub mod stats;
