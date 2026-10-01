//! Simple pixel statistics between two screenshots of the same size.
use crate::gray::Gray;

#[derive(Debug, PartialEq)]
pub struct SizeMismatch;

fn check(a: &Gray, b: &Gray) -> Result<(), SizeMismatch> {
    if a.width == b.width && a.height == b.height { Ok(()) } else { Err(SizeMismatch) }
}

/// Mean absolute difference in luma, 0 for identical images; 0 for empty images.
pub fn mean_abs_diff(a: &Gray, b: &Gray) -> Result<f64, SizeMismatch> {
    check(a, b)?;
    if a.px.is_empty() {
        return Ok(0.0);
    }
    let sum: f64 = a.px.iter().zip(&b.px).map(|(x, y)| (x - y).abs() as f64).sum();
    Ok(sum / a.px.len() as f64)
}

/// Fraction of pixels whose luma moved by more than `threshold`.
pub fn changed_fraction(a: &Gray, b: &Gray, threshold: f32) -> Result<f64, SizeMismatch> {
    check(a, b)?;
    if a.px.is_empty() {
        return Ok(0.0);
    }
    let n = a.px.iter().zip(&b.px).filter(|(x, y)| (*x - *y).abs() > threshold).count();
    Ok(n as f64 / a.px.len() as f64)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn flat(v: f32, n: usize) -> Gray {
        Gray::new(n, 1, vec![v; n])
    }

    #[test]
    fn identical_images_have_zero_diff() {
        assert_eq!(mean_abs_diff(&flat(9.0, 4), &flat(9.0, 4)), Ok(0.0));
        assert_eq!(changed_fraction(&flat(9.0, 4), &flat(9.0, 4), 0.0), Ok(0.0));
    }

    #[test]
    fn mean_abs_diff_averages() {
        let a = Gray::new(2, 1, vec![0.0, 10.0]);
        let b = Gray::new(2, 1, vec![4.0, 4.0]);
        assert_eq!(mean_abs_diff(&a, &b), Ok(5.0));
    }

    #[test]
    fn changed_fraction_respects_threshold() {
        let a = Gray::new(4, 1, vec![0.0, 0.0, 0.0, 0.0]);
        let b = Gray::new(4, 1, vec![1.0, 5.0, 20.0, 0.0]);
        assert_eq!(changed_fraction(&a, &b, 2.0), Ok(0.5));
    }

    #[test]
    fn size_mismatch_is_an_error() {
        assert_eq!(mean_abs_diff(&flat(0.0, 2), &flat(0.0, 3)), Err(SizeMismatch));
    }
}
