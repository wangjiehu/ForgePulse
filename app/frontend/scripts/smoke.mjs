import { existsSync, readFileSync, readdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { join } from "node:path";

const root = fileURLToPath(new URL("..", import.meta.url));
const distDir = join(root, "dist");
const indexPath = join(distDir, "index.html");

const requiredLabels = [
  "ForgePulse",
  "Agent \u51b3\u7b56\u8f68\u8ff9",
  "\u6839\u56e0\u4e0e\u4f34\u968f\u56e0\u7d20",
  "\u539f\u59cb\u8bc1\u636e",
  "\u5904\u7f6e\u65b9\u6848\u4e0e\u5de5\u5355",
  "\u8bca\u65ad\u56e0\u679c\u8bc1\u636e\u7f51\u7edc\u56fe",
  "\u8bc1\u636e\u4e0d\u8db3",
  "\u8bc1\u636e\u51b2\u7a81",
  "\u5bfc\u51fa\u62a5\u544a",
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
