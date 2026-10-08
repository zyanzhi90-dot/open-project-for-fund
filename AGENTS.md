# 项目工作约定

当前交付文件为《全国机器人开放课题_个人申报台账_最终核验版_20261008.xlsx》。继续修改应另存新版，保留既有版本。复用已有核验资料；未获要求不扩展地域检索。忠实展示实际任务与条款，不作“适合承担”等能力判断，不以日期未过代替可申请判断。

## 自动同步 GitHub

用户已授权本目录的项目成果、核验来源和历史记录持续同步至 https://github.com/zyanzhi90-dot/open-project-for-fund 。

每次在本项目完成文件修改、核验记录或新成果后，必须在最终回复前执行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\sync-github.ps1
```

执行后确认上传成功。若失败，保留本地成果并明确报告失败原因，不宣称已同步。遵守 .gitignore；个人未公开申请书、凭据、依赖和缓存不上传。不要强制推送、改写远程历史或自动解决远程冲突。
