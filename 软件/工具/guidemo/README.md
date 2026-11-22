# lighting OS GUIDEMO

这是无硬件条件下运行的 PC GUI 与管理协议模拟器，使用 Python 标准库 `tkinter`，不连接真实 ESP32、CH32、BLE、墨水屏或云服务。

## 运行

```powershell
py -3 软件\工具\guidemo\run_gui.py
```

## 测试

```powershell
py -3 -m unittest discover -s 软件\工具\guidemo\tests -p "test_*.py" -v
```

GUI 可演示获取电源、长按 Kpower、USB 插拔、状态重置，以及 TX/RX 十六进制协议日志。模拟器不代表真实硬件测试结果。协议遵循 ESP32-S3 固件的 SOF `0xA5`、版本 `1`、64 字节载荷上限和 CRC16 规则。

本目录属于 `软件/`，使用 AGPL-3.0-or-later。
