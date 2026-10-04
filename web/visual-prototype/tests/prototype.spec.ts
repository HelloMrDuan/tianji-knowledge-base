import { test, expect } from "@playwright/test";
import { domainPages } from "../src/public/domainPages";
import { modules } from "../src/admin/modules";

const routes = [
  "/",
  "/liuyao/result",
  "/admin",
  "/admin/classics",
  "/admin/rules",
  "/admin/evidence",
  "/history",
  "/favorites",
  ...domainPages.map((page) => "/" + page.id),
  ...domainPages
    .filter((page) => page.id !== "liuyao")
    .map((page) => "/" + page.id + "/result"),
  ...modules.map((module) => "/admin/" + module.id),
];
for (const width of [1440, 390, 360]) {
  for (const route of routes) {
    test(`${route} renders within ${width}px without remote or API requests`, async ({
      page,
    }) => {
      await page.setViewportSize({ width, height: 900 });
      const errors: string[] = [];
      const forbiddenRequests: string[] = [];
      page.on("pageerror", (error) => errors.push(error.message));
      page.on("request", (request) => {
        const url = new URL(request.url());
        if (
          url.pathname.startsWith("/api/") ||
          (url.protocol.startsWith("http") && url.hostname !== "127.0.0.1")
        )
          forbiddenRequests.push(request.url());
      });
      await page.goto(route);
      await expect(page.locator("main h1")).toBeVisible();
      await page.evaluate(() => document.fonts.ready);
      expect(
        await page.evaluate(
          () => document.documentElement.scrollWidth <= innerWidth,
        ),
      ).toBe(true);
      expect(errors).toEqual([]);
      expect(forbiddenRequests).toEqual([]);
    });
  }
}

test("public tools and reserved paths cannot expose internal asset pages", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.locator(".tool-card")).toHaveCount(7);
  await expect(page.locator("input[type=search]")).toHaveCount(0);
  await expect(
    page.getByRole("link", { name: /知识库|RAW|Quarantine|Prompt|后台/ }),
  ).toHaveCount(0);
  await page
    .locator(".tool-card")
    .filter({ hasText: "八字" })
    .getByRole("link")
    .click();
  await expect(
    page.getByRole("heading", { name: "录入出生资料" }),
  ).toBeVisible();
  for (const path of [
    "/knowledge",
    "/raw",
    "/quarantine",
    "/evidence",
    "/prompt",
  ]) {
    await page.goto(path);
    await expect(
      page.getByRole("heading", { name: "回到推演的起点" }),
    ).toBeVisible();
    await expect(page.locator(".admin-sidebar, .asset-table")).toHaveCount(0);
  }
});

test("result hierarchy, collapsed process, related evidence and accessible detail", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/liuyao/result");
  expect(await page.locator(".result-content h2").allTextContents()).toEqual([
    "基础信息",
    "核心盘面",
    "核心结论",
    "规则命中",
    "典籍依据",
    "AI 解读",
  ]);
  await expect(page.locator(".trace-section")).not.toHaveAttribute("open", "");
  await expect(page.locator(".evidence-card")).toHaveCount(2);
  await expect(page.locator(".ai-section")).toContainText("暂未开放");
  await page.getByRole("button", { name: "初爻，动爻详情" }).click();
  await expect(page.getByRole("dialog")).toContainText("青龙");
  await expect(page.getByRole("dialog")).toContainText("甲子水");
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "初爻，动爻详情" }),
  ).toBeFocused();
  await page.getByRole("button", { name: "查看依据" }).first().click();
  await expect(page.getByRole("dialog")).toContainText("不提供“浏览更多原文”");
  await page.getByRole("button", { name: "关闭", exact: true }).click();
  await page.locator("summary").click();
  await expect(page.locator(".trace-section")).toHaveAttribute("open", "");
  await expect(page.locator(".trace-section li")).toHaveCount(5);
});

test("sample favorites persist locally and history stays labelled as example", async ({
  page,
}) => {
  await page.goto("/liuyao/result");
  await page.getByRole("button", { name: "收藏示例", exact: true }).click();
  await page.reload();
  await expect(page.getByRole("button", { name: "已收藏" })).toHaveAttribute(
    "aria-pressed",
    "true",
  );
  await page
    .locator(".public-nav")
    .getByRole("link", { name: "收藏", exact: true })
    .click();
  await expect(page.locator("main")).toContainText("乾为天");
  await page
    .locator(".public-nav")
    .getByRole("link", { name: "历史记录" })
    .click();
  await expect(page.locator("main")).toContainText("静态");
});

