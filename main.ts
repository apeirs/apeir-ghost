import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const botDir = process.env.MAKEFUN_BOT_DIR ?? "/bot";
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

try {
  mkdirSync(outDir, { recursive: true });
  const dest = join(outDir, "LAUNCH.json");
  copyFileSync(join(botDir, "LAUNCH.json"), dest);
  const launch = JSON.parse(readFileSync(dest, "utf8"));
  for (const key of ["mint", "create_signature"]) {
    if (typeof launch?.[key] !== "string" || launch[key] === "") throw new Error(`LAUNCH.json is missing "${key}"`);
  }
} catch (err) {
  console.error(`could not copy LAUNCH.json from ${botDir} to ${outDir}: ${(err as Error).message}`);
  process.exit(1);
}
