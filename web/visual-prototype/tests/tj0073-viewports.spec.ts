import {test,expect,type Page} from "@playwright/test";

/** 3 consumer result pages × 3 viewports. Genuine private backend only, synthetic data. */
const sizes=[
  {width:1440,height:900,label:"desktop"},
  {width:390,height:844,label:"mobile390"},
  {width:360,height:740,label:"mobile360"},
] as const;
const scenes=[
  {name:"question",route:"/ask",api:"/api/v1/public/execute",result:".live-result"},
  {name:"dream",route:"/dream-culture",api:"/api/v1/dream/culture",result:".dream-culture-results"},
  {name:"life",route:"/life-overview",api:"/api/v1/scenarios/public",result:".life-result"},
] as const;
async function prepare(page: Page, name: string) {
  if(name==="life"){
    await page.goto("/bazi-profile");
    await page.getByRole("button",{name:"填入示例"}).click();
    await page.getByRole("button",{name:"保存资料"}).click();
  }
  await page.goto(scenes.find(s=>s.name===name)!.route);
  if(name==="question"){
    await page.locator("textarea").first().fill("这件事我想如何理解？");
    for(let i=0;i<6;i++) await page.locator(".yao-input-list select").nth(i).selectOption("7");
  }else if(name==="dream"){
    await page.getByLabel("梦境叙述").fill("我梦见一条蛇咬住我的手");
  }else{
    await page.getByLabel("观察年份").fill("2027");
  }
}
for(const size of sizes){
  test.describe("TJ-007.3 "+size.label,()=>{
    test.use({viewport:{width:size.width,height:size.height}});
    for(const scene of scenes){
      test(scene.name+" real result screenshot",async({page})=>{
        await prepare(page,scene.name);
        const pending=page.waitForResponse(r=>new URL(r.url()).pathname===scene.api
          && r.request().method()==="POST",{timeout:40000});
        await page.locator('form button[type="submit"]').first().click();
        const response=await pending;
        expect(response.status()).toBe(200);
        const data=await response.json();
        if(scene.name==="question")expect(data.chart?.original?.name).toBeTruthy();
        if(scene.name==="dream"){
          expect(data.status).toBe("reviewed_cultural_matches");
          expect(data.matches.length).toBeGreaterThan(0);
          expect(data.ai_enabled).toBe(false);
        }
        if(scene.name==="life"){
          expect(data.result?.integration_provenance?.all_natal_charts_identical).toBe(true);
          expect(data.result?.integration_provenance?.all_target_years_identical).toBe(true);
        }
        await expect(page.locator(scene.result)).toBeVisible();
        await expect.poll(()=>page.evaluate(()=>
          document.documentElement.scrollWidth<=document.documentElement.clientWidth)).toBe(true);
        await page.screenshot({path:"test-results/tj0073-"+scene.name+"-"+size.label+".png",
          fullPage:true,animations:"disabled"});
      });
    }
  });
}