test("original music requires a gesture, persists volume, pauses globally and on admin transition", async ({
  page,
}) => {
  await page.goto("/");
  expect(
    await page
      .locator("audio")
      .evaluate((audio: HTMLAudioElement) => audio.paused),
  ).toBe(true);
  await page.getByRole("button", { name: "背景音乐设置" }).click();
  await page.getByRole("slider", { name: "背景音乐音量" }).fill("0.5");
  await page.getByRole("button", { name: "播放背景音乐" }).click();
  await expect
    .poll(() =>
      page
        .locator("audio")
        .evaluate(
          (audio: HTMLAudioElement) => !audio.paused && audio.currentTime > 0,
        ),
    )
    .toBe(true);
  await page.getByRole("button", { name: "关闭音乐设置" }).click();
  await page.getByRole("link", { name: "查看六爻示例" }).click();
  expect(
    await page
      .locator("audio")
      .evaluate((audio: HTMLAudioElement) => audio.paused),
  ).toBe(false);
  await page.getByRole("button", { name: "全局暂停音乐" }).click();
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          JSON.parse(localStorage.getItem("tianji.prototype.music") || "{}")
            .optedIn,
      ),
    )
    .toBe(false);
  expect(
    await page
      .locator("audio")
      .evaluate((audio: HTMLAudioElement) => audio.paused),
  ).toBe(true);
  await page.reload();
  expect(
    await page
      .locator("audio")
      .evaluate((audio: HTMLAudioElement) => audio.paused),
  ).toBe(true);
  await page.getByRole("button", { name: "背景音乐设置" }).click();
  await expect(page.getByRole("slider", { name: "背景音乐音量" })).toHaveValue(
    "0.5",
  );
  await page.getByRole("button", { name: "播放背景音乐" }).click();
  await expect(
    page.getByRole("button", { name: "全局暂停音乐" }),
  ).toBeVisible();
  await page.evaluate(() => {
    history.pushState({}, "", "/admin");
    dispatchEvent(new Event("tianji:navigation"));
  });
  await expect(page.locator(".admin-sidebar")).toBeVisible();
  await expect(page.locator("audio")).toHaveCount(0);
});

for (const kind of ["classics"]) {
  test(`admin ${kind} supports filtering, empty states and read-only details`, async ({
    page,
  }) => {
    await page.goto(`/admin/${kind}`);
    await expect(page.locator(".asset-table tbody tr")).toHaveCount(6);
    await page.getByRole("combobox", { name: "领域筛选" }).selectOption("六爻");
    expect(await page.locator(".asset-table tbody tr").count()).toBeGreaterThan(
      0,
    );
    await page.getByRole("textbox").fill("no-matching-record");
    await expect(page.getByText("没有匹配的示例记录")).toBeVisible();
    await page.getByRole("button", { name: "清除筛选" }).click();
    await expect(page.locator(".asset-table tbody tr")).toHaveCount(6);
    await page
      .getByRole("button", { name: "详情", exact: true })
      .first()
      .click();
    await expect(page.getByRole("dialog")).toContainText("DEMO-");
    await expect(page.getByRole("dialog")).toContainText("不提供编辑");
    await page.keyboard.press("Escape");
    await expect(
      page.locator(".ink-landscape, audio, .public-nav"),
    ).toHaveCount(0);
  });
}

test("real rules and evidence admin stay sealed until explicit authorization", async ({
  page,
}) => {
  for (const route of ["/admin/rules", "/admin/evidence"]) {
    const requests: string[] = [];
    const listener = (request: any) => {
      if (request.url().includes("/api/v1/admin/governance/"))
        requests.push(request.url());
    };
    page.on("request", listener);
    await page.goto(route);
    await expect(page.getByRole("heading", { name: route.endsWith("rules") ? "规则管理" : "Evidence 管理", exact: true })).toBeVisible();
    await expect(page.getByRole("heading", { name: "需要内部只读授权" })).toBeVisible();
    await expect(page.getByLabel("后台只读令牌")).toHaveAttribute("type", "password");
    expect(requests).toEqual([]);
    page.off("request", listener);
  }
});

test("mobile admin menu opens implemented Prompt workspace", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/admin");
  await page.getByRole("button", { name: "打开管理导航" }).click();
  await expect(
    page.getByRole("navigation", { name: "后台管理导航" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Prompt 版本", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Prompt 版本", exact: true }),
  ).toBeVisible();
  await expect(page.getByLabel("指令内容")).toBeVisible();
  await expect(page.locator(".admin-sidebar")).not.toHaveClass(/is-open/);
});
