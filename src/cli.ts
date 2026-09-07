#!/usr/bin/env node
import { Command } from "commander";
import { extractWithAi, scoreWithAi } from "./ai/client.js";
import { extractWithMock, scoreWithMock } from "./ai/mock.js";
import { AppError, toUserError } from "./core/errors.js";
import { printJson, saveJson } from "./core/output.js";
import { readJobDescription } from "./io/job-description.js";
import { readPdfText } from "./pdf/reader.js";

interface OutputOptions {
  output?: string;
}

interface AiOptions extends OutputOptions {
  mock?: boolean;
}

const program = new Command();

program
  .name("resume-cli")
  .description("读取 PDF 简历、提取结构化信息，并根据 JD 输出匹配评分")
  .version("0.1.0")
  .showHelpAfterError("使用 --help 查看命令说明。")
  .addHelpText("after", `
示例：
  $ resume-cli parse ./resume.pdf
  $ resume-cli extract ./resume.pdf --mock --output result.json
  $ resume-cli score ./resume.pdf --jd ./jd.txt --mock

配置真实 AI：复制 .env.example 为 .env，并填入 OPENAI_API_KEY。
`);

program
  .command("parse <pdf_path>")
  .description("提取本地 PDF 的文本内容")
  .option("-o, --output <path>", "将 JSON 结果保存到文件（加分项）")
  .action(async (pdfPath: string, options: OutputOptions) => {
    const result = await readPdfText(pdfPath);
    printJson(result);
    await saveJson(result, options.output);
  });

program
  .command("extract <pdf_path>")
  .description("调用 AI 从 PDF 简历中提取结构化信息")
  .option("--mock", "使用确定性的本地演示数据，不调用 AI（加分项）")
  .option("-o, --output <path>", "将 JSON 结果保存到文件（加分项）")
  .action(async (pdfPath: string, options: AiOptions) => {
    const resume = await readPdfText(pdfPath);
    const result = options.mock ? extractWithMock(resume.text) : await extractWithAi(resume.text);
    printJson(result);
    await saveJson(result, options.output);
  });

program
  .command("score <pdf_path>")
  .description("调用 AI 按 JD 对 PDF 简历进行匹配评分")
  .option("--jd <path>", "岗位描述文本文件路径")
  .option("--mock", "使用确定性的本地演示数据，不调用 AI（加分项）")
  .option("-o, --output <path>", "将 JSON 结果保存到文件（加分项）")
  .action(async (pdfPath: string, options: AiOptions & { jd?: string }) => {
    if (!options.jd?.trim()) {
      throw new AppError("JD_REQUIRED", "score 命令需要提供 --jd <path>。使用 --help 查看命令说明。");
    }
    const [resume, jdText] = await Promise.all([readPdfText(pdfPath), readJobDescription(options.jd)]);
    const result = options.mock
      ? scoreWithMock(resume.text, jdText)
      : await scoreWithAi(resume.text, jdText);
    printJson(result);
    await saveJson(result, options.output);
  });

async function main(): Promise<void> {
  try {
    await program.parseAsync();
  } catch (error) {
    const userError = toUserError(error);
    process.stderr.write(`${JSON.stringify({ error: { code: userError.code, message: userError.message } })}\n`);
    process.exitCode = 1;
  }
}

void main();
