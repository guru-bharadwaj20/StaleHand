//! One comparison of two screenshots, optionally restricted to a region, as a serialisable report.
use crate::diff::{SizeMismatch, changed_fraction, mean_abs_diff};
use crate::gray::{Gray, Region};
use crate::ssim::ssim;
use serde::Serialize;

#[derive(Debug, Serialize, PartialEq)]
pub struct Report {
    pub width: usize,
    pub height: usize,
    pub region: Option<[usize; 4]>,
    pub threshold: f32,
    pub ssim: f64,
    pub mean_abs_diff: f64,
    pub changed_fraction: f64,
}

pub fn compare(
    a: &Gray,
    b: &Gray,
    region: Option<Region>,
    threshold: f32,
) -> Result<Report, SizeMismatch> {
    if a.width != b.width || a.height != b.height {
        return Err(SizeMismatch);
    }
    let (ca, cb) = match region {
        Some(r) => (a.crop(r), b.crop(r)),
        None => (a.clone(), b.clone()),
    };
    Ok(Report {
        width: a.width,
        height: a.height,
        region: region.map(|r| [r.x, r.y, r.w, r.h]),
        threshold,
        ssim: ssim(&ca, &cb)?,
        mean_abs_diff: mean_abs_diff(&ca, &cb)?,
        changed_fraction: changed_fraction(&ca, &cb, threshold)?,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn region_ignores_changes_elsewhere() {
        let a = Gray::new(20, 20, vec![100.0; 400]);
        let mut b = a.clone();
        for i in 0..20 {
            b.px[i] = 0.0;
        } // top row changes
        let r = compare(
            &a,
            &b,
            Some(Region {
                x: 0,
                y: 10,
                w: 20,
                h: 10,
            }),
            8.0,
        )
        .unwrap();
        assert_eq!(r.changed_fraction, 0.0);
        assert!((r.ssim - 1.0).abs() < 1e-9);
        let full = compare(&a, &b, None, 8.0).unwrap();
        assert!((full.changed_fraction - 0.05).abs() < 1e-12);
    }

    #[test]
    fn report_serialises_to_json() {
        let a = Gray::new(8, 8, vec![1.0; 64]);
        let json = serde_json::to_string(&compare(&a, &a, None, 8.0).unwrap()).unwrap();
        assert!(json.contains("\"ssim\":1.0") && json.contains("\"region\":null"));
    }
}
