# Drift Summary

## Native
- Native generic operations: 0
- Live docs operations: 38
- Native spec operations: 41
- Guide-only aliases: 1
- Guide-only operations: 1
- Reference-only aliases: 1

## Docs vs Discovery
- Missing from discovery after version normalization: 36
- Extra in discovery after version normalization: 23

## SDK vs Native
- High-confidence SDK paths missing from docs: 2
- High-confidence SDK paths missing from native spec: 1

## Compat
- Compat generic operations: 0
- Google-documented compat operations: 9
- Upstream OpenAI operations: 148
- Gemini-only compat paths: 2
- Upstream-only compat paths: 141
- Upstream-only classification counts: {'documented_family_subset_gap': 10, 'legacy_openai_generation_surface': 2, 'openai_admin_surface': 51, 'openai_assistants_surface': 39, 'openai_audio_surface': 3, 'openai_evals_surface': 12, 'openai_files_uploads_surface': 9, 'openai_fine_tuning_surface': 9, 'openai_realtime_surface': 2, 'openai_responses_surface': 4}
- Upstream-only subset counts: {'likely_intentionally_unsupported_subset_gap': 8, 'not_applicable': 131, 'sdk_adjacent_undocumented_subset_gap': 2}

## Compat Watchlist
- GET /batches: Batch create and retrieve are already present in Google's compatibility story, so this adjacent operation is worth rechecking against future docs.
- POST /batches/{batch_id}/cancel: Batch create and retrieve are already present in Google's compatibility story, so this adjacent operation is worth rechecking against future docs.
