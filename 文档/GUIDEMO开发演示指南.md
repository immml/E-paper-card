# lighting OS GUIDEMO 开发演示指南

## 定位

GUIDEMO 同时包含 GUI Demo 和 Guide Demo：前者用 Tkinter 展示设备状态与协议日志，后者说明开发者如何在没有硬件时复现管理协议和状态机流程。它是 PC 本地模拟器，不是正式设备控制端。

## 环境

- Windows、Linux 或 macOS
- Python 3.10+
- Python 标准库 `tkinter`
- 不需要 `pip install`，不需要真实硬件或网络

## 启动与测试

在仓库根目录执行：

```powershell
py -3 软件\工具\guidemo\run_gui.py
py -3 -m unittest discover -s 软件\工具\guidemo\tests -p "test_*.py" -v
```

GUI 操作：启动后观察 `OFF`；点击“获取电源”；点击“长按 Kpower”；依次点击“USB 插入/USB 拔出”；点击“重置模拟器”。TX/RX 区显示帧的十六进制内容。关闭窗口后程序退出。

## 协议基线

| 字段 | 值 |
|---|---|
| SOF | `0xA5` |
| Version | `1` |
| Header | 7 bytes |
| Payload 上限 | 64 bytes |
| CRC | 初值 `0xFFFF`、多项式 `0xA001` |
| CRC 字节序 | little-endian |

当前模拟命令是 `GET_POWER`、`SET_POWER`、`BUTTON_EVENT` 和 `USB_EVENT`。GUI 的 payload 约定用于演示，不能替代真实 CH32/ESP32 接口协议最终冻结。

## 验证边界

PC 上已验证协议帧、CRC、载荷边界、模拟状态变更、重复序号拒绝和 GUI 操作路径。以下项目未验证：真实串口/USB CDC、BLE、墨水屏刷新、GPIO、I²C、AXP2101、WS2812、CH32 电源管理、真实按键抖动、睡眠唤醒、云端、AI 和 OTA。

因此，GUIDEMO 的 `BOOTING`、`USB` 和电源状态是模拟器内部状态，不应在发布说明中称为硬件功能已完成。错误测试和协议日志也不能证明真实总线的时序和电气可靠性。

## 后续接入硬件

保留 `protocol.py` 和模拟器测试，把传输层从本地 `DeviceSimulator` 替换为串口、USB CDC 或 BLE 适配器；保留同一帧编解码、超时、重试和权限检查。接入前必须新增真实设备握手、重连、日志脱敏和硬件测试，不能直接把 GUIDEMO 的模拟响应当成设备响应。

## 许可证

GUI 工具属于 `软件/`，使用 AGPL-3.0-or-later；文档按仓库文档许可证处理。不得在示例中放入 Wi-Fi 凭证、设备私钥、证书或云端激活码。
