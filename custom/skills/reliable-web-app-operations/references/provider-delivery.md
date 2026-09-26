# Provider Delivery

## Model Outcomes Explicitly

An external request can be:

- not attempted;
- rejected locally because configuration or input is invalid;
- accepted by the provider with a provider reference;
- delivered or completed, usually from a webhook or provider status API;
- failed after acceptance;
- unknown because confirmation is unavailable.

Do not collapse `accepted` into `delivered`, `paid`, `uploaded`, or `completed`.

## Integration Checklist

1. Verify the customer's actual account capability, approved product, region, sender/domain/template, and credential type.
2. Read official provider documentation for the selected product, not a similarly named API.
3. Validate configuration at startup or before the action with an actionable error.
4. Send the real application payload through the normal SDK/API path.
5. Persist provider, reference, channel, attempt, result, and safe error class.
6. Define timeout, retry, idempotency, webhook verification, and reconciliation behavior.
7. Expose channel-level results to operators; partial success is not full success.
8. Test rejected, accepted, delayed, duplicate, and unavailable-provider paths.

When several delivery channels carry the same onboarding credential, generate it once for that authorized delivery attempt. A channel failure must not silently regenerate it and invalidate a credential already sent elsewhere. Preserve the product's expiry, retry, rotation and invalidation rules; provider acceptance is still not delivery.

