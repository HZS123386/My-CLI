import { mkdtemp, rm, writeFile } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { PDFDocument, StandardFonts } from "pdf-lib";
import { afterEach, describe, expect, it } from "vitest";
import { readPdfText } from "./reader.js";

const temporaryDirectories: string[] = [];

afterEach(async () => {
  await Promise.all(temporaryDirectories.splice(0).map((directory) => rm(directory, { recursive: true, force: true })));
});

async function createTextPdf(): Promise<string> {
  const directory = await mkdtemp(path.join(os.tmpdir(), "resume-cli-test-"));
  temporaryDirectories.push(directory);
  const document = await PDFDocument.create();
  const page = document.addPage([400, 400]);
  const font = await document.embedFont(StandardFonts.Helvetica);
  page.drawText("Name: Test Candidate\nTypeScript and PDF parsing", { x: 30, y: 350, size: 12, font, lineHeight: 18 });
  const target = path.join(directory, "resume.pdf");
  await writeFile(target, await document.save());
  return target;
}

describe("PDF reader", () => {
  it("extracts text and removes parser page separators", async () => {
    const result = await readPdfText(await createTextPdf());
    expect(result.pages).toBe(1);
    expect(result.text).toContain("Name: Test Candidate");
    expect(result.text).not.toMatch(/--\s*1\s+of\s+1\s*--/);
  });

  it("reports a clear error for a missing path", async () => {
    await expect(readPdfText(path.join(os.tmpdir(), "resume-cli-no-such-file.pdf")))
      .rejects.toThrow("找不到 PDF 文件");
  });
});
