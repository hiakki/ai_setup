// The pinned Playwright downloader sets its timeout after connecting. Node's
// global agent can time out first (5s), before IPv6-to-IPv4 fallback finishes.
// Preload only for browser installation; forked download workers inherit it.
// Keep the provider's TLS, proxy, address selection and extraction behavior.
const timeout = Number(process.env.PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT || 300000);
if (Number.isFinite(timeout) && timeout >= 0) {
  require('node:http').globalAgent.options.timeout = timeout;
  require('node:https').globalAgent.options.timeout = timeout;
}
