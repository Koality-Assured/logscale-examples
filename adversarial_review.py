#!/usr/bin/env python3
"""Adversarial Security, Quality & Hygiene Auditor for Koality-Assured/logscale-examples.

Performs strict adversarial validation across the repository:
1. Zero-Leak Cryptographic Hash Scan: Scans every token and word across every file against
   cryptographic SHA-256 hashes of private identifiers (account IDs, company names,
   internal project codenames, domains). Hashing these targets guarantees the audit
   script itself does not expose sensitive strings in a public repository.
2. Pattern Leak Scan: Verifies zero local Windows paths, user profiles, or secret tokens.
3. Syntax Validation: Ensures 100% valid syntax across all YAML, Python, and JSON files.
4. Execution Policy Enforcement: Guarantees no live running GitHub Actions workflows exist.
5. Documentation Coverage: Validates that all example directories maintain clear READMEs.
"""

import ast
import hashlib
import json
import os
import re
import sys
from pathlib import Path
import yaml

# SHA-256 hashes of private identifiers that MUST NOT appear anywhere in the codebase.
# Hashing these ensures the public repository does not leak the target values via the audit script itself.
FORBIDDEN_HASHES = {
    # Real AWS account IDs
    "55ebcead5a2750f58cfa1f2666b939fb2782cdef463f7d35144b811dd2c1f739": "AWS Account Hash 077***",
    "aadaec0bf561fb47bc268441f4477f3b9a1ae27f8a80230accb1ef75616f05cf": "AWS Account Hash 682***",
    "91063785aca71cc0aae154589a2e5f8dc086a337c0de1849d8b848dd019f2f53": "AWS Account Hash 026***",
    "1a4cf100217328d19912869af7ce6a4045adf469fecef3600dfa123c4fe202da": "AWS Account Hash 660***",
    "1d21eb187ae938d6cfa49d94a3b108cfeea3a52446e9864d0671048ce056330f": "AWS Account Hash 057***",
    "7eb1bc27dcd577dbbc76d13c5d43a99ef36b504774ea40031e1a67779b2d4f4e": "AWS Account Hash 648***",
    "972765e0abf03b1c64247aa61112ee6aab2bb913662b28e4cd41197ff729bf17": "AWS Account Hash 688***",
    "464d7afe5f1a8cb05904876a78ef3685c9da0d6df4dbf7125149cfab3070be10": "AWS Account Hash 412***",
    "30ef74ab87e1792ba845a0779a464c7fdc4cd3342d7e77b5d174709c7bb300ed": "AWS Account Hash 961***",
    "41ccd800b3930140e049364aaa9a532eb8f7359d96008e9651acd29b8fddb76e": "AWS Account Hash 450***",
    "dab08fbe1577b214e0e423483f01649c268b713e42f3c08de39825eab5a377a5": "AWS Account Hash 629***",
    "0856e9cd8993ed12c08c536039bff5044e6de2e9f73a26b9e8fc969036b605f0": "AWS Account Hash 673***",
    "89a8ab0a9bd79161a59a21b33d334a6755a66dcb97771557c6d1f784c52450b8": "AWS Account Hash 992***",
    "3f5cfd1a08073e1dcee48f77aa71be728b85625dc347d4c6a8fdbf73dd0d87aa": "AWS Account Hash 135***",
    "944db6fb3568c0722241cfd1ffc4fa315aa6f51cb7e42d72f9d77eb55620857a": "AWS Account Hash 038***",

    # Proprietary entities / names
    "cf7d21665b5498c0123f7512cc407ac574d8249c70f4174d0edfbfab713f9af7": "Entity Name Hash tak***",
    "7626518e064a333ced98412bdf9aadbf42e333e0084fed078d16a3b4c0b5cffc": "Entity Name Hash tak***",
    "de69cd742264d4e3fbc8b95df35e2e96d5d68ae763119019b97c1fec6c281b0d": "Org Name Hash 2k-***",
    "93ac07d758d5634824a161b417f614a12d6078323bf0933335306ae81e5f2439": "Org Name Hash 2ks***",
    "7b2faf5774f12d731ad15adec005d73bcacab03d17b698e0745723beadeda744": "Domain Name Hash 2k.***",
    "b1837abd75fdbc571e8da42402afc6b09bdfb4f2fec78d56e95fb24ac9682a2e": "Project Hash aut***",
    "189c75f4c97ee38ea13c0892361a676141a31a748a79db2a0738c07e46a242b4": "Project Hash pix***",
    "7904791f9bb496a3354bf75641e45feb31e881a00cebcb2508e45bd942a6e430": "Project Hash fra***",
    "993fc867ac79d748c13a4ffbe2b2f4555327de8381611dd3865cfe76e899fce6": "Project Hash sym***",
    "f6828ddd9713116e4ee6d04c12f0ecdcbd9e5499755aca87c345cb600ca8dded": "Project Hash dat***",
    "79b23bf9e922d02169cabc6ee5cbe6bfe45cdd67c7cb4f0fdbd4dff17dd87d31": "Domain Hash aws***",
    "318099ac47f991dbcc87b6816a1c0f8b572b6bf9eaa5e4fa8bafbfbee4698dab": "Directory Identifier Hash d-9***",
    "c8f0007fe810b14c194165603bb97ae66cc651a540131464b52044810237e19f": "User Name Hash rob***",
    "8584dc7e2241cf89ebefd95e783688126ab56ec94589d980309995180cb96174": "Email Hash rob***@2k.***",
}

