# 13_同步｜放置说明（跨端协作可选）

- 用途：本地 / AI 助手 / 远程仓库三端同步。
- 操作（以 git 为例）：
  1. 本地改动同步：`git add .` → `git commit -m "update project library"` → `git push`
  2. 另一端读取远程仓库直接修改上传
  3. 远端更新同步到本地：`git pull`
- 规则：上传前读取远端 HEAD，只提交本次差分；拒绝租约后检查并发，不强制推。
