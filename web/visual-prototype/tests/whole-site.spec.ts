import { test, expect } from "@playwright/test";
import { domainPages } from "../src/public/domainPages";
import { modules } from "../src/admin/modules";

for (const domain of domainPages) {
  test(`${domain.id} validates inputs and shows only an input summary`, async ({
    page,
  }) => {
    await page.goto("/" + domain.id);
    if (domain.fields.some((field) => field.id === "timezone")) {
      await expect(page.getByLabel("时区", { exact: true })).toHaveValue(
        "北京时间（UTC+8）",
      );
      await expect(page.getByLabel("时区", { exact: true })).toHaveAttribute(
        "readonly",
        "",
      );
      await expect(
        page.getByRole("combobox", { name: "时区", exact: true }),
      ).toHaveCount(0);
    }
    if (domain.id !== "yijing") {
      await page.getByRole("button", { name: "确认资料", exact: true }).click();
      await expect(
        page.getByRole("status", { name: "输入资料摘要" }),
      ).toHaveCount(0);
    }
    await page.getByRole("button", { name: "填入示例", exact: true }).click();
    await page.getByRole("button", { name: "确认资料", exact: true }).click();
    const summary = page.getByRole("status", { name: "输入资料摘要" });
    await expect(summary).toContainText("尚未计算");
    if (domain.fields.some((field) => field.id === "timezone"))
      await expect(summary).toContainText("北京时间（UTC+8）");
    if (domain.id === "liuyao")
      await expect(summary).toContainText("9 · 7 · 7 · 7 · 7 · 7");
    await page.getByRole("button", { name: "清空", exact: true }).click();
    await expect(summary).toHaveCount(0);
    if (domain.fields.some((field) => field.id === "timezone"))
      await expect(page.getByLabel("时区", { exact: true })).toHaveValue(
        "北京时间（UTC+8）",
      );
    if (domain.id === "fengshui")
      await expect(page.getByLabel("测量角度（°）")).toHaveValue("");
  });
}
test("birth data clears on domain navigation; lunar field follows selected calendar", async ({
  page,
}) => {
  await page.goto("/bazi");
  await page.getByLabel("历法", { exact: true }).selectOption("农历");
  await expect(page.getByLabel("农历月份", { exact: true })).toBeVisible();
  await page.getByLabel("历法", { exact: true }).selectOption("公历");
  await expect(page.getByLabel("农历月份", { exact: true })).toHaveCount(0);
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page
    .getByRole("navigation", { name: "工具切换" })
    .getByRole("link", { name: "星 紫微斗数", exact: true })
    .click();
  await expect(page.getByLabel("出生日期")).toHaveValue("");
  await page
    .getByRole("navigation", { name: "工具切换" })
    .getByRole("link", { name: "八 八字", exact: true })
    .click();
  await expect(page.getByLabel("出生日期")).toHaveValue("");
});
test("six lines require all six values; angle excludes 360 degrees", async ({
  page,
}) => {
  await page.goto("/liuyao");
  await page.getByRole("button", { name: "填入示例", exact: true }).click();
  await page.getByLabel("上爻", { exact: true }).selectOption("");
  await page.getByRole("button", { name: "确认资料", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("全部六个爻值");
  await expect(page.getByRole("status", { name: "输入资料摘要" })).toHaveCount(
    0,
  );
  await page.goto("/fengshui");
  await page.getByLabel("测量角度（°）").fill("360");
  await page.getByRole("button", { name: "确认资料", exact: true }).click();
  await expect(page.getByRole("status", { name: "输入资料摘要" })).toHaveCount(
    0,
  );
  await page.getByLabel("测量角度（°）").fill("0");
  await page.getByRole("button", { name: "确认资料", exact: true }).click();
  await expect(
    page.getByRole("status", { name: "输入资料摘要" }),
  ).toContainText("0");
});
test("mobile full chart reveals six spirits and branches without page overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 360, height: 844 });
  await page.goto("/liuyao/result");
  await expect(page.locator(".line-spirit").first()).toBeHidden();
  await page.getByRole("button", { name: "完整盘面", exact: true }).click();
  await expect(page.locator(".line-spirit").first()).toBeVisible();
  await expect(page.locator(".line-relative").last()).toContainText("甲子水");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});
for (const domain of domainPages.filter((d) => d.id !== "liuyao")) {
  test(`${domain.id} result states never fabricate computed values`, async ({
    page,
  }) => {
    await page.goto("/" + domain.id + "/result");
    await expect(page.locator(".template-state")).toContainText(
      "实际结果尚未接入",
    );
    await page.getByRole("button", { name: "计算中", exact: true }).click();
    await expect(page.locator(".template-state")).toContainText(
      "没有发起计算请求",
    );
    await page.getByRole("button", { name: "计算失败", exact: true }).click();
    await expect(page.locator(".template-state")).toContainText("不展示旧盘面");
  });
}
for (const module of modules.filter((item) => item.id !== "conflicts")) {
  test(`admin ${module.id} filters records, opens details and switches review views`, async ({
    page,
  }) => {
    await page.goto("/admin/" + module.id);
    const rows = page.locator(".module-table tbody tr").last();
    await expect(rows).toBeVisible();
    await page
      .getByLabel("搜索" + module.title, { exact: true })
      .fill("no-match");
    await expect(
      page.getByText("没有匹配的演示记录", { exact: true }),
    ).toBeVisible();
    await page.getByRole("button", { name: "清除筛选", exact: true }).click();
    await page.getByRole("link", { name: "详情", exact: true }).first().click();
    await expect(page.locator("main h1")).toHaveText(module.records[0].name);
    await page.getByRole("button", { name: "关联关系", exact: true }).click();
    await expect(page.locator(".module-relation")).toContainText("待服务返回");
    await page.getByRole("button", { name: "审核轨迹", exact: true }).click();
    await expect(page.locator("main")).toContainText("未发生发布");
    await page.setViewportSize({ width: 360, height: 844 });
    await page.reload();
    await expect(page.locator("main h1")).toHaveText(module.records[0].name);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  });
}
test("admin conflicts never requests internal assets before explicit authorization", async ({
  page,
}) => {
  const apiRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/admin/governance/conflicts"))
      apiRequests.push(request.url());
  });
  await page.goto("/admin/conflicts");
  await expect(page.getByRole("heading", { name: "流派与冲突", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "需要内部只读授权" })).toBeVisible();
  await expect(page.getByLabel("后台只读令牌")).toHaveAttribute("type", "password");
  await expect(page.locator("main")).toContainText("未授权时不返回任何内部冲突记录");
  expect(apiRequests).toEqual([]);
});