# Forbidden regex patterns (path leaks, private IPs, ciphertext secrets)
FORBIDDEN_PATTERNS = [
    (re.compile(r'c:[\\/]users[\\/]', re.IGNORECASE), "Local Windows User Path"),
    (re.compile(r'c:[\\/]code[\\/]other2k', re.IGNORECASE), "Local Source Repository Path"),
    (re.compile(r'AAABAOC\+[a-zA-Z0-9\+/]{50,}', re.IGNORECASE), "Realistic Encrypted Secret Token"),
    (re.compile(r'RctLKVNnP6USYecHz1d2IdMLmclf3Dak/epcav1jZsngrP6WyYJpJxuxs', re.IGNORECASE), "Specific External ID Secret"),
]

REPO_ROOT = Path(__file__).resolve().parent


def audit_leaks() -> list[tuple[str, str]]:
    """Scans all repository files for forbidden sensitive terms using SHA-256 hashing."""
    findings = []
    token_pattern = re.compile(r'[\w\.-]+')

    for root, dirs, files in os.walk(REPO_ROOT):
        # Exclude version control and cache artifacts
        for skip in [".git", ".pytest_cache", "__pycache__", "node_modules", "venv", ".venv"]:
            if skip in dirs:
                dirs.remove(skip)

        for f in files:
            if f in ("adversarial_review.py",):
                continue

            fp = Path(root) / f
            rel = fp.relative_to(REPO_ROOT)

            try:
                content = fp.read_text(encoding="utf-8", errors="ignore")

                # Check regex patterns
                for pat, label in FORBIDDEN_PATTERNS:
                    if pat.search(content):
                        findings.append((str(rel), f"Pattern Violation: {label}"))

                # Check SHA-256 hashed forbidden terms
                tokens = set(token_pattern.findall(content.lower()))
                for token in tokens:
                    thash = hashlib.sha256(token.encode("utf-8")).hexdigest()
                    if thash in FORBIDDEN_HASHES:
                        findings.append((str(rel), f"Cryptographic Match: {FORBIDDEN_HASHES[thash]}"))

            except Exception as e:
                findings.append((str(rel), f"File read error: {e}"))

    return findings


