// start-test.mjs — проверить, что локальный пропатченный MCP стартует с env из .opencode/.env.
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL, fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const REPO = path.resolve(process.env.QA_WORK_DIR || ROOT);
const V = REPO + "/.opencode/mcp/mcp-jira-confluence";

for (const l of fs.readFileSync(REPO + "/.opencode/.env", "utf8").split("\n")) {
  const m = l.match(/^([A-Z0-9_]+)=(.*)$/);
  if (m) process.env[m[1]] = m[2].replace(/^"|"$/g, "");
}

let started = false;
setTimeout(() => { console.log(started ? "SERVER STARTED OK (no crash)" : "SERVER DID NOT START"); process.exit(0); }, 2000);

process.on("uncaughtException", (e) => { console.log("CRASH:", e.message); process.exit(3); });

await import(pathToFileURL(V + "/dist/index.js").href);
started = true;
console.log("import resolved, server bootstrap ran");
