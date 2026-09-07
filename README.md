# resume-cli-demo

一个可直接运行的 Python AI 简历解析 CLI Demo：读取本地 PDF，提取文本；调用 OpenAI 兼容 API 提取结构化简历信息；根据岗位描述（JD）输出匹配评分。

这是面试题演示工具，不应作为自动化招聘决策依据。

## 技术选型

- Python 3.10+
- `pypdf`：读取 PDF 文本层
- Python 标准库 `urllib`：调用 OpenAI 兼容 Chat Completions API
- `argparse`：命令行参数和帮助信息
- `pytest`：自动化测试

## 安装

建议使用虚拟环境：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m pip install -e .
```

也可以只安装运行依赖：

```powershell
python -m pip install -r requirements.txt
```

## 配置真实 AI

复制 `.env.example` 为 `.env` 并填写配置：

```powershell
Copy-Item .env.example .env
```

```dotenv
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

`OPENAI_BASE_URL` 必须指向兼容 Chat Completions 的服务。`--mock` 模式不需要 API Key，也不会发送简历内容。

## CLI 用法

安装到虚拟环境后可以使用 `resume-cli`；未安装为命令时可使用 `python -m resume_cli`。以下示例使用后者，跨环境更稳定：

```powershell
# 查看帮助
python -m resume_cli --help

# 1. 提取 PDF 原始文本
python -m resume_cli parse .\resume.pdf

# 2. 从 PDF 提取结构化简历信息（真实 AI）
python -m resume_cli extract .\resume.pdf

# 3. 根据 JD 进行匹配评分（真实 AI）
python -m resume_cli score .\resume.pdf --jd .\jd.txt
```

两个已实现的加分项：

```powershell
# --mock：没有 API Key 也可完整演示
python -m resume_cli extract examples/resume-sample.pdf --mock
python -m resume_cli score examples/resume-sample.pdf --jd examples/jd-sample.txt --mock

# --output：将相同的 JSON 结果保存到文件，目录不存在时自动创建
python -m resume_cli extract examples/resume-sample.pdf --mock --output output/profile.json
```

也可以在执行 `python -m pip install -e .` 后直接运行：

```powershell
resume-cli parse examples/resume-sample.pdf
```

## 输出格式

`parse` 返回 `source`、`pages`、`text`。

`extract` 返回：

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

`score` 返回 `overall_score`、`skill_score`、`experience_score`、`education_score`（均为 0-100），以及 `comment` 和 `interview_questions`。AI 返回结果会先经过 JSON 解析和字段/分数范围校验。

成功结果输出到标准输出；错误结果以如下 JSON 输出到标准输出，并以退出码 1 结束：

```json
{
  "error": {
    "code": "PDF_NOT_FOUND",
    "message": "找不到 PDF 文件"
  }
}
```

## 演示和测试

仓库内置了可直接使用的样例文件：`examples/resume-sample.pdf` 和 `examples/jd-sample.txt`。

```powershell
python -m resume_cli parse examples/resume-sample.pdf
python -m resume_cli extract examples/resume-sample.pdf --mock --output examples/extract-result.json
python -m resume_cli score examples/resume-sample.pdf --jd examples/jd-sample.txt --mock
pytest
```

## 项目结构

```text
resume_cli/
├─ cli.py             命令行入口
├─ pdf_reader.py      PDF 文本读取和错误处理
├─ ai_client.py       OpenAI 兼容 API 调用和超时
├─ mock.py            本地可复现演示模式
├─ schemas.py         AI JSON 解析与校验
├─ prompts.py         提示词
├─ io_utils.py        环境变量、JD 和 JSON 文件处理
└─ errors.py          统一错误类型
tests/                回归测试
examples/             样例 PDF、JD 和输出
```

## 已实现与限制

已处理 PDF 不存在、路径不是文件、扩展名错误、PDF 解析失败、PDF 无文本、JD 不存在/为空、AI 未配置、AI 超时和无效 JSON 等情况。AI 请求默认 30 秒超时；`--output` 会拒绝覆盖输入 PDF 或 JD。扫描版或没有文本层的 PDF 需要先做 OCR；当前版本不内置 OCR。`--mock` 的分数仅用于演示，不代表真实招聘评估。
