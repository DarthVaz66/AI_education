// update3.mjs — (1) возвращать markdown сырым (без JSON), (2) доп. компактизация.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
for (const line of fs.readFileSync(path.join(ROOT, ".opencode/.env"), "utf8").split("\n")) {
  const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
  if (m) process.env[m[1]] = m[2].replace(/^"|"$/g, "");
}
const DIST = path.join(path.resolve(process.env.QA_WORK_DIR || ROOT), ".opencode/mcp/mcp-jira-confluence/dist");

function mustReplace(file, from, to) {
  const s = fs.readFileSync(file, "utf8");
  if (!s.includes(from)) { console.error("anchor not found in", path.basename(file)); process.exit(2); }
  fs.writeFileSync(file, s.replace(from, to));
  console.log("patched:", path.basename(file));
}

// 1) tools.js: markdown возвращаем как plain text (меньше на JSON-обёртку)
mustReplace(path.join(DIST, "tools.js"),
  `                    const pageResponse = await getConfluencePage(client, pageId, config.spaceKey, format);\n                    return {\n                        content: [\n                            {\n                                type: "text",\n                                text: JSON.stringify(pageResponse, null, 2),\n                            },\n                        ],\n                    };`,
  `                    const pageResponse = await getConfluencePage(client, pageId, config.spaceKey, format);\n                    return {\n                        content: [\n                            {\n                                type: "text",\n                                text: format === "markdown"\n                                    ? pageResponse.content\n                                    : JSON.stringify(pageResponse, null, 2),\n                            },\n                        ],\n                    };`);

// 2) html-to-md.js: убираем пустую строку ПОСЛЕ заголовков и ПОСЛЕ hr
const htmlToMd = `// PATCH (local): Confluence storage HTML -> compact Markdown, for large pages.
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
    return turndown.turndown(String(html))
        .split("\\n")
        .map((l) => l.replace(/[ \\t]+$/g, ""))
        .map((l) => l.replace(/^(\\s*)-\\s{2,}/, "$1- "))
        .filter((l, i, arr) => !(l === "" && arr[i - 1] === ""))
        .join("\\n")
        .replace(/\\n{2,}(?=\\s*[-*] )/g, "\\n")
        .replace(/\\n{2,}(?=\\s*\\d+\\. )/g, "\\n")
        .replace(/^(#{1,6} .*)\\n\\n/gm, "$1\\n")
        .replace(/\\n---\\n\\n/g, "\\n---\\n")
        .trim();
}
`;
fs.writeFileSync(path.join(DIST, "html-to-md.js"), htmlToMd);
console.log("updated: html-to-md.js");
