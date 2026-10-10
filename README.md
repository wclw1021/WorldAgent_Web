# WorldAgent

简约静态项目页，沿用 WorldParticle 的 Linux Biolinum 字体、白底与浅色分区。

## 预览

```powershell
python tools/serve.py
```

打开 http://localhost:4173 。服务支持视频拖动进度。也可以直接打开 `index.html`，或将 `index.html`、`styles.css`、`script.js` 和 `assets/` 部署到任意静态托管服务；页面不依赖 CDN。

## 内容与修改

- `content.json`：11 个结果标题、完整 prompt、backbone 视频对应关系。可添加 `paperUrl` 指定两个 Paper 按钮的目标地址；未设置时按钮暂不可点击。
- `tools/build.py`：页面结构、三张数值表格。修改后运行 `python tools/build.py`。
- `styles.css`：桌面与移动端样式。
- `script.js`：与参考页一致：提前一屏预加载、进入视野自动静音循环播放、离屏暂停、重新进入自动播放。
- `assets/`：本地字体、论文 Method 图、视频封面和 H.264 视频。

## 素材来源

- 样式与字体：`D:\WorldParticle_Web`。
- Method：论文 `figures/MethodVerification.pdf` 与 `sections/3_method.tex`。
- 主要视频：`D:\Dropbox\Agent-simulation\supp_video\source`，完整时长，移除音轨，压缩至网页版本。
- 《The Shining》与 baseline 视频：`WorldAgent.pptx` 第 18、19 页内嵌视频。
- 主结果 prompt：PPT 第 13–18 页及论文 `Main.pdf`、`More_main.pdf`。
- Comparison prompt：论文 `Comparison.pdf`、`More_comparison_model.pdf`。
- 三张表格：PPT 第 20、22 页，与论文 `sections/4_experiments_v2.tex` 交叉核对；保留小数精度与每个比较组的最优值高亮。

`tools/prepare_assets.py` 用于从以上本机素材重新生成资源，需要 Python 的 PyMuPDF、Pillow，以及 PATH 中的 ffmpeg。已有资源时不必运行。`.review/` 仅用于本地检查，不需要部署。
