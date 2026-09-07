export class AppError extends Error {
  readonly code: string;

  constructor(code: string, message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.name = "AppError";
    this.code = code;
  }
}

export function toUserError(error: unknown): AppError {
  if (error instanceof AppError) return error;
  if (error instanceof Error) return new AppError("UNEXPECTED_ERROR", error.message, { cause: error });
  return new AppError("UNEXPECTED_ERROR", "发生了未知错误。", { cause: error });
}
