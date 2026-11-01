# Spec Delta

## ADDED Requirements

### Requirement: Optional 1Password secret loading
Deployment SHALL offer `onepassword-enabled` defaulting to false. When enabled,
it SHALL resolve effective `DC_*` references using the 1Password configure and
load-secrets actions at v5.0.1 before generating .env. Authentication SHALL use
the inherited secret named by `onepassword-token-secret`, defaulting to
`ONEPASSWORD_SERVICE_ACCOUNT_TOKEN`; the token SHALL NOT be deployed.

#### Scenario: Optional retrieval enabled
- **WHEN** loading is enabled and a DC_* variable or secret contains a reference
- **THEN** the resolved value is written with literal-value escaping to .env before upload, including during dry-run

#### Scenario: Secret precedence
- **WHEN** a variable contains an op:// reference but a same-name secret holds an ordinary value
- **THEN** the secret wins before reference selection and its ordinary value is preserved

#### Scenario: Token override
- **WHEN** a caller selects another inherited token secret by name
- **THEN** both authentication and retrieval use that token

#### Scenario: Retrieval failure
- **WHEN** loading is enabled and the token is missing or a reference cannot be resolved
- **THEN** deployment fails before uploading files

#### Scenario: No references
- **WHEN** loading is enabled with a token but no effective DC_* reference exists
- **THEN** both 1Password actions are skipped and ordinary values are preserved

#### Scenario: Loading disabled
- **WHEN** loading is false or omitted
- **THEN** no 1Password action runs and existing environment generation behavior is preserved

