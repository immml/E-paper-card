# SPDX-License-Identifier: AGPL-3.0-or-later
import tkinter as tk
from tkinter import ttk
try:
    from .protocol import BUTTON_EVENT, Frame, GET_POWER, USB_EVENT, encode, decode
    from .simulator import DeviceSimulator, PowerState
except ImportError:
    from protocol import BUTTON_EVENT, Frame, GET_POWER, USB_EVENT, encode, decode
    from simulator import DeviceSimulator, PowerState


class GuideDemo(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("lighting OS GUIDEMO（PC 模拟）")
        self.geometry("720x480")
        self.device = DeviceSimulator()
        self.sequence = 0
        self.state_var = tk.StringVar(value=self.device.state.value)
        self.usb_var = tk.StringVar(value="未插入")
        self.log_view = tk.Text(self, height=18, state="disabled")
        self._build()

    def _build(self):
        status = ttk.LabelFrame(self, text="模拟设备状态")
        status.pack(fill="x", padx=10, pady=8)
        ttk.Label(status, text="电源状态").grid(row=0, column=0, padx=8, pady=6)
        ttk.Label(status, textvariable=self.state_var).grid(row=0, column=1, padx=8)
        ttk.Label(status, text="USB").grid(row=0, column=2, padx=8)
        ttk.Label(status, textvariable=self.usb_var).grid(row=0, column=3, padx=8)
        actions = ttk.LabelFrame(self, text="模拟操作")
        actions.pack(fill="x", padx=10, pady=4)
        ttk.Button(actions, text="获取电源", command=lambda: self._send(GET_POWER, b"")).pack(side="left", padx=4, pady=6)
        ttk.Button(actions, text="长按 Kpower", command=lambda: self._send(BUTTON_EVENT, b"long")).pack(side="left", padx=4)
        ttk.Button(actions, text="USB 插入", command=lambda: self._send(USB_EVENT, b"\1")).pack(side="left", padx=4)
        ttk.Button(actions, text="USB 拔出", command=lambda: self._send(USB_EVENT, b"\0")).pack(side="left", padx=4)
        ttk.Button(actions, text="重置模拟器", command=self._reset).pack(side="left", padx=4)
        ttk.Label(self, text="TX/RX 协议日志（仅 PC 模拟，不代表硬件已验证）").pack(anchor="w", padx=10)
        self.log_view.pack(fill="both", expand=True, padx=10, pady=4)

    def _send(self, command, payload):
        frame = Frame(command, self.sequence, payload)
        self.sequence = (self.sequence + 1) & 0xFF
        tx = encode(frame)
        self._log("TX " + tx.hex(" "))
        try:
            rx = self.device.transact(tx)
            self._log("RX " + rx.hex(" "))
            response = decode(rx)
            if response.command == USB_EVENT:
                self.usb_var.set("已插入" if response.payload == b"\1" else "未插入")
            elif response.payload in {state.value.encode() for state in PowerState}:
                self.state_var.set(response.payload.decode())
        except ValueError as error:
            self._log("ERR " + str(error))

    def _reset(self):
        self.device.reset()
        self.state_var.set(self.device.state.value)
        self.usb_var.set("未插入")
        self._log("RESET simulator")

    def _log(self, message):
        self.log_view.configure(state="normal")
        self.log_view.insert("end", message + "\n")
        self.log_view.see("end")
        self.log_view.configure(state="disabled")


def run():
    GuideDemo().mainloop()
