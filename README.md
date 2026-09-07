# resume-cli-demo

一个可运行的 AI 简历解析 CLI Demo：读取本地 PDF，提取文本；通过 OpenAI 兼容 API 提取简历结构化信息；再基于 JD 给出匹配评分。它是面试题所需的演示工具，不应用作自动化招聘决策。

## 技术选型

- Node.js 20+、TypeScript、pnpm
- `pdf-parse`：解析 PDF 中的文本层
- 原生 `fetch`：调用 OpenAI 兼容的 Chat Completions API
- Commander：命令行参数与帮助信息
- Vitest：基础单元测试

## 安装与配置

```bash
pnpm install
pnpm run build
```

真实 AI 模式需复制环境变量模板并填入 Key：

```bash
Copy-Item .env.example .env
```

`.env` 中的配置：

```dotenv
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

`OPENAI_BASE_URL` 应指向实现 Chat Completions 接口的 OpenAI 兼容服务（默认官方 OpenAI `/v1` 地址）。`--mock` 模式不读取也不发送 API Key。

如果 pnpm 首次安装提示需要批准 `esbuild` 构建脚本，可执行 `pnpm approve-builds --all`，然后再次执行 `pnpm install`。

## CLI 命令

所有成功结果均打印为格式化 JSON；出错时会向标准错误输出带有 `code` 和 `message` 的 JSON。运行 `pnpm run resume-cli -- --help` 可查看帮助。

```bash
# 1. 从 PDF 提取原始文本
pnpm run resume-cli -- parse ./resume.pdf

# 2. 提取结构化简历信息（真实 AI）
pnpm run resume-cli -- extract ./resume.pdf

# 3. 根据 JD 文件评分（真实 AI）
pnpm run resume-cli -- score ./resume.pdf --jd ./jd.txt
```

两个已实现的加分项：

```bash
# --mock：不配置 AI Key 也可完整演示 extract / score
pnpm run resume-cli -- extract ./resume.pdf --mock
pnpm run resume-cli -- score ./resume.pdf --jd ./jd.txt --mock

# --output：把与终端相同的 JSON 写入文件；目录不存在时会创建
pnpm run resume-cli -- extract ./resume.pdf --mock --output ./output/profile.json
```

`parse` 结果包含 `source`、`pages`、`text`；`extract` 固定返回：

```json
{
  "name": "Alex Chen",
  "phone": "+1 415 555 0123",
  "email": "alex.chen@example.com",
  "city": "Hangzhou",
  "education": [
    {
      "school": "Example University",
      "major": "Computer Science",
      "degree": "B.S.",
      "graduation_time": "2015 - 2019"
    }
  ],
  "skills": ["TypeScript", "React"]
}
```

`score` 固定返回 `overall_score`、`skill_score`、`experience_score`、`education_score`（均为 0-100），以及 `comment` 和 `interview_questions`。真实 AI 返回会先执行 JSON 解析与字段/分数范围校验，错误会给出可读提示。

## 演示

仓库提供英文样例 JD。先生成一个带文本层的样例 PDF，再一键跑完三条命令：

```bash
pnpm run generate:example
pnpm run demo
```

或单独演示：

```bash
pnpm run resume-cli -- parse examples/resume-sample.pdf
pnpm run resume-cli -- extract examples/resume-sample.pdf --mock --output examples/extract-result.json
pnpm run resume-cli -- score examples/resume-sample.pdf --jd examples/jd-sample.txt --mock
```

## 测试

```bash
pnpm run test
```

测试覆盖 JSON 代码围栏处理、AI 输出字段/范围校验，以及本地 mock 提取和评分结果。

## 已实现与限制

已实现 PDF 存在性、文件类型、读取失败、空文本和 JD 缺失/空文件的错误处理；`parse`、`extract`、`score` 均支持 `--help`。AI 请求有 30 秒超时保护，错误统一输出 JSON；PDF 页面分隔标记不会进入最终文本。扫描版或没有文本层的 PDF 会提示先 OCR；当前版本没有内置 OCR。真实模式依赖模型服务正确返回 JSON，若服务不可用可用 `--mock` 完成本地演示。
