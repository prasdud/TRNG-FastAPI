# Hardware Random Number Generator Testing Documentation
## Complete Master Testing Guide

**Project**: True Hardware Random Number Generator (SDR + Video Data)  
**Output**: 9-digit decimal numbers (configurable length)  
**Date**: November 2025  
**Author**: Comprehensive Testing Framework

---

## Table of Contents

1. [Testing Philosophy](#testing-philosophy)
2. [Theoretical Foundations](#theoretical-foundations)
3. [Testing Hierarchy](#testing-hierarchy)
4. [Statistical Tests Explained](#statistical-tests-explained)
5. [Implementation Guide](#implementation-guide)
6. [Practical Testing Workflow](#practical-testing-workflow)
7. [Tool Reference](#tool-reference)
8. [Troubleshooting & Interpretation](#troubleshooting--interpretation)
9. [Quick Reference Checklist](#quick-reference-checklist)

---

## Testing Philosophy

### Fundamental Principles

**You cannot prove a sequence is random; you can only gather statistical evidence that no obvious non-random structure is detectable.**

The goal of randomness testing is:
- ✅ Detect systematic biases or patterns
- ✅ Verify uniform distribution across outputs
- ✅ Confirm independence between successive values
- ✅ Ensure complexity and high entropy
- ❌ NOT: Prove absolute randomness (impossible)

### Key Insight

For a true hardware RNG combining entropy sources (SDR + video):
- **Statistical test suites** measure output quality (are generated numbers random?)
- **Min-entropy estimation** validates entropy sources (is your hardware truly providing entropy?)

Both are equally important for cryptographic applications.

---

## Theoretical Foundations

### 1. Randomness Definitions

**Shannon Entropy (Theoretical Maximum)**
```
H = -∑(p_i × log₂(p_i))
```
- Perfect randomness: H = 1 bit per bit
- For 9-digit decimal: theoretical max ≈ 26.6 bits per output

**Min-Entropy (Practical Guarantee)**
```
H_min = -log₂(max(p_i))
```
- Worst-case entropy per bit
- Matters more for security than Shannon entropy
- NIST SP 800-90B focuses on this metric

**Bias Estimation**
```
Bias (ε) = |p_1 - 0.5|
```
- p_1 = probability of observing a 1 bit
- Perfect randomness: ε → 0
- Acceptable cryptographic threshold: ε < 0.01

### 2. Probability and Statistical Testing

**Null Hypothesis Framework**
- H₀: "The data is uniformly distributed and independent" (Random)
- H₁: "The data exhibits non-random structure" (Not Random)

**P-value Interpretation**
```
p-value < 0.01:   Strong evidence AGAINST randomness (FAIL)
p-value 0.01-0.99: Consistent with randomness (PASS)
p-value > 0.99:   Suspiciously uniform (possible weakness in test)
```

**Test Batches**
When running multiple tests on the same dataset:
- Expect approximately 5% of tests to fail by random chance (false positives)
- If >5-10% fail, investigate deeper
- If <1% fail, generator likely has no obvious defects

---

## Testing Hierarchy

### Level 1: Quick Sanity Checks (5-15 minutes)
**Purpose**: Catch obvious implementation errors

- Monobit frequency test (0s vs 1s count)
- Shannon entropy calculation
- Bias estimation
- Visual inspection (bitmap viewing)
- Compression test (gzip ratio)

**Pass Criteria**:
- 0 and 1 appear approximately equally
- Shannon H ≈ 1.0 (±0.05)
- Bias ε < 0.05
- Incompressible (gzip compression ratio < 5%)

### Level 2: Standard Validation (2-8 hours)
**Purpose**: Comprehensive quality verification for general use

- **Full NIST SP 800-22 suite** (15 tests)
- **TestU01 SmallCrush** (10 tests)
- **Quick entropy source validation**

**Pass Criteria**:
- ≥90% of NIST tests pass (p-value ≥ 0.01)
- All TestU01 SmallCrush tests pass
- No obvious patterns in visual inspection

### Level 3: Thorough Validation (1-3 days)
**Purpose**: Cryptographic certification readiness

- **NIST SP 800-22 complete suite** with multiple independent samples
- **TestU01 Crush or BigCrush**
- **PractRand testing**
- **NIST SP 800-90B entropy source testing**

**Pass Criteria**:
- ≥95% of all tests pass
- Min-entropy ≥ 0.9 bits per bit
- No failures in PractRand
- Consistent results across multiple independent samples

### Level 4: Professional Certification
**Purpose**: Production/cryptographic deployment

- Accredited third-party laboratory evaluation
- FIPS 140-2 or FIPS 140-3 certification
- Security review of entropy source design

---

## Statistical Tests Explained

### NIST SP 800-22 Revision 1a (15 Tests)

#### Test 1: Frequency (Monobit) Test
**What it tests**: Checks if the number of 1s and 0s are approximately equal

**Null Hypothesis**: H₀: probability(1) = probability(0) = 0.5

**How it works**:
```
1. Convert output to bit stream
2. Count number of 1s (n_1) and 0s (n_0)
3. Calculate: s = |n_1 - n_0| / √n (where n = total bits)
4. Compute p-value from complementary error function
5. If p-value ≥ 0.01, PASS
```

**Example for 1 million bits**:
- Expected: ~500,000 ones and ~500,000 zeros
- If observed: 501,000 ones, 499,000 zeros → PASS
- If observed: 530,000 ones, 470,000 zeros → FAIL

**Interpretive significance**: Detects most obvious biases; if this fails, generator has fundamental problem.

---

#### Test 2: Frequency Test Within a Block
**What it tests**: Ensures blocks within the sequence are uniformly distributed

**How it works**:
```
1. Divide bit stream into M blocks of length N
2. Count 1s in each block
3. For each block, calculate: p_i = count_1s / N
4. Test if {p_1, p_2, ..., p_M} follows expected distribution
5. Chi-square test on aggregated results
```

**Example**: For 1 million bits in 1000-bit blocks:
- 1000 blocks total
- Each block should have ~500 ones
- Tests for anomalies in any specific block

---

#### Test 3: Runs Test
**What it tests**: Detects if there are too many or too few runs of consecutive identical bits

**Null Hypothesis**: H₀: Bits transition between 0→1 and 1→0 at random intervals

**How it works**:
```
1. Count total runs (maximal sequences of identical bits)
2. For random data: E[runs] ≈ 2pq(n-1) where p=0.5, q=0.5
3. Calculate test statistic
4. Compare to expected distribution
```

**Example - visualizing runs**:
```
Sequence: 110101110011010
Runs:    [11][0][1][0][111][00][11][0][1][0]
Count: 10 runs

For 1 million bits, expect ~500,000 runs
If actual: 450,000-550,000 → likely PASS
If actual: 100,000 or 800,000 → FAIL
```

**Interpretive significance**: Detects patterns like "too clustered" or "alternating" behavior.

---

#### Test 4: Test for Longest Run of Ones in a Block
**What it tests**: Checks for unusually long sequences of consecutive 1s

**How it works**:
```
1. Divide sequence into blocks
2. Find longest run of 1s in each block
3. Categorize runs by length
4. Test if distribution matches expected
```

**Example**:
```
For 8-bit blocks:
11001011 → longest run of 1s = 2
11110011 → longest run of 1s = 4
10111101 → longest run of 1s = 3
```

---

#### Test 5: Binary Matrix Rank Test
**What it tests**: Detects linear dependencies in bit sequences

**How it works**:
```
1. Form matrices (32×32 or 64×64) from bit stream
2. Calculate rank of each matrix over GF(2) (binary field)
3. Count matrices with rank 32, 31, or <31
4. Compare to expected distribution
```

**Interpretive significance**: Catches correlations that simpler tests miss.

---

#### Test 6: Discrete Fourier Transform (Spectral) Test
**What it tests**: Detects periodic patterns using frequency analysis

**How it works**:
```
1. Convert bit stream to ±1 values
2. Apply FFT (Fast Fourier Transform)
3. Count peaks in power spectrum
4. Test if peak count matches expected distribution
5. If too few peaks → periodic structure present
```

**Interpretive significance**: Catches cyclic patterns or modulation artifacts from SDR/video processing.

---

#### Test 7: Non-Overlapping Template Matching Test
**What it tests**: Frequency of specific bit patterns (templates)

**How it works**:
```
1. Define non-overlapping bit patterns (e.g., "111", "101")
2. Count occurrences in stream
3. Compare frequency to expected for random data
4. Use chi-square test
```

**Example**:
```
Pattern: "11" in stream 110110111001
Non-overlapping matches: at positions 0-1 → count = 1

For 1 million bits, expect ~250,000 occurrences of "11"
If actual: 245,000-255,000 → likely PASS
```

---

#### Test 8: Overlapping Template Matching Test
**What it tests**: Similar to non-overlapping but allows pattern overlap

**How it works**:
```
1. Slide template window across entire stream
2. Count total matches (including overlaps)
3. Compare to expected
```

**Example**:
```
Pattern: "11" in stream 1111
Overlapping matches: positions 0-1, 1-2, 2-3 → count = 3
Non-overlapping would count: 1
```

---

#### Test 9: Maurer's Universal Statistical Test
**What it tests**: Measures algorithmic complexity and compressibility

**How it works**:
```
1. Measure distance between matching patterns
2. Calculate: T = (1/n)∑log₂(distance_i)
3. Compare to expected value for random sequence
4. Low T indicates high compressibility (bad randomness)
```

**Interpretive significance**: Catches sequences that appear random but compress well.

---

#### Test 10: Approximate Entropy Test
**What it tests**: Regularity and pattern repetition in sequence

**How it works**:
```
1. For overlapping blocks of length m and m+1
2. Calculate frequency of patterns
3. Compute entropy: ApEn = log(C^m/C^(m+1))
4. Regular patterns have low ApEn, random has high
```

---

#### Test 11: Cumulative Sums (Cusums) Test
**What it tests**: Detects unusual deviations in cumulative bit values

**How it works**:
```
1. Convert bits: 0→-1, 1→+1
2. Calculate cumulative sum: Z_k = ∑(±1)
3. Test if max cumulative deviation is too large
4. Large deviation indicates bias or clustering
```

**Visualization**:
```
Bit sequence:  1 0 1 1 0 1 1 1
As ±1:        +1-1+1+1-1+1+1+1
Cumsum:       1 0 1 2 1 2 3 4
              ↑ If too extreme → FAIL
```

---

#### Test 12: Random Excursions Test
**What it tests**: Properties of cumulative sum excursions from zero

---

#### Test 13: Random Excursions Variant Test
**What it tests**: Frequency of specific state visits

---

#### Test 14: Serial Test
**What it tests**: Distribution of consecutive patterns (m-tuples)

---

#### Test 15: Linear Complexity Test
**What it tests**: Sequence complexity via LFSR (Linear Feedback Shift Register) analysis

**How it works**:
```
1. Find shortest LFSR that generates the sequence
2. Short LFSR → low complexity → not random
3. Expected length: n/2 for random sequence
```

---

### TestU01 Batteries

#### SmallCrush (10 tests)
Quick validation suitable for:
- Initial testing
- Development iterations
- Quick feedback loop

**Typical runtime**: 30 seconds - 2 minutes for 10M bits

#### Crush (96 tests)
Comprehensive testing for:
- General randomness verification
- Production quality checks
- Subtle bias detection

**Typical runtime**: 15-30 minutes for 1GB data

#### BigCrush (160 tests)
Exhaustive testing for:
- Security-critical applications
- Research validation
- Detailed failure analysis

**Typical runtime**: 2-8 hours for 10GB data

---

### PractRand

**Advantages**:
- Detects subtle biases missed by NIST STS
- Particularly good at catching:
  - Subtle correlation patterns
  - Weak periodicity
  - Non-uniform mixing
- Real-time streaming analysis possible

**Output format**:
```
[8 MB]   PASS ... and 0 words
[16 MB]  PASS ... and 0 words
[32 MB]  PASS ... and 0 words
...
[512 MB] FAIL: BirthdaySpacings test [Low16/64]
```

---

### NIST SP 800-90B Entropy Source Testing

**Purpose**: Validates that your hardware sources are providing true entropy

**Key Tests**:
1. **IID (Independent and Identically Distributed) Testing**
   - Checks if raw entropy bits are independent
   - Catches correlated outputs from SDR/video

2. **Min-Entropy Estimators** (multiple approaches):
   - **Prediction estimator**: Can we predict next bits?
   - **LZ77 compression**: Does data compress?
   - **Markov model**: Are state transitions predictable?
   - **Lag predictor**: Autocorrelation-based

3. **Min-Entropy Per Bit**: Should be ≥ 0.9 for cryptographic use

**Critical for your design**: Run this to verify SDR + video mixing actually produces entropy gain.

---

## Implementation Guide

### Step 1: Generate Test Data

**Code Structure** (Python):

```python
import hashlib
from collections import Counter

def generate_test_samples(sdr_stream, video_stream, num_samples=1_000_000, output_length=9):
    """
    Generate test data from your hardware RNG
    
    Args:
        sdr_stream: Binary stream from SDR
        video_stream: Binary stream from video
        num_samples: Number of 9-digit numbers to generate
        output_length: Configurable output length (bits)
    
    Returns:
        numbers: List of generated random numbers
        bit_stream: Concatenated bit representation
    """
    numbers = []
    bit_stream = []
    
    L = 64
    
    for i in range(num_samples):
        # Extract x, y from your streams
        x = get_next_bits(sdr_stream, L)
        y = get_next_bits(video_stream, L)
        
        # Your entropy mixing formula
        lx = x.bit_length()
        ly = y.bit_length()
        E = (lx << (L + ly + lx)) | (ly << (lx + L)) | (x << ly) | y
        
        # SHA256 processing
        hashed = hashlib.sha256(E.to_bytes(256, 'big')).digest()
        
        # Extract output_length bits
        output = int.from_bytes(hashed[:output_length//8], 'big')
        numbers.append(output)
        
        # Collect bit representation for statistical tests
        bit_stream.extend(bin(output)[2:].zfill(output_length))
    
    return numbers, ''.join(bit_stream)


def save_bitstream_for_testing(bit_stream, filename):
    """Save as ASCII for NIST STS and PractRand"""
    with open(filename, 'w') as f:
        f.write(bit_stream)
    
    # Also save binary version for some tools
    binary_data = bytes(int(bit_stream[i:i+8], 2) for i in range(0, len(bit_stream), 8))
    with open(filename + '.bin', 'wb') as f:
        f.write(binary_data)
```

**Sample sizes by test complexity**:
- Quick sanity checks: 100,000 bits
- NIST STS: 1,000,000 bits minimum (preferably 10,000,000)
- TestU01 SmallCrush: 10,000,000 bits
- TestU01 Crush: 1,000,000,000+ bits
- PractRand: Start with 1GB, can go higher

---

### Step 2: Level 1 - Quick Sanity Checks

```python
import math
from scipy import stats

def quick_sanity_checks(bit_stream):
    """Run Level 1 tests"""
    
    # Test 1: Monobit Frequency
    n_ones = bit_stream.count('1')
    n_zeros = len(bit_stream) - n_ones
    total = len(bit_stream)
    
    # Chi-square test for 0s vs 1s
    chi2, p_value = stats.chisquare([n_ones, n_zeros])
    print(f"Monobit Test:")
    print(f"  1s: {n_ones}, 0s: {n_zeros}")
    print(f"  p-value: {p_value:.6f} {'PASS' if p_value >= 0.01 else 'FAIL'}")
    
    # Test 2: Shannon Entropy
    prob_1 = n_ones / total
    prob_0 = n_zeros / total
    shannon_h = -(prob_1 * math.log2(prob_1) + prob_0 * math.log2(prob_0))
    print(f"\nShannon Entropy: {shannon_h:.6f} (target: 1.0)")
    print(f"  {'PASS' if 0.95 <= shannon_h <= 1.05 else 'WARNING'}")
    
    # Test 3: Bias Estimation
    bias = abs(prob_1 - 0.5)
    print(f"\nBias: {bias:.6f} (target: <0.01)")
    print(f"  {'PASS' if bias < 0.01 else 'WARNING'}")
    
    # Test 4: Runs Test
    runs = 1
    for i in range(len(bit_stream) - 1):
        if bit_stream[i] != bit_stream[i+1]:
            runs += 1
    
    expected_runs = 2 * n_ones * n_zeros / total
    variance = 2 * n_ones * n_zeros * (2*n_ones*n_zeros - total) / (total**2 * (total-1))
    z_score = (runs - expected_runs) / math.sqrt(variance)
    p_runs = 2 * (1 - stats.norm.cdf(abs(z_score)))
    
    print(f"\nRuns Test:")
    print(f"  Observed runs: {runs}")
    print(f"  Expected runs: {expected_runs:.0f}")
    print(f"  p-value: {p_runs:.6f} {'PASS' if p_runs >= 0.01 else 'FAIL'}")
    
    # Test 5: Compression Check
    import gzip
    original_size = len(bit_stream) // 8
    compressed = gzip.compress(bit_stream.encode())
    compression_ratio = len(compressed) / original_size
    
    print(f"\nCompression Test:")
    print(f"  Original: {original_size} bytes")
    print(f"  Compressed: {len(compressed)} bytes")
    print(f"  Ratio: {compression_ratio:.2%}")
    print(f"  {'PASS' if compression_ratio > 0.95 else 'FAIL'} (target: >95%)")
```

---

### Step 3: Level 2 - Standard Validation

#### Option A: NIST STS Installation & Usage

**Installation (Linux/Ubuntu)**:
```bash
# Download NIST STS
wget https://csrc.nist.gov/projects/random-bit-generation/documentation-and-software

# Extract and build
unzip sts-2.1.2.zip
cd sts-2.1.2
make

# Prepare data (convert to ASCII format)
python3 -c "
bit_stream = '...'  # your bits
with open('data.txt', 'w') as f:
    f.write(bit_stream)
"

# Run NIST STS
./assess 1000000
# Follow interactive prompts
# Select test file: data.txt
# Select stream format: 1 (for ASCII)
```

**Output Interpretation**:
```
NIST STS Output:
Test: Frequency
p_value: 0.123456 -> PASS (p >= 0.01)

Test: Runs  
p_value: 0.00542 -> FAIL (p < 0.01)

Test: Block Frequency
p_value: 0.876543 -> PASS
...
```

**Acceptance criteria**:
- At least 90% of 15 tests should PASS
- p-values should be well-distributed (not all near 1.0 or 0.0)

---

#### Option B: Python Implementation (nistrng)

```bash
pip install nistrng
```

```python
from nistrng import *

# Load your test data
with open('bitstream.txt', 'r') as f:
    bits = f.read().strip()

# Convert to list of integers
bits = [int(b) for b in bits]

# Run NIST suite
suite = [
    monobit_test,
    frequency_test_within_a_block,
    runs_test,
    longest_run_of_ones_in_a_block,
    binary_matrix_rank_test,
    dft_test,
    non_overlapping_template_matching_test,
    overlapping_template_matching_test,
    maurers_universal_statistical_test,
    linear_complexity_test,
    serial_test,
    approximate_entropy_test,
    cumulative_sums_test,
    random_excursions_test,
    random_excursions_variant_test
]

# Run all tests
results = []
for test in suite:
    result = test(bits)
    results.append((test.__name__, result))
    print(f"{test.__name__}: {result}")

# Summary
passed = sum(1 for _, result in results if result)
print(f"\nPassed: {passed}/{len(results)}")
```

---

### Step 4: Level 3 - Thorough Validation

#### TestU01 Installation & Usage

**Installation**:
```bash
# Download from http://simul.iro.umontreal.ca/testu01/tu01.html
wget http://simul.iro.umontreal.ca/testu01/TestU01.zip
unzip TestU01.zip
cd TestU01-1.2.3
./configure
make
sudo make install
```

**Usage**:
```bash
# Prepare data (binary format)
python3 convert_to_binary.py bitstream.txt > data.bin

# Run SmallCrush
testu01_smallcrush data.bin

# Run Crush (for more thorough testing)
testu01_crush data.bin

# Run BigCrush (comprehensive)
testu01_bigcrush data.bin
```

---

#### PractRand Installation & Usage

**Installation**:
```bash
# Download from http://pracrand.sourceforge.net/
wget https://sourceforge.net/projects/pracrand/files/PractRand/latest
unzip PractRand_...
cd PractRand_...
make

# Or simpler: apt install pracrand
sudo apt install pracrand
```

**Usage**:
```bash
# Run on binary data
RNG_test stdin < data.bin

# Or pipe directly
python3 generate_stream.py | RNG_test stdin

# Watch real-time output as data is tested
# Will show PASS/FAIL for each chunk (8MB blocks typically)
```

**Output Example**:
```
[8 MB]    PASS ... and 0 words in 0.20 sec
[16 MB]   PASS ... and 0 words in 0.20 sec
[32 MB]   PASS ... and 0 words in 0.20 sec
[64 MB]   PASS ... and 0 words in 0.20 sec
[128 MB]  PASS ... and 0 words in 0.21 sec
[256 MB]  PASS ... and 0 words in 0.22 sec
[512 MB]  FAIL: BirthdaySpacings test [Low16/64]
```

---

### Step 5: Entropy Source Validation (SP 800-90B)

**For academic/development purposes**, estimate min-entropy:

```python
def estimate_min_entropy(raw_bits, k=16):
    """
    Estimate min-entropy using prediction method
    
    Attempts to predict next bit based on:
    - Last k bits (history)
    - Bit frequency
    - Observed patterns
    """
    
    # Count transitions
    prediction_correct = 0
    total_predictions = 0
    
    for i in range(k, len(raw_bits)):
        # Simple predictor: predict majority from last k bits
        window = raw_bits[i-k:i]
        if window.count('1') > k/2:
            prediction = '1'
        else:
            prediction = '0'
        
        if prediction == raw_bits[i]:
            prediction_correct += 1
        total_predictions += 1
    
    # Prediction success rate
    success_rate = prediction_correct / total_predictions
    
    # Min-entropy: -log2(max probability of guessing)
    # Success rate maps to max probability of next bit
    if success_rate <= 0.5:
        min_entropy = 1.0  # Near perfect
    else:
        min_entropy = -math.log2(success_rate)
    
    print(f"Prediction Success Rate: {success_rate:.4f}")
    print(f"Estimated Min-Entropy: {min_entropy:.4f} bits per bit")
    print(f"Target: >= 0.9 bits per bit")
    print(f"Status: {'PASS' if min_entropy >= 0.9 else 'FAIL'}")
    
    return min_entropy
```

---

## Practical Testing Workflow

### Timeline & Resource Requirements

#### For Initial Development (Your Phase)
**Time**: 1-2 hours per iteration
**Data**: 10 million bits (1.25 MB)

```
Step 1: Generate 10M bits (5 minutes)
Step 2: Quick sanity checks (5 minutes)
  - Monobit test
  - Entropy calculation
  - Compression check
Step 3: NIST STS full suite (30-45 minutes)
Step 4: TestU01 SmallCrush (5-10 minutes)
Step 5: Analyze results (10-15 minutes)
```

**Decision logic**:
- All quick checks pass? → Proceed to detailed testing
- Any quick check fails? → Debug entropy mixing, increase bit extraction, adjust formula
- NIST or SmallCrush fails? → Investigate which test failed, revisit entropy source quality

---

#### For Quality Assurance
**Time**: 4-8 hours
**Data**: 1 billion bits (125 MB)

```
Step 1: Generate 1B bits (15-30 minutes)
Step 2: NIST STS with multiple runs (1-2 hours)
Step 3: TestU01 Crush (1-2 hours)
Step 4: PractRand full sequence (1-2 hours)
Step 5: Min-entropy estimation (30 minutes)
Step 6: Report generation (30 minutes)
```

---

#### For Cryptographic Certification
**Time**: 1-3 weeks
**Data**: 10+ billion bits (1+ GB)
**Expert review**: Required

```
Step 1: Multiple independent test runs (ongoing)
Step 2: NIST STS, TestU01 BigCrush, PractRand (parallel)
Step 3: NIST SP 800-90B entropy source validation
Step 4: Design documentation and security review
Step 5: Independent lab evaluation (optional but recommended)
```

---

## Tool Reference

### Quick Comparison

| Tool | Use Case | Runtime | Sensitivity | Ease |
|------|----------|---------|-------------|------|
| **Manual (Chi-sq, Runs)** | Quick sanity | Seconds | Low | Easy |
| **NIST STS** | Standard validation | 30min-2hr | Medium | Medium |
| **TestU01 SmallCrush** | Development testing | 1-5min | Medium | Easy |
| **TestU01 Crush** | Quality assurance | 30min-2hr | High | Medium |
| **TestU01 BigCrush** | Certification prep | 4-12hr | Very High | Medium |
| **PractRand** | Subtle bias detection | 30min-4hr | Very High | Easy |
| **ENT** | Quick estimate | Seconds | Low | Very Easy |
| **Dieharder** | Additional validation | 1-2hr | High | Medium |

---

### Installation Quick Reference

**Ubuntu/Debian**:
```bash
# NIST STS
wget https://csrc.nist.gov/projects/random-bit-generation/documentation-and-software
# Follow build instructions

# TestU01
sudo apt install testu01  # Or build from source

# PractRand
sudo apt install pracrand

# Python libraries
pip install nistrng scipy numpy
```

**macOS**:
```bash
brew install testu01
brew install pracrand
pip install nistrng scipy numpy
```

---

## Troubleshooting & Interpretation

### Common Failure Scenarios

#### Scenario 1: Monobit Test Fails
**Symptom**: p-value < 0.01, imbalance between 0s and 1s

**Likely causes**:
- SDR hardware bias (check SDR calibration)
- Video data not truly random (lighting variations, static scenes)
- SHA256 not properly mixing entropy sources

**Solution**:
- Increase entropy source sample size (L parameter)
- Add XOR operations between SDR and video streams
- Verify entropy sources are actually independent
- Check bit extraction is correct (no off-by-one errors)

---

#### Scenario 2: Runs Test Fails
**Symptom**: Too many or too few runs; observable clustering

**Likely causes**:
- Temporal correlation in entropy sources
- Inadequate mixing between sources
- Weak SDR signal causing bit repetition

**Solution**:
- Implement higher-order entropy mixing (use more state)
- Add temporal decorrelation step (e.g., Von Neumann extractor)
- Verify SDR SNR is sufficient
- Increase delay between consecutive entropy source samples

---

#### Scenario 3: Multiple NIST Tests Fail (>10%)
**Symptom**: >10% of NIST tests fail; likely systematic pattern

**Likely causes**:
- Entropy sources not truly independent
- Hash function not properly mixing inputs
- Insufficient entropy extraction

**Solution**:
- Review entropy mixing formula carefully
- Test SDR and video streams independently
- Increase L parameter (64 may be too small)
- Consider additional post-processing:
  - Von Neumann extractor
  - Toeplitz matrix transformation
  - Iterative hashing

---

#### Scenario 4: Compression Ratio High (>10% compressibility)
**Symptom**: Sequence compresses noticeably; indicates patterns

**Likely causes**:
- Repeating patterns from video (e.g., frame sync, header data)
- SDR modulation artifacts
- Inadequate entropy mixing

**Solution**:
- Skip leading bits of video frames (skip header/sync)
- Use middle bits of video (avoid edges with artifacts)
- Ensure video content has enough variation
- Increase mixing complexity

---

#### Scenario 5: PractRand Fails While NIST Passes
**Symptom**: PractRand detects failures at 256MB+ that NIST missed

**Interpretation**: Subtle biases present, missed by NIST's test battery

**Solution**:
- Treat as genuine failure (PractRand is stricter)
- Investigate entropy source correlation
- Review mixing formula for hidden patterns
- Consider redesigning entropy extraction

---

### P-value Distribution Interpretation

**Good Distribution** (Random generator):
```
P-value ranges:
[0.00-0.10]: 2-3 tests
[0.10-0.20]: 2-3 tests
[0.20-0.30]: 2-3 tests
[0.30-0.40]: 2-3 tests
[0.40-0.50]: 1-2 tests
[0.50-0.60]: 1-2 tests
[0.60-0.70]: 1-2 tests
[0.70-0.80]: 1-2 tests
[0.80-0.90]: 1-2 tests
[0.90-1.00]: 1-2 tests
```

**Suspicious Distribution** (Possible issues):
```
All p-values clustered at 0.95-1.00
→ Tests passing "too perfectly" (possible weakness in mixing)

Many p-values < 0.01
→ Systematic non-random structure

P-values form specific pattern (e.g., all even, all odd)
→ Underlying bias or correlation
```

---

### Interpreting NIST Test Failures

**1 test fails** (out of 15)
- Possibly random fluctuation (expected ~5%)
- If same test fails on multiple independent runs: investigate

**2-3 tests fail** (out of 15)
- Suggests pattern in one aspect (e.g., all compression-related tests)
- Isolate the specific property being tested
- Debug that component

**>4 tests fail** (out of 15)
- Likely systematic issue
- Design or implementation problem
- Significant rework needed

---

### When to Move Between Testing Levels

**Move from Level 1 → Level 2**: When all sanity checks pass consistently

**Move from Level 2 → Level 3**:
- Level 2 shows ≥90% pass rate
- No systematic failures
- Ready for deeper analysis

**Stop and Debug**:
- Level 1: Any test fails consistently
- Level 2: <70% pass rate
- Level 3: PractRand failure or BigCrush >5% failures

---

## Quick Reference Checklist

### Pre-Testing Checklist
- [ ] Entropy sources (SDR, video) verified working
- [ ] Bit extraction logic tested with known inputs
- [ ] SHA256 implementation verified
- [ ] Output range confirmed (0 to 999,999,999 for 9-digit)
- [ ] No buffer overflows or integer wraparound issues
- [ ] Sufficient test data can be generated

### Level 1 Testing
- [ ] Monobit frequency test run (p-value recorded)
- [ ] Shannon entropy calculated
- [ ] Bias estimated
- [ ] Runs test performed
- [ ] Compression ratio checked
- [ ] All Level 1 tests PASS

### Level 2 Testing
- [ ] NIST STS downloaded/installed
- [ ] Test data generated (1M+ bits)
- [ ] All 15 NIST tests executed
- [ ] TestU01 SmallCrush run
- [ ] ≥90% of tests passed
- [ ] Results documented with timestamps

### Level 3 Testing
- [ ] Large dataset prepared (1B+ bits)
- [ ] TestU01 Crush/BigCrush executed
- [ ] PractRand completed without FAIL
- [ ] Min-entropy estimated
- [ ] Multiple independent test runs completed
- [ ] Results consistent across runs

### Documentation
- [ ] Test date and time recorded
- [ ] Entropy source configuration documented
- [ ] All parameters (L, output_length, hash function) recorded
- [ ] Test data size recorded
- [ ] All test results saved with p-values
- [ ] Summary report generated
- [ ] Any anomalies investigated and documented

---

## Recommended Testing Protocol for Your Hardware RNG

### Phase 1: Development (Current)
**Objective**: Verify entropy mixing formula works

**Actions**:
```
1. Generate 10M bits daily during development
2. Run Level 1 checks after each formula modification
3. Keep quick sanity check results in log
4. When consistently passing Level 1 → proceed to Phase 2
```

### Phase 2: Validation
**Objective**: Confirm design is sound

**Actions**:
```
1. Generate 1B bits from final design
2. Run full NIST STS suite
3. Run TestU01 SmallCrush
4. Estimate min-entropy
5. Document all results
6. If ≥90% pass → proceed to Phase 3
7. If <90% pass → investigate and revise design
```

### Phase 3: Certification Preparation
**Objective**: Ready for production/cryptographic use

**Actions**:
```
1. Generate 10B bits (multiple independent runs)
2. Complete NIST STS multiple times
3. Run TestU01 BigCrush
4. Complete PractRand testing
5. Full NIST SP 800-90B entropy source assessment
6. Generate comprehensive test report
7. Consider independent lab evaluation
```

---

## References & Further Reading

### Primary Sources
- NIST SP 800-22 Revision 1a: "A Statistical Test Suite for Random Number Generators for Cryptographic Applications"
- NIST SP 800-90B: "Recommendation for the Entropy Sources Used for Random Bit Generation"
- TestU01 Documentation: http://simul.iro.umontreal.ca/testu01/
- PractRand: http://pracrand.sourceforge.net/

### Standards
- FIPS 140-2: "Security Requirements for Cryptographic Modules"
- FIPS 140-3: Updated version (2019)
- FIPS 186-4: "Digital Signature Standard (DSS)"

### Key Papers
- Rukhin et al. (2010): "NIST Statistical Test Suite"
- L'Ecuyer & Simard (2007): "TestU01: A C Library for Empirical Testing of Random Number Generators"
- Cowan (1997): Diehard tests original paper

---

## Conclusion

This master testing framework provides:

✅ **Theoretical understanding** of what each test measures  
✅ **Practical implementation** for running tests  
✅ **Interpretation guidance** for analyzing results  
✅ **Troubleshooting strategies** for common failures  
✅ **Phased approach** from development to certification  

**Key principle**: Start simple, iterate fast, advance systematically. No single test proves randomness—only a battery of complementary tests gathering statistical evidence of the *absence* of non-randomness.

Your hardware RNG combining SDR and video entropy sources is well-positioned for validation. Focus first on confirming entropy source independence, then on output quality through statistical testing.