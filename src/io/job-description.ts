import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { AppError } from "../core/errors.js";

export async function readJobDescription(jdPath: string): Promise<string> {
  const absolutePath = path.resolve(jdPath);
  let fileStat: Awaited<ReturnType<typeof stat>>;
  try {
    fileStat = await stat(absolutePath);
  } catch {
    throw new AppError("JD_NOT_FOUND", `找不到 JD 文件：${absolutePath}`);
  }
  if (!fileStat.isFile()) {
    throw new AppError("JD_NOT_A_FILE", `指定的 JD 路径不是文件：${absolutePath}`);
  }

  let content: string;
  try {
    content = await readFile(absolutePath, "utf8");
  } catch (cause) {
    throw new AppError("JD_READ_FAILED", `无法读取 JD 文件：${absolutePath}`, { cause });
  }
  if (!content.trim()) {
    throw new AppError("JD_EMPTY", `JD 文件为空：${absolutePath}`);
  }
  return content.trim();
}
