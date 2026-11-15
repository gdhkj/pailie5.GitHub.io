# 排列五四位杀号分析（GitHub Pages）

## 功能
- 以最近100期为默认主分析窗口；可切换30/100/200/300/500期。
- 万、千、百、十位分开统计0–9频率。
- 每个位置可独立设置自动排除1–9个数字。
- 自动按所选窗口低频数字生成建议，并可手动修改。
- 滚动历史回测：每一期只使用此前N期数据，避免未来数据泄漏。
- 每日GitHub Actions同步官方开奖数据，保留最近500期。

## 部署
1. 将整个文件夹内容上传到一个 GitHub repository。
2. 确认仓库 Settings → Actions → General 允许 Actions 写入 repository（Read and write permissions）。
3. 到 Actions → `Sync official P5 results` → Run workflow，手动运行首次同步。
4. 检查 `data/draws.json` 是否出现至少100期记录。若失败，先检查官方接口是否变更或 gameNo 是否仍为 `350133`，不要将未验证的数据当作正式结果。
5. Settings → Pages → Deploy from a branch，选择 `main` / `/(root)`。
6. 等待 Pages 发布后打开网址。

## 官方数据接口
默认调用：
`https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry`
参数：`gameNo=350133&provinceId=0&pageSize=100&isVerify=1&pageNo=1`
请求使用移动端 User-Agent 与移动端 Referer。接口编号和响应字段基于公开开发者资料线索，可能变更；首次运行必须验证返回的期号与开奖号码能和中国体彩网官方公布内容对应。若接口被 WAF 阻挡或格式变更，workflow 会失败并保留旧数据。

可以在 GitHub Actions Variables 中配置：
- `SPORTTERY_GAME_NO`
- `SPORTTERY_PAGE_SIZE`
- `SPORTTERY_API_URL`

## 回测口径
对每一个测试期，使用之前N期的每个位置数字频数，选出频数最低的K个数字作为排除集合，再检查实际开奖号码是否落入集合。理论随机基准约为 K/10。历史回测不是未来保证，也不能据此宣称存在稳定预测优势。

## 重要限制
- 只分析五位排列五开奖结果的前四位：万、千、百、十；个位置不参与分析。
- 前端只读仓库中的 `data/draws.json`，不直接请求官方 API。
- GitHub Actions 是每日定时任务，执行时间可能延迟；官方接口不可用时会保留上一版数据。
- 本项目仅用于历史数据统计与研究，不含投注、收款或派彩功能。
