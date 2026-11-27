# Marketplace publication

Reviewed against the current upstream documentation on 2026-11-27:

- [Catalog submission](https://contributors.home-assistant.io/marketplace/guides/catalog/)
- [Validation checks](https://contributors.home-assistant.io/marketplace/reference/validation/)
- [Custom integrations](https://contributors.home-assistant.io/marketplace/guides/integrations/)
- [HACS general requirements](https://www.hacs.xyz/docs/publish/start/)
- [HACS catalog requirements](https://www.hacs.xyz/docs/publish/include/)
- [HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/)
- [Catalog CI implementation](https://github.com/hacs/default/blob/master/.github/workflows/checks.yml)
- [Catalog PR template](https://github.com/hacs/default/blob/master/.github/PULL_REQUEST_TEMPLATE.md)
- [Brand image specifications](https://github.com/home-assistant/brands#image-specification)

## Validation status

The [v0.1.3 validation run](https://github.com/bkflatekvaal/ha-norges-bank/actions/runs/45957246646)
passed hassfest, repository validation, and all 30 tests on release commit
`85a148bea90916e22f3a9debc82e024bc462a027`. The release was published after
all jobs completed. Log inspection found no brand-image warnings, but repository
validation warned about missing integration categories.

The v0.1.4 changes restore `finance`, declare `country: NO`, and make brand-image
warnings fatal, matching the catalog's current admission workflow. The workflow
runs the same `ghcr.io/home-assistant/hassfest:latest` container as the upstream
hassfest action and catalog, plus `hacs/action@main`, with no ignored checks.
New successful run and release links must accompany submission.

Tests target the minimum supported Home Assistant version, 2026.8.0; a green
job does not establish runtime compatibility with every newer version.

`hacs.json`, `hacs/action`, and `hacs/default` are still the required upstream
technical names for Marketplace metadata, validation, and catalog submission.
Do not rename these to hypothetical Marketplace equivalents.

## Repository checks

- One integration in `custom_components/norges_bank`, with its runtime files,
  English and Norwegian translations, and local brand images.
- Manifest has the required identity, version, documentation, issue tracker,
  and code owner fields. Version `0.1.4` matches the `v0.1.4` release tag
  and `Norges Bank v0.1.4` release title.
- Root `hacs.json` specifies the name, minimum supported Home Assistant, and
  `country: NO`. Norway is the target market (NOK quotations and Norwegian policy
  rate); this metadata is not a claim that the public API is geoblocked.
- Public, non-archived repository, with description, topics, issues, README,
  GitHub-recognized OSI-approved MIT license, and full GitHub releases.
- No `norges_bank` domain in `https://next.home-assistant.io/integrations.json`,
  the exact upcoming-core source used by the catalog check.
- Repository absent from all seven catalog feeds and the removed-repositories
  feed at `https://data-v2.hacs.xyz/`.
- Not in the shared catalog; no matching submission found in the catalog's
  issues and pull requests at the review date.
- `finance` is a current category for currency exchange rates. Its previous
  omission triggered a warning in the v0.1.3 repository validation log.

Marketplace itself requires Home Assistant 2026.11 or later. This does not
require raising the integration's existing 2026.8.0 minimum. README exclusion
markers take effect in Marketplace from Home Assistant 2026.12 onward.

## Brand image audit

All eight files decode as 8-bit RGBA PNGs with transparency and are stored under
`custom_components/norges_bank/brand/`.

| File | Dimensions | Size | Result |
| --- | --- | --- | --- |
| `icon.png` | 256 x 256 | 2,767 bytes | Required square dimensions |
| `icon@2x.png` | 512 x 512 | 5,730 bytes | Required high-resolution dimensions |
| `logo.png` | 1044 x 256 | 16,375 bytes | Landscape; shortest side within 128–256 |
| `logo@2x.png` | 2088 x 512 | 36,881 bytes | Same aspect ratio; shortest side within 256–512 |
| `dark_icon.png` | 256 x 256 | 2,069 bytes | White; same alpha as the light-theme icon |
| `dark_icon@2x.png` | 512 x 512 | 4,699 bytes | White; same alpha as the light-theme icon |
| `dark_logo.png` | 1044 x 256 | 10,689 bytes | White; same alpha as the light-theme logo |
| `dark_logo@2x.png` | 2088 x 512 | 23,568 bytes | White; same alpha as the light-theme logo |

The images depict Norges Bank, with no Home Assistant branding. The icon artwork
fills the width; its approximately 7/14-pixel vertical margins preserve the
non-square mark within the required square canvas. Logos fill the height, with
only 1/2 transparent pixels at the right edge. No substantial surrounding padding
was found. PNG encoding is non-interlaced; interlacing is preferred, not required.

The `dark_` variants use white artwork for contrast on dark backgrounds. They
retain the exact dimensions and per-pixel alpha of their corresponding originals,
including anti-aliased edges. The original navy images remain unchanged for light
themes. Decoded output pixels were checked for white RGB and identical alpha.

## Lessons from previous submissions

All four PRs authored by `bkflatekvaal` in `hacs/default` were reviewed, including
issue comments, reviews, and inline-comment endpoints (no inline comments).

| Evidence | Lesson | Application here |
| --- | --- | --- |
| [SweTrack #10086](https://github.com/hacs/default/pull/10086#pullrequestreview-4957419029) and [Amina #11257](https://github.com/hacs/default/pull/11257#pullrequestreview-5304045939), closed without merge | Never submit from the fork's `master` branch | Use a dedicated `add-ha-norges-bank` branch based on upstream `master` |
| [SweTrack privacy review](https://github.com/hacs/default/pull/10087#pullrequestreview-5566460315) | Account identifiers can leak even when credentials are redacted | Diagnostics never dumps `entry.data` or `entry.options`; only public data and selected settings are exported. Regression coverage explicitly includes `account_id`, nested configuration, credentials, titles, identifiers, and raw error details |
| [SweTrack brand review](https://github.com/hacs/default/pull/10087#pullrequestreview-6080293192) | Unsupported SVGs and redundant fallback images block admission; warnings matter | Exactly eight supported PNG names, no SVG. White dark variants differ from navy originals; landscape logos differ from square icons. CI now fails on brand warnings |
| [SweTrack API-key review](https://github.com/hacs/default/pull/10087#pullrequestreview-6085611826) | Secret inputs must be masked in setup and reauthentication | Not applicable: this integration has no account or credential fields, only currency and policy-rate selectors |
| [Amina #11258 approval](https://github.com/hacs/default/pull/11258#pullrequestreview-5581925961) | Installation docs must reflect catalog inclusion | Keep custom-repository instructions until merge; then lead with searching for Norges Bank in Marketplace |
| [SweTrack queue instructions](https://github.com/hacs/default/pull/10087#issuecomment-5323921423) | Avoid duplicates, unsolicited review requests, and queue-bumping comments; drafts are outside the queue | Prepare one complete PR; address requested changes, publish fixes, refresh evidence, and mark ready after resolving a draft |

SweTrack #10087 and Amina #11258 were ultimately merged. Their approvals are
useful precedents, not a guarantee for this integration.

## Code review relevant to admission

- HTTP uses Home Assistant's shared asynchronous client session and fixed
  `https://data.norges-bank.no` endpoints, with certificate verification enabled
  by default. No credentials, user-supplied host, or disabled TLS checks.
- Requests have a 20-second timeout. Polling is coordinated every six hours.
- Setup uses config entries, first-refresh handling, typed runtime data, and
  platform unloading. Configuration uses selectors and ships English/Norwegian
  translations. No YAML setup or secret input fields are needed.
- Diagnostics uses an allowlist and reports exception class names rather than
  arbitrary exception strings. Public rate data is intentionally included.
- Existing tests cover parsing, setup, options, retries, sensors, and diagnostics.
  Review of these areas is not a claim of a complete security audit or HA quality
  scale certification.

## Submission checklist

1. Confirm the release commit passes all three jobs with no ignored checks and no
   brand-image warnings. Inspect logs, not only job conclusions.
2. Publish a full release after validation, with matching manifest/project
   version, `v<version>` tag, and `Norges Bank v<version>` title. Use links to that
   release and its successful validation jobs in the PR.
3. Recheck catalog membership, removed entries, core-domain conflicts, and
   pending submissions before opening a new PR.
4. From the owner's personal fork, create `add-ha-norges-bank` from current
   upstream `master`; add only `bkflatekvaal/ha-norges-bank` alphabetically to
   the JSON list in `integration`. Enable maintainer edits.
5. Fill the current upstream PR template completely. Do not request reviewers
   or send unsolicited follow-up comments. If maintainers draft the PR, resolve
   the reported issues and mark ready only when the fixes are released.
6. After merge, update README installation instructions to lead with searching
   for **Norges Bank** in Marketplace, retaining the link as a fallback.

Catalog acceptance requires upstream review. Until then, users can install using
the Marketplace custom-repository link in the README. A screenshot in the chat
shows the installed integration, but no end-to-end installation test against a
live Home Assistant instance was performed during this review.
