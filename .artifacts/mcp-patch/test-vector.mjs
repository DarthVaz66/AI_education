// test-vector.mjs — проверить патч на реальной странице 2228226.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const REPO = path.resolve(process.env.QA_WORK_DIR || ROOT);
const VENDOR = path.join(REPO, ".opencode/mcp/mcp-jira-confluence");

// подгружаем .opencode/.env в process.env
for (const line of fs.readFileSync(path.join(REPO, ".opencode/.env"), "utf8").split("\n")) {
  const m = line.match(/^([A-Z0-9_]+)=(.*)$/);
  if (m) process.env[m[1]] = m[2].replace(/^"|"$/g, "");
}

const imp = (p) => import(pathToFileURL(path.join(VENDOR, p)).href);
const { loadConfig } = await imp("dist/config.js");
const { createConfluenceClient } = await imp("dist/client.js");
const { getConfluencePage } = await imp("dist/confluence.js");

const cfg = loadConfig();
const client = createConfluenceClient(cfg);

const storage = await getConfluencePage(client, "2228226", cfg.spaceKey, "storage");
const md = await getConfluencePage(client, "2228226", cfg.spaceKey, "markdown");

console.log("title:", storage.title, "| version:", storage.version);
console.log("storage bytes:", Buffer.byteLength(storage.content, "utf8"), "| format:", storage.contentFormat);
console.log("markdown bytes:", Buffer.byteLength(md.content, "utf8"), "| format:", md.contentFormat);
console.log("has REQ-01..REQ-22:", /REQ-22/.test(md.content));
console.log("has table (REQ-14):", /\|\s*libvirt \/ QMP error/.test(md.content));
console.log("has glossary:", /## Glossary/.test(md.content));
console.log("empty storage?:", storage.content.length === 0);
console.log("---- md head ----");
console.log(md.content.slice(0, 500));
