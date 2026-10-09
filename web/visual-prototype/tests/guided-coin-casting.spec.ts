import { test, expect } from "@playwright/test";

test("a newcomer can cast six real simulated three-coin throws before requesting the real Liuyao engine", async ({ page }) => {
  const requests: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname === "/api/v1/public/execute") {
      requests.push(request.postData() || "");
    }
  });
  await page.goto("/ask");
  const progress = page.getByRole("progressbar", { name: "起卦进度" });
  await expect(progress).toHaveAttribute("aria-valuenow", "0");
  await expect(page.getByRole("button", { name: "开始推演" })).toBeDisabled();
  await page.getByPlaceholder("例如：现在这个工作机会，我是否适合继续推进？").fill("这件事情下一步该怎样考虑？");
  await page.getByLabel("起卦日期").fill("2026-10-09");
  await page.getByLabel("起卦时间").fill("17:30");
  for (let round = 0; round < 6; round++) {
    const label = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"][round];
    await page.getByRole("button", { name: `掷第 ${round + 1} 次铜钱 · ${label}` }).click();
    await expect(progress).toHaveAttribute("aria-valuenow", String(round + 1));
    const select = page.getByRole("combobox", { name: `${label}结果` });
    await expect(select).toHaveValue(/^[6789]$/);
  }
  await expect(page.getByText("六爻已齐，可以查看真实排盘。")).toBeVisible();
  expect(requests).toHaveLength(0);
  await expect(page.getByRole("button", { name: "开始推演" })).toBeEnabled();
  await page.getByRole("button", { name: "开始推演" }).click();
  await expect(page.locator(".live-result")).toBeVisible();
  await expect(page.locator(".live-lines .live-line")).toHaveCount(6);
  expect(requests).toHaveLength(1);
  const body = JSON.parse(requests[0]);
  expect(body.domain).toBe("liuyao");
  expect(body.input.yao_values).toHaveLength(6);
  expect(body.input.yao_values.every((value: number) => [6, 7, 8, 9].includes(value))).toBe(true);
  expect(JSON.stringify(body)).not.toContain("这件事情");
});

test("manual six-line entry, reset and edit prevent premature or stale divination", async ({ page }) => {
  const requests: string[] = [];
  page.on("request", (request) => {
    if (new URL(request.url()).pathname === "/api/v1/public/execute") requests.push(request.postData() || "");
  });
  await page.goto("/ask");
  const prompt = page.getByPlaceholder("例如：现在这个工作机会，我是否适合继续推进？");
  await prompt.fill("我的工作选择有哪些不同方向？");
  await page.getByLabel("起卦日期").fill("2026-10-09");
  await page.getByLabel("起卦时间").fill("17:30");
  await page.getByRole("button", { name: "一次投完六次" }).click();
  await expect(page.getByRole("progressbar", { name: "起卦进度" })).toHaveAttribute("aria-valuenow", "6");
  await page.getByRole("button", { name: "重新起卦" }).click();
  await expect(page.getByRole("progressbar", { name: "起卦进度" })).toHaveAttribute("aria-valuenow", "0");
  const labels = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"];
  for (let i = 0; i < labels.length; i++) {
    await page.getByRole("combobox", { name: labels[i] + "结果" }).selectOption(i === 0 ? "9" : "7");
  }
  await expect(page.getByRole("progressbar", { name: "起卦进度" })).toHaveAttribute("aria-valuenow", "6");
  await page.getByRole("button", { name: "开始推演" }).click();
  await expect(page.locator(".live-result")).toBeVisible();
  expect(requests).toHaveLength(1);
  expect(JSON.parse(requests[0]).input.yao_values).toEqual([9, 7, 7, 7, 7, 7]);
  await page.getByRole("combobox", { name: "初爻结果" }).selectOption("");
  await expect(page.locator(".live-result")).toHaveCount(0);
  await expect(page.getByRole("button", { name: "开始推演" })).toBeDisabled();
  expect(requests).toHaveLength(1);
});

test("six-step guided casting fits mobile viewport", async ({ page }) => {
  await page.setViewportSize({ width: 360, height: 780 });
  await page.goto("/ask");
  await expect(page.getByRole("button", { name: "掷第 1 次铜钱 · 初爻" })).toBeVisible();
  await expect(page.getByRole("progressbar", { name: "起卦进度" })).toHaveAttribute("aria-valuenow", "0");
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
