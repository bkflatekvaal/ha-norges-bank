# Marketplace publication

Reviewed against the current upstream documentation on 2026-11-27:

- [Catalog submission](https://contributors.home-assistant.io/marketplace/guides/catalog/)
- [Validation checks](https://contributors.home-assistant.io/marketplace/reference/validation/)
- [Custom integrations](https://contributors.home-assistant.io/marketplace/guides/integrations/)
- [Brand image specifications](https://github.com/home-assistant/brands#image-specification)

## Validation status

The [2026-11-26 validation run](https://github.com/bkflatekvaal/ha-norges-bank/actions/runs/45778935424)
passed all three jobs on commit `78cb8a57f41df16742053952e38a7eb07a0c634c`:

- [Hassfest](https://github.com/bkflatekvaal/ha-norges-bank/actions/runs/45778935424/job/139769362236)
- [Marketplace repository validation](https://github.com/bkflatekvaal/ha-norges-bank/actions/runs/45778935424/job/139769362525), without ignored checks
- [Tests and lint](https://github.com/bkflatekvaal/ha-norges-bank/actions/runs/45778935424/job/139769362502)

These results cover the published code, not subsequent local changes. After
pushing changes, use the new successful run as submission evidence. The workflow
uses `home-assistant/actions/hassfest@master` (which runs the published hassfest
container) and `hacs/action@main`, following the current validation guide. Tests
currently target the minimum supported Home Assistant version, 2026.8.0; a green
test job does not establish runtime compatibility with every newer version.

`hacs.json`, `hacs/action`, and `hacs/default` are still the required upstream
technical names for Marketplace metadata, validation, and catalog submission.
Do not rename these to hypothetical Marketplace equivalents.

## Repository checks

- One integration in `custom_components/norges_bank`, with its runtime files,
  English and Norwegian translations, and local brand images.
- Manifest has the required identity, version, documentation, issue tracker,
  and code owner fields. Version `0.1.3` matches the planned `v0.1.3` release tag
  and `Norges Bank v0.1.3` release title.
- Root `hacs.json` specifies the name and minimum supported Home Assistant.
- Public, non-archived repository, with description, topics, issues, README,
  MIT license, and full GitHub releases.
- No `norges_bank` domain found in the current core integration tree.
- Not in the shared catalog; no matching submission found in the catalog's
  issues and pull requests at the review date.
- `categories` is optional. It was removed in v0.1.2 after a validator failure.
  Current documentation supports categories, including Finance, but adding it
  back should be verified against the published hassfest container before release.

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

## Submission checklist

1. Push the prepared changes and confirm all three validation jobs pass without
   any `ignore` option. Keep links to the successful jobs.
2. For a new release, update the manifest and project version together, update
   the changelog, and publish a full GitHub release after validation. A tag alone
   is insufficient. A full [v0.1.2 release](https://github.com/bkflatekvaal/ha-norges-bank/releases/tag/v0.1.2)
   already exists, but does not include these documentation changes.
3. Recheck the catalog and pending submissions before opening a new pull request.
4. From the owner's personal account, fork `hacs/default`, create a branch from
   `master`, and add `bkflatekvaal/ha-norges-bank` in alphabetical order to the
   JSON list in `integration`.
5. Complete the upstream pull request template, including the release and
   successful validation links. Submit as the owner or a major contributor.

Catalog acceptance requires upstream review. Until then, users can install using
the Marketplace custom-repository link in the README.
