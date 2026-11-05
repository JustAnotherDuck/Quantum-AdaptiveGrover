# Archived Modules

This directory contains experimental and exploratory modules that were evaluated during the early stages of the AdaptiveGrover-QCA research project and subsequently archived to maintain sharp focus on the core research questions.

## Archived Components

### 1. `bbht.py` (Boyer-Brassard-Høyer-Tapp 1996 Algorithm)
- **Original Purpose**: Tested exponential iteration schedules ($m \leftarrow \min(\lambda m, \sqrt{N})$) for search spaces with an unknown number of marked items.
- **Reason for Archiving**: In symmetric key cryptanalysis (the core focus of this project), a unique plaintext-ciphertext pair typically induces exactly $M = 1$ unique target key (or a small known multiplicity confirmed by a second plaintext-ciphertext pair). The fixed-budget adaptive controller, depth modulation, and shallow-restart mechanisms directly address realistic noisy search without the geometric overhead of blind exponential search schedules.

### 2. `toyspn.py` (Heys 2002 16-bit Pedagogical SPN)
- **Original Purpose**: Classical reference implementation of the substitution-permutation network described in Howard Heys's 2002 tutorial.
- **Reason for Archiving**: The project consolidated its cipher targets onto:
  1. **Simplified AES (S-AES)** (`src/agqca/ciphers/saes.py`): Primary 16-bit classical cipher target verified against Schaefer (2003) test vectors.
  2. **Reversible SPN Oracle (Mode B)** (`src/agqca/oracles/mode_b_spn.py`): Direct quantum gate-level reversible compute-copy-uncompute circuit implementing Heys S-box and linear diffusion layers without classical software scaffolding.

Both modules remain functional and preserved here for historical provenance and reproducibility.
