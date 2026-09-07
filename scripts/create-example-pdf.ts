import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { PDFDocument, StandardFonts, rgb } from "pdf-lib";

const outputPath = path.resolve("examples/resume-sample.pdf");
const document = await PDFDocument.create();
const page = document.addPage([595, 842]);
const font = await document.embedFont(StandardFonts.Helvetica);
const lines = [
  "Name: Alex Chen",
  "Phone: +1 415 555 0123",
  "Email: alex.chen@example.com",
  "City: Hangzhou",
  "",
  "Summary",
  "Full-stack engineer with 4 years of experience building web platforms.",
  "",
  "Skills",
  "TypeScript, JavaScript, React, Node.js, REST API, SQL, Docker, Git",
  "",
  "Education",
  "2015 - 2019 | Example University | B.S. Computer Science",
];

page.drawText(lines.join("\n"), {
  x: 56,
  y: 786,
  size: 12,
  lineHeight: 19,
  font,
  color: rgb(0.1, 0.1, 0.1),
});

await mkdir(path.dirname(outputPath), { recursive: true });
await writeFile(outputPath, await document.save());
process.stdout.write(`示例 PDF 已生成：${outputPath}\n`);
