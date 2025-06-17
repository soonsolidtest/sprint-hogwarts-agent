# ChromeDriver 目录

这个目录用于存放 ChromeDriver 可执行文件。

## 使用说明

1. **下载 ChromeDriver**
   - 访问 https://chromedriver.chromium.org/downloads
   - 或者访问 https://googlechromelabs.github.io/chrome-for-testing/
   - 下载与你的 Chrome 浏览器版本匹配的 ChromeDriver

2. **安装步骤**
   ```bash
   # 下载后将 chromedriver 文件放到这个目录
   # macOS/Linux 需要添加执行权限
   chmod +x drivers/chromedriver
   ```

3. **支持的文件名**
   - `chromedriver` (Linux/macOS)
   - `chromedriver.exe` (Windows)

## 版本兼容性

请确保 ChromeDriver 版本与你的 Chrome 浏览器版本兼容：

- Chrome 114+ 使用 ChromeDriver 114+
- 可以通过 `chrome://version/` 查看 Chrome 版本
- 可以通过 `./chromedriver --version` 查看 ChromeDriver 版本

## 自动下载

如果本地没有 ChromeDriver，系统会按以下顺序尝试：
1. 使用本目录中的 ChromeDriver
2. 使用系统 PATH 中的 ChromeDriver  
3. 通过网络自动下载（需要网络连接） 