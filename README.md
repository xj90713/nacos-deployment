# Nacos 配置 GitOps 发布仓库

本仓库用于管理所有环境的 Nacos 配置文件，实现nacos配置规范管理以及自动化发布。

## 目录结构

目录结构参考gitlab代码项目组以及项目名称

```
nacos-deployment/
├── business/                 # gitlab组
│   ├── business-listener/    # gitlab项目名称
│   │   ├── test/            # TEST配置
│   │   │   └── *.yaml
│   │   ├── uat/             # UAT环境配置
│   │   │   └── *.yaml
│   │   └── prod/            # 生产环境配置
│   │       └── *.yaml
│   └── customer-service/
│       ├── test/
│       ├── uat/
│       └── prod/
└── scrm/                     # SCRM组
    └── ...
```

## 发布策略

### test和 UAT 环境
- 配置文件路径：`*/*/test/*.yaml` 或 `*/*/uat/*.yaml`
- 发布分支：`release`
- 发布流程：
  1. 提交配置变更到 `release` 分支
  2. CI/CD 自动验证 YAML 格式
  3. 验证通过后自动发布到对应环境的 Nacos

### 生产环境
- 配置文件路径：`*/*/prod/*.yaml`
- 发布分支：`master`
- 发布流程：
  1. 从 `release` 分支创建 merge request 到 `master`
  2. 经过审核后合并到 `master`
  3. CI/CD 自动验证 YAML 格式和敏感信息替换
  4. 验证通过后自动发布到生产环境 Nacos


## CI/CD 验证

每次提交都会进行以下验证：
1. YAML 语法检查
2. 环境变量检查，主要是数据库密码信息等（仅生产环境）
3. Nacos 配置发布测试

## 分支策略

- `release`: 用于测试和 UAT 环境的配置发布
- `master`: 用于生产环境的配置发布

## 注意事项

1. 确保配置文件放在正确的环境目录下
2. 文件必须符合 YAML 格式规范
3. 生产环境配置变更必须经过 Code Review
4. 建议在提交前本地验证 YAML 格式
5. 每次可以提交多个 YAML 文件，如有失败部署的文件，根据报错修改再次提交即可
6. 如有新增nacos配置文件可以在对应路径新增 YAML 文件即可，无需登录nacos

## 常见问题

1. YAML 验证失败
   - 检查文件格式是否符合规范
   - 可以使用 yamllint 工具本地验证

2. 发布失败
   - 检查 Nacos 服务是否可用
   - 验证配置文件路径是否正确
   - 查看 CI/CD 日志定位具体错误
