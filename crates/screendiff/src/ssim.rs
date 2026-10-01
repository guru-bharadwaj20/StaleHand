//! Mean structural similarity (SSIM) over all 7x7 windows, computed with integral images so a full
//! 1288x728 screenshot takes a few milliseconds. Constants follow Wang et al. (2004) for 8-bit data.
use crate::diff::SizeMismatch;
use crate::gray::Gray;

pub const WIN: usize = 7;
const C1: f64 = (0.01 * 255.0) * (0.01 * 255.0);
const C2: f64 = (0.03 * 255.0) * (0.03 * 255.0);

/// Summed-area table with one row and column of zero padding.
struct Integral {
    w: usize,
    s: Vec<f64>,
}

impl Integral {
    fn new(width: usize, height: usize, f: impl Fn(usize) -> f64) -> Self {
        let w = width + 1;
        let mut s = vec![0.0; w * (height + 1)];
        for y in 0..height {
            let mut row = 0.0;
            for x in 0..width {
                row += f(y * width + x);
                s[(y + 1) * w + x + 1] = s[y * w + x + 1] + row;
            }
        }
        Integral { w, s }
    }

    fn window(&self, x: usize, y: usize, n: usize) -> f64 {
        let w = self.w;
        self.s[(y + n) * w + x + n] - self.s[y * w + x + n] - self.s[(y + n) * w + x]
            + self.s[y * w + x]
    }
}

/// SSIM of one window from its sums.
fn window_ssim(n: f64, sa: f64, sb: f64, saa: f64, sbb: f64, sab: f64) -> f64 {
    let (ma, mb) = (sa / n, sb / n);
    let va = (saa - n * ma * ma) / (n - 1.0);
    let vb = (sbb - n * mb * mb) / (n - 1.0);
    let cov = (sab - n * ma * mb) / (n - 1.0);
    ((2.0 * ma * mb + C1) * (2.0 * cov + C2)) / ((ma * ma + mb * mb + C1) * (va + vb + C2))
}

/// Mean SSIM; images smaller than one window are compared as a single window.
pub fn ssim(a: &Gray, b: &Gray) -> Result<f64, SizeMismatch> {
    if a.width != b.width || a.height != b.height {
        return Err(SizeMismatch);
    }
    let (w, h) = (a.width, a.height);
    if w == 0 || h == 0 {
        return Ok(1.0);
    }
    let n = WIN.min(w).min(h);
    let ia = Integral::new(w, h, |i| a.px[i] as f64);
    let ib = Integral::new(w, h, |i| b.px[i] as f64);
    let iaa = Integral::new(w, h, |i| (a.px[i] as f64).powi(2));
    let ibb = Integral::new(w, h, |i| (b.px[i] as f64).powi(2));
    let iab = Integral::new(w, h, |i| a.px[i] as f64 * b.px[i] as f64);
    let nn = (n * n) as f64;
    let mut total = 0.0;
    let mut count = 0usize;
    for y in 0..=h - n {
        for x in 0..=w - n {
            total += window_ssim(
                nn,
                ia.window(x, y, n),
                ib.window(x, y, n),
                iaa.window(x, y, n),
                ibb.window(x, y, n),
                iab.window(x, y, n),
            );
            count += 1;
        }
    }
    Ok(total / count as f64)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn noise(w: usize, h: usize, seed: u64) -> Gray {
        let mut s = seed;
        let px = (0..w * h)
            .map(|_| {
                s = s
                    .wrapping_mul(6364136223846793005)
                    .wrapping_add(1442695040888963407);
                ((s >> 33) % 256) as f32
            })
            .collect();
        Gray::new(w, h, px)
    }

    /// Direct, slow SSIM to check the integral-image version against.
    fn naive(a: &Gray, b: &Gray) -> f64 {
        let n = WIN;
        let mut total = 0.0;
        let mut count = 0;
        for y in 0..=a.height - n {
            for x in 0..=a.width - n {
                let (mut sa, mut sb, mut saa, mut sbb, mut sab) = (0.0, 0.0, 0.0, 0.0, 0.0);
                for dy in 0..n {
                    for dx in 0..n {
                        let (p, q) = (a.at(x + dx, y + dy) as f64, b.at(x + dx, y + dy) as f64);
                        sa += p;
                        sb += q;
                        saa += p * p;
                        sbb += q * q;
                        sab += p * q;
                    }
                }
                total += window_ssim((n * n) as f64, sa, sb, saa, sbb, sab);
                count += 1;
            }
        }
        total / count as f64
    }

    #[test]
    fn identical_images_score_one() {
        let a = noise(32, 20, 1);
        assert!((ssim(&a, &a).unwrap() - 1.0).abs() < 1e-9);
    }

    #[test]
    fn matches_naive_computation() {
        let (a, b) = (noise(40, 25, 1), noise(40, 25, 2));
        assert!((ssim(&a, &b).unwrap() - naive(&a, &b)).abs() < 1e-9);
    }

    #[test]
    fn small_edit_scores_higher_than_large_edit() {
        let a = noise(40, 40, 3);
        let mut small = a.clone();
        let mut large = a.clone();
        for i in 0..40 {
            small.px[i] = 0.0;
        }
        for i in 0..800 {
            large.px[i] = 0.0;
        }
        let (s, l) = (ssim(&a, &small).unwrap(), ssim(&a, &large).unwrap());
        assert!(s > l && s < 1.0, "small {s} large {l}");
    }

    #[test]
    fn size_mismatch_is_an_error() {
        assert!(ssim(&noise(8, 8, 1), &noise(9, 8, 1)).is_err());
    }
}
