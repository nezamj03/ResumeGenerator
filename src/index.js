import puppeteer from "puppeteer";
import * as fs from "fs";

const login = {
  EMAIL: "mjaz@mit.edu",
  PASSWORD: "ifwuLP6VF=SX_)D",
};

const selectors = {
  EMAIL: "#session_key",
  PASSWORD: "#session_password",
  LOGIN: '[data-id="sign-in-form__submit-btn"]',
  SHOW_ALL_EXP: "#navigation-index-see-all-experiences",
  EACH_EXP: "section > div > div > div > ul > li",
  MAIN_PAGE: "#voyager-feed",
  PROFILE_CONTENT: "#profile-content",
  SEARCH: "div > h2",
};

async function startBrowser() {
  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: false,
  });
  const page = await browser.newPage();
  return { browser, page };
}

async function closeBrowser(browser) {
  await browser.close();
}

async function signIn(page) {
  await page.focus(selectors.EMAIL);
  await page.keyboard.type(login.EMAIL);
  await page.focus(selectors.PASSWORD);
  await page.keyboard.type(login.PASSWORD);
  try {
    const [res] = await Promise.all([
      page.waitForNavigation(),
      page.click(selectors.LOGIN),
    ]);
  } catch (error) {
    console.log(`login failed`);
    return;
  }
}

function queryStringByPage(page) {
  return `http://www.linkedin.com/search/results/people/?keywords=data%20scientist&network=%5B%22O%22%5D&page=${page}`;
}

async function scrapePerson(page) {
  try {
    const url = `${await page.url()}/details/experience`;
    await page.goto(url);
    await page.waitForSelector(selectors.EACH_EXP);
    const res = await page.$$eval(selectors.EACH_EXP, (experiences) =>
      experiences.map((exp) => exp.innerText)
    );
    await page.goBack();
    return res;
  } catch (error) {
    return [];
  }
}

async function simulate(url, path) {
  const { browser, page } = await startBrowser();
  page.setDefaultTimeout(15000);
  await page.goto(url);
  await signIn(page);
  await page.waitForSelector(selectors.MAIN_PAGE);
  const pages = Array.from(Array(95).keys())
    .slice(1)
    .map((page) => queryStringByPage(page));

  for (const pageUrl of pages) {
    await page.goto(pageUrl);
    await page.waitForSelector(selectors.SEARCH);
    for (let i of Array.from(Array(10).keys()).slice(1)) {
      try {
        await page.click(`div > div > ul > li:nth-child(${i})`);
        await page.waitForSelector(selectors.PROFILE_CONTENT);
        const person = await scrapePerson(page);
        await write(person, path);
        await page.goBack();
        await page.waitForSelector(selectors.SEARCH);
      } catch (error) {
        await page.keyboard.press("Escape");
      }
    }
  }
  closeBrowser(browser);
}

async function write(resume, path) {
  const content = JSON.stringify(resume);
  if (!fs.existsSync(path)) {
    fs.writeFile(path, content, "utf8", function (err) {
      if (err) {
        console.log(err);
      }
    });
  } else {
    fs.appendFile(path, `, ${content}`, (err) => {
      if (err) {
        console.log(err);
      }
    });
  }
}

(async () => {
  await simulate("https://linkedin.com/", "SWE_1.json");
})();
