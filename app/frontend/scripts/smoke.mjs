import { existsSync, readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const root = fileURLToPath(new URL("..", import.meta.url));
const distDir = join(root, "dist");
const indexPath = join(distDir, "index.html");

const requiredLabels = [
  "ForgePulse",
  "Agent 决策轨迹",
  "根因与伴随因素",
  "原始证据",
  "处置方案与工单",
  "诊断因果证据网络图",
  "证据不足",
  "证据冲突",
  "导出报告",
];

function fail(message) {
  console.error(`smoke failed: ${message}`);
  process.exit(1);
}

if (!existsSync(indexPath)) {
  fail("dist/index.html is missing; run npm run build first");
}

const indexHtml = readFileSync(indexPath, "utf8");
const jsAssets = [...indexHtml.matchAll(/src="([^"]+\.js)"/g)].map((match) => match[1]);
const cssAssets = [...indexHtml.matchAll(/href="([^"]+\.css)"/g)].map((match) => match[1]);

if (jsAssets.length === 0) {
  fail("no JavaScript asset is referenced by dist/index.html");
}

if (cssAssets.length === 0) {
  fail("no CSS asset is referenced by dist/index.html");
}

for (const asset of [...jsAssets, ...cssAssets]) {
  const assetPath = join(distDir, asset.replace(/^\//, ""));
  if (!existsSync(assetPath)) {
    fail(`referenced asset is missing: ${asset}`);
  }
}

const assetDir = join(distDir, "assets");
const bundleText = readdirSync(assetDir)
  .filter((name) => name.endsWith(".js"))
  .map((name) => readFileSync(join(assetDir, name), "utf8"))
  .join("\n");

for (const label of requiredLabels) {
  if (!bundleText.includes(label)) {
    fail(`required UI label is missing from built bundle: ${label}`);
  }
}

console.log("frontend smoke passed");