test("admin chapters never requests internal assets before explicit authorization", async ({
  page,
}) => {
  const apiRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/admin/governance/chapters"))
      apiRequests.push(request.url());
  });
  await page.goto("/admin/chapters");
  await expect(page.getByRole("heading", { name: "章节管理", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "需要内部只读授权" })).toBeVisible();
  await expect(page.getByLabel("后台只读令牌")).toHaveAttribute("type", "password");
  await expect(page.locator("main")).toContainText("不会返回章节正文");
  expect(apiRequests).toEqual([]);
});

test("admin terms never requests internal assets before explicit authorization", async ({
  page,
}) => {
  const apiRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/admin/governance/terms"))
      apiRequests.push(request.url());
  });
  await page.goto("/admin/terms");
  await expect(page.getByRole("heading", { name: "术语管理", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "需要内部只读授权" })).toBeVisible();
  await expect(page.getByLabel("后台只读令牌")).toHaveAttribute("type", "password");
  await expect(page.locator("main")).toContainText("不返回来源章节正文");
  expect(apiRequests).toEqual([]);
});

test("admin sources never requests internal assets before explicit authorization", async ({
  page,
}) => {
  const apiRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/admin/governance/sources"))
      apiRequests.push(request.url());
  });
  await page.goto("/admin/sources");
  await expect(page.getByRole("heading", { name: "来源管理", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "需要内部只读授权" })).toBeVisible();
  await expect(page.getByLabel("后台只读令牌")).toHaveAttribute("type", "password");
  await expect(page.locator("main")).toContainText("不返回内部文件路径");
  expect(apiRequests).toEqual([]);
});

