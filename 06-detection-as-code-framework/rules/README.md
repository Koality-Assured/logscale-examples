# Sigma Detection Rules (Single Source of Truth)

Canonical detection rules authored in generic [Sigma](https://github.com/SigmaHQ/sigma) specification format.

## Rule Catalog

- [`aws-cloudtrail-root-login.yaml`](./aws-cloudtrail-root-login.yaml): Detects console logins using the AWS Root account credentials.
- [`okta-mfa-fatigue-attack.yaml`](./okta-mfa-fatigue-attack.yaml): Detects >= 3 rejected Okta MFA push prompts within 10 minutes.
- [`github-repo-made-public.yaml`](./github-repo-made-public.yaml): Detects when a repository's visibility is changed from private to public.
