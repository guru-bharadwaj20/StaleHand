//! Grayscale image buffer and region cropping.

#[derive(Debug, Clone, PartialEq)]
pub struct Gray {
    pub width: usize,
    pub height: usize,
    pub px: Vec<f32>,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct Region {
    pub x: usize,
    pub y: usize,
    pub w: usize,
    pub h: usize,
}

impl Gray {
    pub fn new(width: usize, height: usize, px: Vec<f32>) -> Self {
        assert_eq!(px.len(), width * height, "pixel count must equal width * height");
        Gray { width, height, px }
    }

    /// ITU-R BT.601 luma from 8-bit RGB.
    pub fn from_rgb(width: usize, height: usize, rgb: &[u8]) -> Self {
        let px = rgb
            .chunks_exact(3)
            .map(|p| 0.299 * p[0] as f32 + 0.587 * p[1] as f32 + 0.114 * p[2] as f32)
            .collect();
        Gray::new(width, height, px)
    }

    pub fn at(&self, x: usize, y: usize) -> f32 {
        self.px[y * self.width + x]
    }

    /// The part of `r` inside the image; an empty region gives a 0x0 image.
    pub fn crop(&self, r: Region) -> Gray {
        let x1 = (r.x + r.w).min(self.width);
        let y1 = (r.y + r.h).min(self.height);
        let (x0, y0) = (r.x.min(x1), r.y.min(y1));
        let mut px = Vec::with_capacity((x1 - x0) * (y1 - y0));
        for y in y0..y1 {
            px.extend_from_slice(&self.px[y * self.width + x0..y * self.width + x1]);
        }
        Gray::new(x1 - x0, y1 - y0, px)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn ramp(w: usize, h: usize) -> Gray {
        Gray::new(w, h, (0..w * h).map(|i| i as f32).collect())
    }

    #[test]
    fn luma_of_white_is_255() {
        let g = Gray::from_rgb(1, 1, &[255, 255, 255]);
        assert!((g.px[0] - 255.0).abs() < 1e-3);
    }

    #[test]
    fn crop_takes_the_region() {
        let c = ramp(4, 3).crop(Region { x: 1, y: 1, w: 2, h: 2 });
        assert_eq!((c.width, c.height), (2, 2));
        assert_eq!(c.px, vec![5.0, 6.0, 9.0, 10.0]);
    }

    #[test]
    fn crop_is_clipped_to_the_image() {
        let c = ramp(4, 3).crop(Region { x: 3, y: 2, w: 10, h: 10 });
        assert_eq!((c.width, c.height), (1, 1));
        assert_eq!(c.px, vec![11.0]);
    }

    #[test]
    fn crop_outside_is_empty() {
        let c = ramp(4, 3).crop(Region { x: 9, y: 9, w: 2, h: 2 });
        assert_eq!((c.width, c.height), (0, 0));
    }
}
