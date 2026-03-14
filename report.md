# Clinical Entity Extraction Pipeline Reliability Report

## Quantitative Evaluation Summary

| Metric | Average Value |
| :--- | :--- |
| Entity Type Error Rate | 0.0863 |
| Assertion Error Rate | 0.1467 |
| Temporality Error Rate | 0.1041 |
| Subject Error Rate | 0.0188 |
| Event Date Accuracy | 0.2765 |
| Attribute Completeness | 0.9024 |

## Identified Systemic Weaknesses
- High entity type classification error rate.
- Low event date extraction accuracy.

## Proposed Guardrails
1. **Enhanced Date Parsing**: Implement more robust regex patterns or LLM-based date resolution to improve `event_date_accuracy` beyond simple text matches.
2. **Expanded Keyword Lexicon**: Increase the breadth of negation and temporal keywords to reduce false positives in `assertion` and `temporality` logic.
3. **Schema Validation**: Introduce mandatory attribute checks at the extraction stage to ensure high `attribute_completeness` for critical entity types like MEDICATIONS.
4. **Context-Aware Classification**: Use section-specific LLM prompts to improve `entity_type` accuracy in ambiguous document regions.
