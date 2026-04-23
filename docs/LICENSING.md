# Licensing Notes

Do not make the final licensing decision blindly. The project description supports open science, but the project also mentions technology transfer, commercialization, and IP protection.

## Recommended Split

Use separate thinking for:

- documentation
- code
- curated dataset
- raw measurement logs

## Practical Recommendation

### Documentation

Recommended:

- `CC-BY-4.0`

Why:

- easy reuse with attribution
- appropriate for README files, dataset cards, and explanatory text

### Code and Scripts

Recommended:

- `MIT`
- or `Apache-2.0` if you want an explicit patent grant

Why:

- common for research tooling
- GitHub users understand these licenses well

### Curated Tabular Dataset

Recommended candidates:

- `CC-BY-4.0`
- `CC0-1.0` only if the consortium explicitly wants maximum reuse

Why:

- dataset users often expect a Creative Commons style data license
- `CC-BY-4.0` keeps attribution expectations clear

### Raw Measurement Logs

Default recommendation:

- do not publish under an open license until the consortium explicitly approves it

Why:

- raw files may contain operational details, vendor-specific structure, or material that the consortium may want to retain for future exploitation

## Safe Initial Position

For the first public GitHub repository:

- publish docs and metadata first
- publish the curated dataset only after review
- add formal licenses only when the release scope is approved

## What to Confirm Before Final Licensing

Check with the consortium or project lead:

1. Can the curated public dataset be openly redistributed?
2. Are raw logs excluded from the public release?
3. Do you want attribution to the consortium, institution, or named authors?
4. Is there any planned patent, utility model, or commercial follow-up that would be weakened by premature disclosure?

## Suggested Final Setup

If the consortium agrees to an open release:

- `LICENSE` for code: `MIT` or `Apache-2.0`
- `LICENSE-DATA` for dataset: `CC-BY-4.0`
- mention the split clearly in `README.md`
