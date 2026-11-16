// flip-default.mjs — сделать markdown дефолтным форматом для get_confluence_page.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
for (const line of fs.readFileSync(path.join(ROOT, ".opencode/.env"), "utf8").split("\n")) {
  const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
  if (m) process.env[m[1]] = m[2].replace(/^"|"$/g, "");
}
const TOOLS = path.join(path.resolve(process.env.QA_WORK_DIR || ROOT), ".opencode/mcp/mcp-jira-confluence/dist/tools.js");

function mustReplace(file, from, to) {
  const s = fs.readFileSync(file, "utf8");
  if (!s.includes(from)) { console.error("anchor not found:", from.slice(0, 70)); process.exit(2); }
  fs.writeFileSync(file, s.replace(from, to));
  console.log("patched:", to.length > 60 ? from.slice(0, 40) + " …" : from);
}

// 1) дефолт формата -> markdown
mustReplace(TOOLS,
  `const format = args?.format === "markdown" ? "markdown" : "storage";`,
  `const format = args?.format === "storage" ? "storage" : "markdown";`);

// 2) обновить описание схемы
mustReplace(TOOLS,
  `description: "Body format. 'storage' (default) returns Confluence storage-format HTML; 'markdown' returns the body converted to Markdown (smaller; recommended for large pages).",`,
  `description: "Body format. 'markdown' (default) returns the body converted to Markdown (smaller; recommended for large pages); 'storage' returns raw Confluence storage-format HTML.",`);

console.log("DONE: default format = markdown");
