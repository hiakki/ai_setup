// Copy/adapt in the authorized app; use its pinned Playwright and axe packages.
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('representative screen: usable, accessible, visually stable', async ({ page }) => {
  await page.goto('/'); // Use the app's Playwright baseURL and a real key route.
  await expect(page.getByRole('main')).toBeVisible();
  const accessibility = await new AxeBuilder({ page }).analyze();
  expect(accessibility.violations).toEqual([]);
  await expect(page).toHaveScreenshot('representative-screen.png', {
    animations: 'disabled', fullPage: true,
  });
});

test('mobile content fits and reduced motion is supported', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.goto('/');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await expect(page.getByRole('main')).toBeVisible();
  // Add the app's primary keyboard workflow and motion-specific assertions here.
});
