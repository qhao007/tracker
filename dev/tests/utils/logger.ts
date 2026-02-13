/**
 * 日志工具
 */

/**
 * 日志级别
 */
export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR',
}

/**
 * 日志条目
 */
interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  testName?: string;
  step?: string;
  data?: unknown;
}

/**
 * 简单的日志记录器
 */
export class Logger {
  private logs: LogEntry[] = [];
  private testName: string = '';

  /**
   * 设置当前测试名称
   */
  setTestName(testName: string): void {
    this.testName = testName;
  }

  /**
   * 记录日志
   */
  log(level: LogLevel, message: string, data?: unknown): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      testName: this.testName,
      data,
    };
    this.logs.push(entry);

    // 同时输出到控制台
    const prefix = `[${new Date().toISOString()}] [${level}]`;
    if (data) {
      console.log(`${prefix} ${message}`, data);
    } else {
      console.log(`${prefix} ${message}`);
    }
  }

  /**
   * Debug 级别日志
   */
  debug(message: string, data?: unknown): void {
    this.log(LogLevel.DEBUG, message, data);
  }

  /**
   * Info 级别日志
   */
  info(message: string, data?: unknown): void {
    this.log(LogLevel.INFO, message, data);
  }

  /**
   * Warn 级别日志
   */
  warn(message: string, data?: unknown): void {
    this.log(LogLevel.WARN, message, data);
  }

  /**
   * Error 级别日志
   */
  error(message: string, data?: unknown): void {
    this.log(LogLevel.ERROR, message, data);
  }

  /**
   * 记录测试开始
   */
  testStart(testName: string): void {
    this.setTestName(testName);
    this.info(`🧪 Test started: ${testName}`);
  }

  /**
   * 记录测试结束
   */
  testEnd(testName: string, status: 'passed' | 'failed' | 'skipped'): void {
    const emoji = status === 'passed' ? '✅' : status === 'failed' ? '❌' : '⏭️';
    this.info(`${emoji} Test ended: ${testName} - ${status}`);
    this.testName = '';
  }

  /**
   * 记录步骤
   */
  step(step: string, message: string): void {
    this.info(`📍 [${step}] ${message}`);
  }

  /**
   * 记录页面操作
   */
  pageAction(action: string, selector: string): void {
    this.debug(`Page action: ${action} on ${selector}`);
  }

  /**
   * 记录 API 调用
   */
  apiCall(method: string, url: string, status?: number): void {
    const statusStr = status ? ` [${status}]` : '';
    this.info(`🌐 API: ${method} ${url}${statusStr}`);
  }

  /**
   * 记录断言结果
   */
  assertion(description: string, passed: boolean): void {
    const emoji = passed ? '✅' : '❌';
    this.info(`${emoji} Assertion: ${description}`);
  }

  /**
   * 获取所有日志
   */
  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  /**
   * 清空日志
   */
  clear(): void {
    this.logs = [];
  }

  /**
   * 导出日志
   */
  export(): string {
    return JSON.stringify(this.logs, null, 2);
  }
}

// 全局日志器实例
export const logger = new Logger();

/**
 * 测试步骤记录器
 */
export class StepRecorder {
  private steps: string[] = [];
  private stepNumber: number = 0;

  /**
   * 开始记录步骤
   */
  start(): void {
    this.steps = [];
    this.stepNumber = 0;
  }

  /**
   * 添加步骤
   */
  add(description: string): number {
    this.stepNumber++;
    const step = `${this.stepNumber}. ${description}`;
    this.steps.push(step);
    logger.info(`📝 Step ${step}`);
    return this.stepNumber;
  }

  /**
   * 获取所有步骤
   */
  getSteps(): string[] {
    return [...this.steps];
  }

  /**
   * 打印步骤摘要
   */
  printSummary(): void {
    console.log('\n📋 Steps Summary:');
    this.steps.forEach(step => console.log(`  ${step}`));
    console.log('');
  }
}

/**
 * 创建测试专用的日志器
 */
export function createTestLogger(testName: string): Logger {
  const testLogger = new Logger();
  testLogger.setTestName(testName);
  return testLogger;
}
