
import argparse
import json
import os
import re
from datetime import datetime

# Heuristic mappings for entity type validation
HEADING_TO_ENTITY_TYPE_HINT = {
    "medications": ["MEDICATION"],
    "vaccinations": ["IMMUNIZATION"],
    "diagnosis": ["PROBLEM"],
    "problems": ["PROBLEM"],
    "allergies": ["ALLERGY"],
    "procedures": ["PROCEDURE"],
    "vitals": ["VITAL_NAME"],
    "tests": ["TEST", "LAB_RESULT"]
}

# Assertion and Temporality Keywords
NEGATION_KEYWORDS = ["no evidence of", "ruled out", "denies", "not present", "absence of"]
UNCERTAIN_KEYWORDS = ["possible", "suspected", "query", "rule out", "likely"]
CURRENT_KEYWORDS = ["currently", "on admission", "presenting with", "ongoing", "now"]
HISTORY_KEYWORDS = ["history of", "past medical history", "previous", "prior", "resolved"]
UPCOMING_KEYWORDS = ["scheduled for", "to be performed", "plan for", "follow-up in"]

# Date extraction
DATE_PATTERNS = [r'\d{4}-\d{2}-\d{2}', r'\d{1,2}/\d{1,2}/\d{2,4}']
PLACEHOLDER_DATES = ["[ENCOUNTER_DATE]", "[DATE_OF_BIRTH]", "[DOB]", "[SERVICE_DATE]"]

# Attribute Completeness Mapping
EXPECTED_ATTRIBUTES = {
    "MEDICATION": ["STRENGTH", "UNIT", "DOSE", "ROUTE", "FREQUENCY"],
    "TEST": ["TEST_VALUE", "TEST_UNIT"],
    "VITAL_NAME": ["VITAL_NAME_VALUE", "VITAL_NAME_UNIT"]
}

def calculate_entity_type_errors(entities):
    if not entities: return 0.0
    errors = 0
    for e in entities:
        h = e.get("heading", "").lower()
        t = e.get("entity_type", "")
        for hint, valid_types in HEADING_TO_ENTITY_TYPE_HINT.items():
            if hint in h and t not in valid_types: 
                errors += 1
                break
    return errors / len(entities)

def calculate_assertion_errors(entities):
    if not entities: return 0.0
    errors = 0
    for e in entities:
        text = e.get("text", "").lower()
        ass = e.get("assertion", "")
        if ass == "POSITIVE" and any(kw in text for kw in NEGATION_KEYWORDS): errors += 1
        elif ass == "NEGATIVE" and not any(kw in text for kw in NEGATION_KEYWORDS): errors += 1
    return errors / len(entities)

def calculate_temporality_errors(entities):
    if not entities: return 0.0
    errors = 0
    for e in entities:
        text = e.get("text", "").lower()
        temp = e.get("temporality", "")
        if temp == "CURRENT" and any(kw in text for kw in HISTORY_KEYWORDS): errors += 1
    return errors / len(entities)

def calculate_subject_errors(entities):
    if not entities: return 0.0
    errors = sum(1 for e in entities if e.get("subject") != "PATIENT")
    return errors / len(entities)

def calculate_event_date_accuracy(entities):
    total_derived = 0
    accurate = 0
    for e in entities:
        derived = None
        rels = e.get("metadata_from_qa", {}).get("relations", [])
        for r in rels:
            if r.get("entity_type") == "derived_date":
                derived = r.get("entity")
                break
        if derived and derived not in PLACEHOLDER_DATES:
            total_derived += 1
            text = e.get("text", "")
            if derived in text: accurate += 1
    return accurate / total_derived if total_derived > 0 else 1.0

def calculate_attribute_completeness(entities):
    if not entities: return 0.0
    total_ratio = 0.0
    for e in entities:
        etype = e.get("entity_type")
        if etype in EXPECTED_ATTRIBUTES:
            expected = EXPECTED_ATTRIBUTES[etype]
            found = 0
            rels = [r.get("entity_type") for r in e.get("metadata_from_qa", {}).get("relations", [])]
            for attr in expected:
                if attr in rels: found += 1
            total_ratio += (found / len(expected))
        else:
            total_ratio += 1.0
    return total_ratio / len(entities)

def evaluate_document(input_path, output_path):
    with open(input_path, 'r') as f: data = json.load(f)
    report = {
        "input_file": os.path.basename(input_path),
        "metrics": {
            "entity_type_error_rate": calculate_entity_type_errors(data),
            "assertion_error_rate": calculate_assertion_errors(data),
            "temporality_error_rate": calculate_temporality_errors(data),
            "subject_error_rate": calculate_subject_errors(data),
            "event_date_accuracy": calculate_event_date_accuracy(data),
            "attribute_completeness": calculate_attribute_completeness(data)
        }
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f: json.dump(report, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_json", required=True)
    parser.add_argument("--output_json", required=True)
    args = parser.parse_args()
    evaluate_document(args.input_json, args.output_json)
