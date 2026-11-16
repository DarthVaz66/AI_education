// apply-patch.mjs — применить патч format=markdown к вендоренной копии mcp-jira-confluence.
// Автор: .artifacts (разрешённая зона записи). Запуск: node .artifacts/mcp-patch/apply-patch.mjs
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

// Рабочий каталог берём из переменной окружения QA_WORK_DIR (.opencode/.env) — без хардкода пути.
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
for (const line of fs.readFileSync(path.join(ROOT, ".opencode/.env"), "utf8").split("\n")) {
  const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
  if (m) process.env[m[1]] = m[2].replace(/^"|"$/g, "");
}
const REPO = path.resolve(process.env.QA_WORK_DIR || ROOT);
const VENDOR = path.join(REPO, ".opencode/mcp/mcp-jira-confluence");
const DIST = path.join(VENDOR, "dist");

function fail(msg) { console.error("PATCH-FAIL:", msg); process.exit(2); }
function mustReplace(file, from, to) {
  const src = fs.readFileSync(file, "utf8");
  if (!src.includes(from)) fail(`anchor not found in ${path.basename(file)}:\n${from.slice(0,80)}...`);
  const out = src.replace(from, to);
  fs.writeFileSync(file, out);
  console.log("patched:", path.basename(file));
}

// 1) html-to-md.js
const htmlToMd = `// PATCH (local): Confluence storage HTML -> Markdown, for large pages.
import TurndownService from "turndown";
import { gfm } from "turndown-plugin-gfm";

const turndown = new TurndownService({
    headingStyle: "atx",
    hr: "---",
    bulletListMarker: "-",
    codeBlockStyle: "fenced",
});
turndown.use(gfm);

export function convertHtmlToMarkdown(html) {
    if (html === null || html === undefined) return "";
    return turndown.turndown(String(html));
}
`;
fs.writeFileSync(path.join(DIST, "html-to-md.js"), htmlToMd);
console.log("wrote: html-to-md.js");

// 2) confluence.js
const conf = path.join(DIST, "confluence.js");
mustReplace(conf,
  `import { convertMarkdownToHtml } from "./markdown.js";`,
  `import { convertMarkdownToHtml } from "./markdown.js";\nimport { convertHtmlToMarkdown } from "./html-to-md.js";`);
mustReplace(conf,
  `export async function getConfluencePage(client, pageId, spaceKey) {`,
  `export async function getConfluencePage(client, pageId, spaceKey, format = "storage") {`);
mustReplace(conf,
  `        content: data.body?.storage?.value ?? "",\n    };\n}`,
  `        contentFormat: format === "markdown" ? "markdown" : "storage",\n        content: format === "markdown"\n            ? convertHtmlToMarkdown(data.body?.storage?.value ?? "")\n            : (data.body?.storage?.value ?? ""),\n    };\n}`);

// 3) tools.js — schema + handler
const tools = path.join(DIST, "tools.js");
mustReplace(tools,
  `                            pageId: {\n                                type: "string",\n                                description: "The ID of the Confluence page to read.",\n                            },`,
  `                            pageId: {\n                                type: "string",\n                                description: "The ID of the Confluence page to read.",\n                            },\n                            format: {\n                                type: "string",\n                                enum: ["storage", "markdown"],\n                                description: "Body format. 'storage' (default) returns Confluence storage-format HTML; 'markdown' returns the body converted to Markdown (smaller; recommended for large pages).",\n                            },`);
mustReplace(tools,
  `                    const pageResponse = await getConfluencePage(client, pageId, config.spaceKey);`,
  `                    const format = args?.format === "markdown" ? "markdown" : "storage";\n                    const pageResponse = await getConfluencePage(client, pageId, config.spaceKey, format);`);

// 4) opencode.json — switch jira-confluence to local patched server
const ocPath = path.join(REPO, "opencode.json");
mustReplace(ocPath,
  `      "command": ["npx", "-y", "mcp-jira-confluence"],`,
  `      "command": ["node", "{env:QA_WORK_DIR}.opencode/mcp/mcp-jira-confluence/dist/index.js"],`);

console.log("DONE: patch applied");
