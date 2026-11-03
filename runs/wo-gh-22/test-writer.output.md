Tests written to `tests/test_model_benchmark.py` covering scenarios S1, S2, and S3. The tests verify:

- **S1**: Ground truth has exactly 10 entries V1-V10 mapping to K1-K10, and fixture page carries planted values
- **S2**: Scorer fails K1-K10 and passes K11-K12 on fixture; passes all 12 checks on compliant page (includes minimal compliant page inline)
- **S3**: tokens.json and DESIGN.md agree on every token value

The tests follow the existing factory suite style (unittest, scenario-tagged docstrings, tempfile fixtures) and require no browser or Playwright dependencies. They will pass once the builder station creates the benchmark files.
