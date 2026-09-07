import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";

export function printJson(value: unknown): void {
  process.stdout.write(`${JSON.stringify(value, null, 2)}\n`);
}

export async function saveJson(value: unknown, outputPath?: string): Promise<void> {
  if (!outputPath) return;

  const absolutePath = path.resolve(outputPath);
  await mkdir(path.dirname(absolutePath), { recursive: true });
  await writeFile(absolutePath, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  process.stderr.write(`结果已保存到 ${absolutePath}\n`);
}