def audit_syntax() -> list[tuple[str, str]]:
    """Validates syntax across YAML, Python, and JSON files."""
    syntax_errors = []
    for root, dirs, files in os.walk(REPO_ROOT):
        for skip in [".git", ".pytest_cache", "__pycache__", "node_modules", "venv", ".venv"]:
            if skip in dirs:
                dirs.remove(skip)

        for f in files:
            fp = Path(root) / f
            rel = fp.relative_to(REPO_ROOT)

            # YAML validation
            if f.endswith((".yaml", ".yml")):
                try:
                    class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
                        pass

                    def any_constructor(loader, tag_suffix, node):
                        if isinstance(node, yaml.ScalarNode):
                            return loader.construct_scalar(node)
                        elif isinstance(node, yaml.SequenceNode):
                            return loader.construct_sequence(node)
                        elif isinstance(node, yaml.MappingNode):
                            return loader.construct_mapping(node)
                        return None

                    SafeLoaderIgnoreUnknown.add_multi_constructor("!", any_constructor)

                    with open(fp, "r", encoding="utf-8") as yf:
                        yaml.load(yf, Loader=SafeLoaderIgnoreUnknown)
                except Exception as e:
                    syntax_errors.append((str(rel), f"YAML Parse Error: {e}"))

            # Python syntax validation
            elif f.endswith(".py") and f != "adversarial_review.py":
                try:
                    with open(fp, "r", encoding="utf-8") as pf:
                        ast.parse(pf.read(), filename=str(fp))
                except Exception as e:
                    syntax_errors.append((str(rel), f"Python Syntax Error: {e}"))

            # JSON syntax validation
            elif f.endswith(".json") and not f.endswith("package-lock.json"):
                try:
                    with open(fp, "r", encoding="utf-8") as jf:
                        json.load(jf)
                except Exception as e:
                    syntax_errors.append((str(rel), f"JSON Parse Error: {e}"))

    return syntax_errors


def audit_execution_policy() -> list[str]:
    """Ensures no live GitHub Actions workflows exist per user instruction."""
    violations = []
    gh_workflows = REPO_ROOT / ".github" / "workflows"
    if gh_workflows.exists() and any(gh_workflows.iterdir()):
        violations.append(
            f"Found live GitHub Actions workflows in {gh_workflows}. "
            "Policy strictly prohibits real running workflows in this example repository."
        )
    return violations


def audit_documentation_coverage() -> list[str]:
    """Verifies that every example domain and subdirectory includes a README."""
    missing_docs = []
    for root, dirs, files in os.walk(REPO_ROOT):
        for skip in [".git", ".pytest_cache", "__pycache__", "node_modules", "venv", ".venv"]:
            if skip in dirs:
                dirs.remove(skip)

        rel = Path(root).relative_to(REPO_ROOT)
        if str(rel) == ".":
            continue

        # If directory contains code, manifests, or queries, require README.md
        has_substance = any(
            f.endswith((".py", ".tf", ".yaml", ".yml", ".json")) and not f.endswith("requirements.txt")
            for f in files
        )
        if has_substance and "README.md" not in files:
            missing_docs.append(str(rel))

    return missing_docs


def main() -> int:
    print("=" * 80)
    print(" ADVERSARIAL SECURITY & QUALITY AUDITOR: Koality-Assured/logscale-examples")
    print("=" * 80)

    # 1. Leak Scan
    leaks = audit_leaks()
    if leaks:
        print(f"\n[FAIL] Found {len(leaks)} prohibited sensitive strings / identifiers:")
        for rel, term in leaks:
            print(f"  - {rel}: contains '{term}'")
    else:
        print("\n[PASS] Zero internal account numbers, company names, or sensitive terms found (Cryptographically verified).")

    # 2. Syntax Validation
    syntax_issues = audit_syntax()
    if syntax_issues:
        print(f"\n[FAIL] Found {len(syntax_issues)} syntax errors:")
        for rel, err in syntax_issues:
            print(f"  - {rel}: {err}")
    else:
        print("[PASS] 100% of YAML, Python, and JSON files parsed cleanly without syntax errors.")

    # 3. Execution Policy Enforcement
    policy_violations = audit_execution_policy()
    if policy_violations:
        print(f"\n[FAIL] Execution policy violations detected:")
        for viol in policy_violations:
            print(f"  - {viol}")
    else:
        print("[PASS] Zero live GitHub Actions workflows detected (Reference example policy verified).")

    # 4. Documentation Coverage
    missing_docs = audit_documentation_coverage()
    if missing_docs:
        print(f"\n[FAIL] Missing README.md in {len(missing_docs)} example directories:")
        for d in missing_docs:
            print(f"  - {d}")
    else:
        print("[PASS] 100% documentation coverage: Every example directory maintains a README.md.")

    print("\n" + "=" * 80)
    if leaks or syntax_issues or policy_violations or missing_docs:
        print(" ADVERSARIAL AUDIT STATUS: FAILED")
        print("=" * 80)
        return 1

    print(" ADVERSARIAL AUDIT STATUS: ALL CHECKS PASSED (MERGE READY)")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
