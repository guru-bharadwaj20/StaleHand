//! The Mersenne Twister exactly as CPython's `random.Random(seed)` seeds and uses it, so a bootstrap with the
//! same seed draws the same clusters in both languages.
const N: usize = 624;
const M: usize = 397;

pub struct PyRandom {
    state: [u32; N],
    index: usize,
}

impl PyRandom {
    /// `random.Random(seed)` for a non-negative integer seed.
    pub fn new(seed: u64) -> Self {
        let mut key = vec![seed as u32];
        if seed >> 32 != 0 {
            key.push((seed >> 32) as u32);
        }
        let mut r = PyRandom {
            state: [0; N],
            index: N,
        };
        r.init_by_array(&key);
        r
    }

    fn init_genrand(&mut self, s: u32) {
        self.state[0] = s;
        for i in 1..N {
            let prev = self.state[i - 1];
            self.state[i] = 1_812_433_253u32
                .wrapping_mul(prev ^ (prev >> 30))
                .wrapping_add(i as u32);
        }
        self.index = N;
    }

    fn init_by_array(&mut self, key: &[u32]) {
        self.init_genrand(19_650_218);
        let (mut i, mut j) = (1usize, 0usize);
        for _ in 0..N.max(key.len()) {
            let prev = self.state[i - 1];
            self.state[i] = (self.state[i] ^ (prev ^ (prev >> 30)).wrapping_mul(1_664_525))
                .wrapping_add(key[j])
                .wrapping_add(j as u32);
            i += 1;
            j += 1;
            if i >= N {
                self.state[0] = self.state[N - 1];
                i = 1;
            }
            if j >= key.len() {
                j = 0;
            }
        }
        for _ in 0..N - 1 {
            let prev = self.state[i - 1];
            self.state[i] = (self.state[i] ^ (prev ^ (prev >> 30)).wrapping_mul(1_566_083_941))
                .wrapping_sub(i as u32);
            i += 1;
            if i >= N {
                self.state[0] = self.state[N - 1];
                i = 1;
            }
        }
        self.state[0] = 0x8000_0000;
    }

    fn twist(&mut self) {
        for k in 0..N {
            let y = (self.state[k] & 0x8000_0000) | (self.state[(k + 1) % N] & 0x7fff_ffff);
            let mut v = self.state[(k + M) % N] ^ (y >> 1);
            if y & 1 != 0 {
                v ^= 0x9908_b0df;
            }
            self.state[k] = v;
        }
        self.index = 0;
    }

    pub fn next_u32(&mut self) -> u32 {
        if self.index >= N {
            self.twist();
        }
        let mut y = self.state[self.index];
        self.index += 1;
        y ^= y >> 11;
        y ^= (y << 7) & 0x9d2c_5680;
        y ^= (y << 15) & 0xefc6_0000;
        y ^ (y >> 18)
    }

    /// `randrange(n)` for 0 < n < 2**32: rejection sampling on the bit length, as CPython does.
    pub fn randbelow(&mut self, n: u32) -> u32 {
        assert!(n > 0, "randbelow needs n > 0");
        let k = 32 - n.leading_zeros();
        loop {
            let r = self.next_u32() >> (32 - k);
            if r < n {
                return r;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn matches_cpython_getrandbits() {
        // python: r = random.Random(0); [r.getrandbits(32) for _ in range(3)]
        let mut r = PyRandom::new(0);
        assert_eq!(
            [r.next_u32(), r.next_u32(), r.next_u32()],
            [3_626_764_237, 1_654_615_998, 3_255_389_356]
        );
    }

    #[test]
    fn matches_cpython_randrange() {
        // python: r = random.Random(42); [r.randrange(30) for _ in range(5)]
        let mut r = PyRandom::new(42);
        let got: Vec<u32> = (0..5).map(|_| r.randbelow(30)).collect();
        assert_eq!(got, vec![20, 3, 0, 23, 8]);
    }
}
