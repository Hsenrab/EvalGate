# Feature Specification: Azure Authentication Modes

**Feature Branch**: `005-azure-auth-modes`
**Created**: 2026-11-19
**Status**: Draft
**Input**: Feature 5, "Azure authentication modes", from [feature-breakdown.md](../../feature-breakdown.md), subject to [requirements.md](../../requirements.md) and the project constitution.

## User Scenarios & Testing

### User Story 1 - Choose Azure Authentication by Environment (Priority: P1)

As a demo user, I want the same generation and evaluation commands to work with
either an Azure OpenAI API key or Microsoft Entra authentication so that I can
use the credential method approved for my environment.

**Acceptance Scenarios**:

1. **Given** `AZURE_API_KEY` and the shared Azure endpoint settings are available,
   **When** the user runs the demo without Entra mode, **Then** ASSERT uses
   API-key authentication and the commands/config files remain unchanged.
2. **Given** `ASSERT_AZURE_USE_AAD=1` and a working local or managed
   `DefaultAzureCredential`, **When** the user runs the demo, **Then** ASSERT
   uses Entra authentication and the commands/config files remain unchanged.
3. **Given** credentials are missing or invalid, **When** a live command runs,
   **Then** it fails clearly without exposing credential values and tells the
   user to check the selected auth mode.

## Requirements

### Functional Requirements

- **FR-001**: The workflow MUST support Azure OpenAI API-key authentication
  through environment configuration.
- **FR-002**: The workflow MUST support Entra authentication through
  `ASSERT_AZURE_USE_AAD=1` and existing `DefaultAzureCredential` availability.
- **FR-003**: Auth selection MUST require no changes to generation, evaluation,
  or comparison JSON configurations and MUST reuse ASSERT/LiteLLM's existing
  credential handling, including ASSERT's `DefaultAzureCredential` fallback.
- **FR-004**: Entra mode MUST be selected when `ASSERT_AZURE_USE_AAD=1`.
  Otherwise `AZURE_API_KEY` MUST select key auth when present; with neither
  present, ASSERT MAY use its `DefaultAzureCredential` fallback. The README
  MUST explain this fallback and its failure modes clearly.
- **FR-005**: Credentials MUST remain in process environment variables or the
  ignored root `.env`; they MUST NOT be accepted in JSON config, tracked
  examples, logs, console output, or saved artifacts.
- **FR-006**: The README MUST provide separate placeholder-only setup examples
  for API key and Entra, a selection explanation, and one common credential
  failure troubleshooting path.
- **FR-007**: Any code/config change MUST be limited to what ASSERT cannot
  already handle. A new token provider, credential store, login flow, or
  authentication adapter is explicitly excluded unless upstream support is
  proven insufficient and separately approved.
- **FR-008**: Automated validation MUST remain provider-free and verify
  credential-field rejection and unchanged command/config behavior.
- **FR-009**: One bounded manual smoke generation SHOULD be recorded for each
  approved auth mode, with unrun modes clearly disclosed.

### Common Errors

- Neither an API key nor usable Entra identity is available.
- `ASSERT_AZURE_USE_AAD=1` is set but the environment has no usable Entra login.
- Neither explicit mode is configured, so ASSERT attempts its
  `DefaultAzureCredential` fallback and no identity source is available.
- A credential is placed in JSON configuration and is rejected.
- Endpoint or API version settings are missing or invalid.

## Success Criteria

- **SC-001**: Users can switch between documented API-key and Entra setups by
  changing environment variables only.
- **SC-002**: All generation, evaluation, and comparison configuration examples
  remain unchanged between auth modes and contain no credential values.
- **SC-003**: Missing or invalid credentials produce a clear non-secret error
  and no false completion marker.
- **SC-004**: The implementation introduces no custom authentication system and
  adds only the minimum code needed, if any, beyond ASSERT's supported auth path.

## Scope and Assumptions

- Features 1-4 are available and already keep credentials out of JSON.
- ASSERT 0.3.0 with the `azure-auth` extra owns Azure API-key and Entra
  credential handling.
- `DefaultAzureCredential` fallback is supported behavior, not an error. The
  feature adds clear guidance/errors around a failed credential chain.
- The supported selection is environment-based; no interactive auth picker,
  credential persistence, rotation, vault integration, or multi-tenant UI is
  included.
- Comparison remains offline and does not itself require Azure credentials.
