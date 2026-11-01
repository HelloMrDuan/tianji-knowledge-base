import { expect, test, type Page } from "@playwright/test";

// TJ-009.2 (E0364) — REAL-browser behavior tests for the WBS rule
// "进入后台停止音乐、离开后台不擅自重启" (entering the background stops the
// music; leaving the background never restarts it on its own).
//
// Test-nature disclosure: these tests run the real shipped MusicPlayer in
// real Chromium against the real dev server — clicks, the <audio> element,
// playback state and localStorage are all genuine, and no API is stubbed.
// The single simulated link is the browser's own visibility signal: a
// headless CI tab cannot be genuinely backgrounded on demand, so the test
// overrides document.visibilityState/document.hidden and dispatches the
// real "visibilitychange" event the shipped handler listens to. Nothing
// else about the behavior under test is simulated.

const preferenceKey = "tianji.prototype.music";

async function setVisibility(page: Page, state: "hidden" | "visible") {
  await page.evaluate((s) => {
    Object.defineProperty(document, "visibilityState", {
      value: s,
      configurable: true,
    });
    Object.defineProperty(document, "hidden", {
      value: s === "hidden",
      configurable: true,
    });
    document.dispatchEvent(new Event("visibilitychange"));
  }, state);
}

async function audioState(page: Page) {
  return page.locator("audio").evaluate((audio: HTMLAudioElement) => ({
    paused: audio.paused,
    currentTime: audio.currentTime,
  }));
}

async function savedPreferences(page: Page) {
  return page.evaluate(
    (key) => JSON.parse(localStorage.getItem(key) || "{}"),
    preferenceKey,
  );
}

async function startPlayback(page: Page) {
  await page.goto("/");
  expect((await audioState(page)).paused).toBe(true);
  await page.getByRole("button", { name: "背景音乐设置" }).click();
  await page.getByRole("slider", { name: "背景音乐音量" }).fill("0.5");
  await page.getByRole("button", { name: "播放背景音乐" }).click();
  await expect
    .poll(async () => {
      const s = await audioState(page);
      return !s.paused && s.currentTime > 0;
    })
    .toBe(true);
  await page.getByRole("button", { name: "关闭音乐设置" }).click();
  await expect(
    page.getByRole("button", { name: "全局暂停音乐" }),
  ).toBeVisible();
}

test("playing music stops when the tab enters the background and never restarts on return", async ({
  page,
}) => {
  await startPlayback(page);
  expect(await savedPreferences(page)).toEqual({ volume: 0.5, optedIn: true });

  await setVisibility(page, "hidden");
  await expect.poll(async () => (await audioState(page)).paused).toBe(true);
  await expect(
    page.getByRole("button", { name: "全局暂停音乐" }),
  ).toHaveCount(0);
  // A tab switch is not the user's pause choice: the persisted preference
  // must be byte-identical after the visibility pause.
  expect(await savedPreferences(page)).toEqual({ volume: 0.5, optedIn: true });

  const frozenAt = (await audioState(page)).currentTime;
  await setVisibility(page, "visible");
  await page.waitForTimeout(500);
  const afterReturn = await audioState(page);
  expect(afterReturn.paused).toBe(true);
  expect(afterReturn.currentTime).toBe(frozenAt);

  // The user can still resume manually afterwards.
  await page.getByRole("button", { name: "背景音乐设置" }).click();
  await page.getByRole("button", { name: "播放背景音乐" }).click();
  await expect.poll(async () => (await audioState(page)).paused).toBe(false);
});

test("a manual pause is never overridden by a background/foreground cycle", async ({
  page,
}) => {
  await startPlayback(page);
  await page.getByRole("button", { name: "全局暂停音乐" }).click();
  await expect.poll(async () => (await audioState(page)).paused).toBe(true);
  expect(await savedPreferences(page)).toEqual({ volume: 0.5, optedIn: false });
  const frozenAt = (await audioState(page)).currentTime;

  await setVisibility(page, "hidden");
  await setVisibility(page, "visible");
  await page.waitForTimeout(500);
  const afterCycle = await audioState(page);
  expect(afterCycle.paused).toBe(true);
  expect(afterCycle.currentTime).toBe(frozenAt);
  expect(await savedPreferences(page)).toEqual({ volume: 0.5, optedIn: false });
});

test("a tab that never played stays silent through a background/foreground cycle", async ({
  page,
}) => {
  await page.goto("/");
  expect(await audioState(page)).toEqual({ paused: true, currentTime: 0 });
  await setVisibility(page, "hidden");
  await setVisibility(page, "visible");
  await page.waitForTimeout(500);
  expect(await audioState(page)).toEqual({ paused: true, currentTime: 0 });
});
