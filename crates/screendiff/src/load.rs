//! Reading screenshots from disk.
use crate::gray::Gray;
use std::path::Path;

pub fn load_gray(path: &Path) -> Result<Gray, image::ImageError> {
    let img = image::open(path)?.to_rgb8();
    let (w, h) = img.dimensions();
    Ok(Gray::from_rgb(w as usize, h as usize, img.as_raw()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn loads_png_as_luma() {
        let dir = std::env::temp_dir().join("screendiff-load-test");
        std::fs::create_dir_all(&dir).unwrap();
        let path = dir.join("white.png");
        image::RgbImage::from_pixel(3, 2, image::Rgb([255, 255, 255]))
            .save(&path)
            .unwrap();
        let g = load_gray(&path).unwrap();
        assert_eq!((g.width, g.height), (3, 2));
        assert!(g.px.iter().all(|&p| (p - 255.0).abs() < 1e-3));
    }

    #[test]
    fn missing_file_is_an_error() {
        assert!(load_gray(Path::new("/nonexistent/screen.png")).is_err());
    }
}
