import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { PDFParse } from "pdf-parse";
import { AppError } from "../core/errors.js";

export interface ParsedPdf {
  source: string;
  pages: number;
  text: string;
}

export async function readPdfText(pdfPath: string): Promise<ParsedPdf> {
  const absolutePath = path.resolve(pdfPath);
  let fileStat: Awaited<ReturnType<typeof stat>>;

  try {
    fileStat = await stat(absolutePath);
  } catch {
    throw new AppError("PDF_NOT_FOUND", `找不到 PDF 文件：${absolutePath}`);
  }

  if (!fileStat.isFile()) {
    throw new AppError("PDF_NOT_A_FILE", `指定路径不是文件：${absolutePath}`);
  }
  if (path.extname(absolutePath).toLowerCase() !== ".pdf") {
    throw new AppError("NOT_PDF", `文件不是 PDF：${absolutePath}`);
  }

  let buffer: Buffer;
  try {
    buffer = await readFile(absolutePath);
  } catch (cause) {
    throw new AppError("PDF_READ_FAILED", `无法读取 PDF 文件：${absolutePath}`, { cause });
  }

  if (buffer.length === 0) {
    throw new AppError("PDF_READ_FAILED", `PDF 文件为空：${absolutePath}`);
  }

  let parser: PDFParse | undefined;
  try {
    parser = new PDFParse({ data: buffer });
    const result = await parser.getText();
    // pdf-parse adds a page separator such as "-- 1 of 2 --" to each page.
    // It is useful for debugging but should not be sent to the model as resume content.
    const text = result.text
      .replace(/\r\n?/g, "\n")
      .replace(/^\s*--\s*\d+\s+of\s+\d+\s*--\s*$/gm, "")
      .trim();
    if (!text) {
      throw new AppError(
        "PDF_TEXT_EMPTY",
        "PDF 中未提取到文本。该文件可能是扫描件，请先进行 OCR。",
      );
    }
    return { source: absolutePath, pages: result.total, text };
  } catch (cause) {
    if (cause instanceof AppError) throw cause;
    throw new AppError("PDF_PARSE_FAILED", `无法解析 PDF：${absolutePath}`, { cause });
  } finally {
    await parser?.destroy();
  }
}
