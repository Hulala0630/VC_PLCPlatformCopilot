# Infrastructure Notes / 基础设施说明

The repository starts with a simple `docker-compose.yml` for local orchestration.

当前仓库先使用简单的 `docker-compose.yml` 进行本地编排。

Future production-oriented work should add:

未来面向生产环境时应补充：

- Backend image hardening and non-root runtime user.
  后端镜像加固，并使用非 root 运行用户。
- Frontend static build served through Nginx or a platform-native static host.
  前端静态构建可由 Nginx 或平台原生静态托管服务提供。
- SQLite volume backup strategy or migration to PostgreSQL if collaboration requirements grow.
  为 SQLite 增加卷备份策略；如果协作需求增长，可迁移到 PostgreSQL。
- Chroma persistence volume and model/runtime configuration.
  为 Chroma 增加持久化卷，并配置模型与运行时参数。
