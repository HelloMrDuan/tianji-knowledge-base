import { test, expect } from "@playwright/test";
import { domainPages } from "../src/public/domainPages";
import { modules } from "../src/admin/modules";

for (const domain of domainPages) {
  test(`${domain.id} validates inputs and shows only an input summary`, async ({
    page,
  }) => {
    await page.goto("/" + domain.id);
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
    if (domain.id === "liuyao")
      await expect(summary).toContainText("9 · 7 · 7 · 7 · 7 · 7");
    await page.getByRole("button", { name: "清空", exact: true }).click();
    await expect(summary).toHaveCount(0);
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
for (const module of modules) {
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
test("configuration previews and prompt drafts clear on reload and never request a service", async ({
  page,
}) => {
  const requests: string[] = [];
  page.on("request", (request) => {
    if (request.url().includes("/api/")) requests.push(request.url());
  });
  await page.goto("/admin/prompts");
  await page.getByLabel("指令内容").fill("DEMO review text");
  await page.getByRole("button", { name: "确认草稿预览" }).click();
  await expect(page.getByRole("status")).toContainText("仅当前页面");
  await page.reload();
  await expect(page.getByLabel("指令内容")).not.toHaveValue("DEMO review text");
  await page.goto("/admin/providers");
  await page.getByLabel("超时（毫秒）").fill("4000");
  await page.getByRole("button", { name: "确认配置预览" }).click();
  await expect(page.getByRole("status")).toContainText("未发送连接请求");
  await page.reload();
  await expect(page.getByLabel("超时（毫秒）")).toHaveValue("3000");
  expect(requests).toEqual([]);
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