test("admin layers never requests internal assets before explicit authorization", async ({
  page,
}) => {
  const apiRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/admin/governance/layers"))
      apiRequests.push(request.url());
  });
  await page.goto("/admin/layers");
  await expect(page.getByRole("heading", { name: "RAW / Quarantine / Canonical", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "需要内部只读授权" })).toBeVisible();
  await expect(page.getByLabel("后台只读令牌")).toHaveAttribute("type", "password");
  await expect(page.locator("main")).toContainText("不会返回任何内部文件路径或隔离正文");
  expect(apiRequests).toEqual([]);
});

test("admin algorithms never requests contracts before explicit authorization", async ({
  page,
}) => {
  const apiRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/admin/governance/algorithms"))
      apiRequests.push(request.url());
  });
  await page.goto("/admin/algorithms");
  await expect(page.getByRole("heading", { name: "算法与 Variant", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "需要内部只读授权" })).toBeVisible();
  await expect(page.getByLabel("后台只读令牌")).toHaveAttribute("type", "password");
  await expect(page.locator("main")).toContainText("真实读取 Phase2 execution contracts");
  expect(apiRequests).toEqual([]);
});

test("admin provider never requests configuration before explicit authorization", async ({
  page,
}) => {
  const apiRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/admin/system/provider"))
      apiRequests.push(request.url());
  });
  await page.goto("/admin/providers");
  await expect(page.getByRole("heading", { name: "AI Provider / Model", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "需要内部只读授权" })).toBeVisible();
  await expect(page.getByLabel("后台只读令牌")).toHaveAttribute("type", "password");
  await expect(page.locator("main")).toContainText("不读取、不返回也不编辑 API Key");
  expect(apiRequests).toEqual([]);
});

test("admin prompts never requests registry before explicit authorization", async ({
  page,
}) => {
  const apiRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/admin/system/prompts"))
      apiRequests.push(request.url());
  });
  await page.goto("/admin/prompts");
  await expect(page.getByRole("heading", { name: "Prompt 版本", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "需要内部只读授权" })).toBeVisible();
  await expect(page.getByLabel("后台只读令牌")).toHaveAttribute("type", "password");
  await expect(page.locator("main")).toContainText("不再提供页面内假编辑器");
  expect(apiRequests).toEqual([]);
});

test("admin evaluations never requests fixtures before explicit authorization", async ({
  page,
}) => {
  const apiRequests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/v1/admin/system/evaluations"))
      apiRequests.push(request.url());
  });
  await page.goto("/admin/evaluations");
  await expect(page.getByRole("heading", { name: "Eval / Golden Cases", exact: true })).toBeVisible();
  await expect(page.getByRole("heading", { name: "需要内部只读授权" })).toBeVisible();
  await expect(page.getByLabel("后台只读令牌")).toHaveAttribute("type", "password");
  await expect(page.locator("main")).toContainText("不会伪造通过分数");
  expect(apiRequests).toEqual([]);
});

test("library filtering, empty favorites and favorite removal work across pages", async ({
  page,
}) => {
  await page.goto("/favorites");
  await expect(page.getByRole("heading", { name: "还没有收藏" })).toBeVisible();
  await page.goto("/history");
  await page.getByLabel("工具筛选").selectOption("八字");
  await expect(
    page.getByRole("heading", { name: "没有匹配的记录" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "清除筛选" }).click();
  await page.getByRole("button", { name: "收藏示例", exact: true }).click();
  await page
    .locator(".public-nav")
    .getByRole("link", { name: "收藏", exact: true })
    .click();
  await expect(page.locator(".journal-row")).toContainText("乾为天");
  await page.getByRole("button", { name: "取消收藏示例" }).click();
  await expect(page.getByRole("heading", { name: "还没有收藏" })).toBeVisible();
});
