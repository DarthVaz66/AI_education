// update-html2md.mjs — ужать Markdown (компактные списки, без лишних пустых строк).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
for (const line of fs.readFileSync(path.join(ROOT, ".opencode/.env"), "utf8").split("\n")) {
  const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
  if (m) process.env[m[1]] = m[2].replace(/^"|"$/g, "");
}
const DIST = path.join(path.resolve(process.env.QA_WORK_DIR || ROOT), ".opencode/mcp/mcp-jira-confluence/dist");

const htmlToMd = `// PATCH (local): Confluence storage HTML -> Markdown, compacted, for large pages.
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
    const raw = turndown.turndown(String(html));
    return raw
        .split("\\n")
        .map((l) => l.replace(/[ \\t]+$/g, ""))
        .map((l) => l.replace(/^(\\s*)-\\s{2,}/, "$1- "))
        .filter((l, i, arr) => !(l === "" && arr[i - 1] === ""))
        .join("\\n")
        .trim();
}
`;
fs.writeFileSync(path.join(DIST, "html-to-md.js"), htmlToMd);
console.log("updated: html-to-md.js");
