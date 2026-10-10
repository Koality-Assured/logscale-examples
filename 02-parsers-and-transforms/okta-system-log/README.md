# Okta System Log Parser

Structures Okta identity and authentication events, extracting user identities, client geographic context, MFA outcomes, and target application names.

## Key Normalized Fields

- `Vendor.actor.alternateId`: Corporate email address (`alice.engineer@example.com`).
- `Vendor.eventType`: Primary event identifier (`user.authentication.sso`, `user.session.start`, `policy.evaluate_sign_on`).
- `source.ip`: Remote client IPv4/IPv6 address.
- `client.geo.city_name` & `country_name`: Origin geographic coordinates extracted by Okta.
- `Vendor.outcome.result`: Status bucket (`SUCCESS`, `FAILURE`, `DENY`, `CHALLENGE`).
