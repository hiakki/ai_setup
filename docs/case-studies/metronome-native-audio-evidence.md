# musician-metronome-macos: a native fallback still needs an audible test

Reviewed: 28 September 2026. Search terms: musician-metronome-macos, native audio,
platform capability, fallback, native module, build integration, audible verification.

The local repair note describes replacing an unavailable browser-style audio
path with a native system-sound module. It lists newly created native files, then
asks the operator to add them to the build if needed, rebuild and test sound.
The associated test guide contains procedures and expected console messages;
it is not a completed test report. No native build or listening test was run for
this central review.

## Reusable reasoning

| Earlier assumption / missing evidence | Better decision and acceptance gate |
| --- | --- |
| A browser implementation would transfer to another runtime unchanged. | Verify the target platform's actual capability before selecting an adapter. Keep platform behavior explicit instead of treating API names as portability proof. |
| Creating native source files completed the integration. | Verify target membership, successful compilation, module registration and invocation through the real app. Existence of a file or import does not establish a working binary. |
| A successful callback or log established audible output. | Verify output on the intended device/path and the user-facing result. Silence may involve routing, device, volume or implementation; do not infer one cause from a success log. |
| A system beep satisfied a metronome's original sound contract. | Test the actual timing, accent, pitch/duration and volume requirements. A fallback may have reduced capabilities; label that difference before accepting it. |

These are evidence gates derived from an incomplete repair record, not a claim
that the native fallback was successful or a recommendation for a particular
audio API today. Recheck current platform documentation before implementing one.
No extra native skill is needed; use the existing platform specialist and
workflow verification guidance for the target task.

## Source identities

Source directory `musician-metronome-macos` had no Git repository. Both documents
were read directly. Their content hashes identify the reviewed notes, not a build:

| Source | SHA-256 |
| --- | --- |
| `AUDIO_FIX.md` | `35856743c5fc9397c58e33dd263966df0005bda086acc88bd0c1ebe71b6a08d2` |
| `TEST_AUDIO.md` | `2bb569003881c220c317902b5a84276e9c52ddd4151310b9e33ea8d10f976d85` |

Search `ai-setup search "metronome audio"`; compare this with the
[NarrateAI audio audition](narrateai-automation-and-evidence.md#audio-experiment-follow-up)
for the distinction between functional output and subjective quality approval.
Keep any new target's implementation, listening observations and timing evidence
in its own project docs.
