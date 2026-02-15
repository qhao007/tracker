/**
 * 测试数据工厂 - 生成唯一测试数据
 * 确保每个测试使用唯一的数据，避免测试间干扰
 */
export class TestDataFactory {
  private static counter = 0;

  /**
   * 生成唯一的项目名称
   */
  static generateProjectName(prefix: string = 'TestUI_Project'): string {
    return `${prefix}_${this.generateUniqueId()}`;
  }

  /**
   * 生成唯一的 CP 名称
   */
  static generateCPName(prefix: string = 'TestUI_CP'): string {
    return `${prefix}_${this.generateUniqueId()}`;
  }

  /**
   * 生成唯一的 TC 名称
   */
  static generateTCName(prefix: string = 'TestUI_TC'): string {
    return `${prefix}_${this.generateUniqueId()}`;
  }

  /**
   * 生成唯一的 feature 名称
   */
  static generateFeatureName(prefix: string = 'Feature'): string {
    return `${prefix}_${this.generateUniqueId()}`;
  }

  /**
   * 生成时间戳前缀（用于快速识别）
   */
  static getTimestampPrefix(): string {
    return Date.now().toString();
  }

  /**
   * 生成唯一 ID
   */
  private static generateUniqueId(): string {
    return `${Date.now()}_${++this.counter}_${Math.random().toString(36).substr(2, 5)}`;
  }

  /**
   * 生成测试数据对象
   */
  static createProjectData(overrides?: { name?: string; description?: string }): {
    name: string;
    description: string;
  } {
    return {
      name: overrides?.name || this.generateProjectName(),
      description: `Test project created at ${new Date().toISOString()}`,
    };
  }

  /**
   * 生成 CP 测试数据
   */
  static createCPData(overrides?: {
    feature?: string;
    coverPoint?: string;
    details?: string;
    priority?: string;
  }): {
    feature: string;
    coverPoint: string;
    details: string;
    priority: string;
  } {
    return {
      feature: overrides?.feature || this.generateFeatureName(),
      coverPoint: overrides?.coverPoint || this.generateCPName(),
      details: overrides?.details || 'Test CP created by automated tests',
      priority: overrides?.priority || 'P0',
    };
  }

  /**
   * 生成 TC 测试数据
   * 注意：返回格式与 TCPage.createTC() 期望的格式一致
   */
  static createTCData(overrides?: {
    testbench?: string;
    testName?: string;
    scenario?: string;
    owner?: string;
    category?: string;
    dvMilestone?: string;
    targetDate?: string;
  }): {
    testbench: string;
    testName: string;
    name: string; // 别名，与 testName 相同
    scenario?: string;
    owner?: string;
    category?: string;
    dvMilestone?: string;
    targetDate?: string;
  } {
    const tcName = overrides?.testName || this.generateTCName();
    return {
      testbench: overrides?.testbench || 'tb_' + tcName,
      testName: tcName,
      name: tcName, // 别名，兼容测试代码中使用的 tcData.name
      scenario: overrides?.scenario || 'Test scenario for ' + tcName,
      owner: overrides?.owner || 'tester',
      category: overrides?.category || 'Functional',
      dvMilestone: overrides?.dvMilestone || 'DV1.0',
      targetDate: overrides?.targetDate,
    };
  }

  /**
   * 生成边界测试数据
   */
  static createBoundaryTestData(): {
    emptyString: string;
    shortString: string;
    longString: string;
    specialChars: string;
  } {
    return {
      emptyString: '',
      shortString: 'A',
      longString: 'A'.repeat(500),
      specialChars: '!@#$%^&*()_+-=[]{}|;\':",./<>?',
    };
  }
}
