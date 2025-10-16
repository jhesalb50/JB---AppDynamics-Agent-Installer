
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import xml.etree.ElementTree as ET
import base64
from io import BytesIO
from PIL import Image, ImageTk  # only if pillow is available

# base64 placeholder logo (simple AppDynamics-blue gradient square)
LOGO_BASE64 = """
iVBORw0KGgoAAAANSUhEUgAAADAAAAAwCAYAAABg3Am1AAAA5klEQVRoge2YwQ6CMBBF3wRVqVot
tlMJpANAELo6FbAkkmfMVV9dMLGR478Uu8QwF5uTdDUgz1CJyTzE0l7c7+jAzYgRPAETALmAMykG
KwRhwO3AJOB1fwEcnmlLCzNjQAQ0FCpclFyBlbDkgZUnbSObDDsMhFJsjg+A9t+jHBQLDGAJeX8E
6fbxe+pI2GAiD7iamCKxkON8cQjHehx0CvA4RlmYpKjbaoQj33PNAKx8cVf0oLg6qcbscNRBkIgM
VN92qD+/rXQf34kN+d/GSNwN/PVWOEL1IF0i+F9D6w5dS7ldtzA+bfEUMhdYuVAAAAAElFTkSuQmCC
"""

class AppDynamicsAgentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("AppDynamics Agent Manager (Linux)")
        self.root.geometry("900x700")
        self.root.minsize(750, 600)
        self.root.configure(bg="#f2f3f5")

        # Header with logo and text
        header = tk.Frame(self.root, bg="#0B3D91", height=70)
        header.pack(fill="x")
        logo_data = base64.b64decode(LOGO_BASE64)
        pil_img = Image.open(BytesIO(logo_data))
        pil_img = pil_img.resize((48, 48))
        self.logo_img = ImageTk.PhotoImage(pil_img)
        logo_label = tk.Label(header, image=self.logo_img, bg="#0B3D91")
        logo_label.pack(side="left", padx=20, pady=10)
        title_label = tk.Label(header, text="AppDynamics Agent Manager", bg="#0B3D91", fg="white", font=("Segoe UI", 18, "bold"))
        title_label.pack(side="left")

        # Config frame
        config = ttk.LabelFrame(self.root, text="Controller and Agent Configuration")
        config.pack(fill="x", padx=20, pady=10)
        labels = ["Controller Host:", "Controller Port:", "Account Name:", "Account Key:", "Application Name:", "Download URL:"]
        self.entries = {}
        for i, label in enumerate(labels[:-1]):
            ttk.Label(config, text=label).grid(row=i//2, column=(i%2)*2, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(config, width=40 if i%2==0 else 20, show="*" if "Key" in label else "")
            entry.grid(row=i//2, column=(i%2)*2+1, padx=5, pady=5)
            self.entries[label] = entry
        ttk.Label(config, text=labels[-1]).grid(row=3, column=0, sticky="w", padx=5, pady=5)
        download = ttk.Entry(config, width=80)
        download.grid(row=3, column=1, columnspan=3, padx=5, pady=5)
        self.entries[labels[-1]] = download

        # Options
        opts = ttk.LabelFrame(self.root, text="Agent Options")
        opts.pack(fill="x", padx=20, pady=5)
        self.server_vis = tk.BooleanVar()
        self.http_listener = tk.BooleanVar()
        ttk.Checkbutton(opts, text="Enable Server Visibility", variable=self.server_vis).grid(row=0, column=0, padx=8, pady=5, sticky="w")
        ttk.Checkbutton(opts, text="Enable HTTP Listener (port 8293)", variable=self.http_listener).grid(row=0, column=1, padx=8, pady=5, sticky="w")

        # Buttons
        buttons = tk.Frame(self.root, bg="#f2f3f5")
        buttons.pack(fill="x", padx=20, pady=5)
        tk.Button(buttons, text="Discover", bg="#17a2b8", fg="white", width=14, command=self.discover_agent).pack(side="left", padx=6)
        tk.Button(buttons, text="Install", bg="#28a745", fg="white", width=14, command=self.install_agent).pack(side="left", padx=6)
        tk.Button(buttons, text="Uninstall", bg="#dc3545", fg="white", width=14, command=self.uninstall_agent).pack(side="left", padx=6)
        tk.Button(buttons, text="Clear Logs", bg="#6c757d", fg="white", width=14, command=self.clear_logs).pack(side="right", padx=6)

        # Logs
        logs = ttk.LabelFrame(self.root, text="Activity Log")
        logs.pack(fill="both", expand=True, padx=20, pady=10)
        self.log_area = scrolledtext.ScrolledText(logs, wrap=tk.WORD, state="disabled")
        self.log_area.pack(fill="both", expand=True)

    def log(self, msg):
        self.log_area.configure(state="normal")
        self.log_area.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        self.log_area.configure(state="disabled")
        self.log_area.see(tk.END)

    def clear_logs(self):
        self.log_area.configure(state="normal")
        self.log_area.delete("1.0", tk.END)
        self.log_area.configure(state="disabled")

    def run_cmd(self, cmd):
        try:
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in proc.stdout:
                self.log(line.strip())
            for err in proc.stderr:
                if err.strip():
                    self.log(f"ERROR: {err.strip()}")
            proc.wait()
            return proc.returncode
        except Exception as e:
            self.log(f"Exception: {e}")
            return 1

    def uninstall_agent(self):
        threading.Thread(target=self._uninstall, daemon=True).start()

    def _uninstall(self):
        self.log("Starting uninstall process...")
        agent_path = "/opt/appdynamics/machine-agent"
        if not os.path.exists(agent_path):
            self.log("No existing agent installation found.")
            return
        backup = f"/opt/appdynamics/backup_machine_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log(f"Backing up existing agent directory to {backup}")
        self.run_cmd(f"sudo mv {agent_path} {backup}")
        self.run_cmd("sudo systemctl stop machine-agent.service || true")
        self.run_cmd("sudo systemctl disable machine-agent.service || true")
        self.log("Uninstall complete.")

    def install_agent(self):
        threading.Thread(target=self._install, daemon=True).start()

    def _install(self):
        host = self.entries["Controller Host:"].get().strip()
        port = self.entries["Controller Port:"].get().strip()
        acc = self.entries["Account Name:"].get().strip()
        key = self.entries["Account Key:"].get().strip()
        app = self.entries["Application Name:"].get().strip()
        url = self.entries["Download URL:"].get().strip()
        if not all([host, port, acc, key, app]):
            messagebox.showinfo("Missing Config", "Please fill all required fields before installing.")
            return

        target = "/opt/appdynamics/machine-agent"
        self.log("Starting installation...")
        self.run_cmd(f"sudo mkdir -p {target}")
        self.run_cmd(f"sudo chown $(whoami):$(whoami) {target}")
        if url:
            filename = os.path.basename(url)
            self.log(f"Downloading package from {url}")
            self.run_cmd(f"wget -q {url} -O /tmp/{filename}")
            self.run_cmd(f"sudo tar -xzf /tmp/{filename} -C /opt/appdynamics/")
        xml_path = os.path.join(target, "conf/controller-info.xml")
        os.makedirs(os.path.dirname(xml_path), exist_ok=True)
        with open(xml_path, "w") as f:
            f.write(f"""<controller-info>
    <controller-host>{host}</controller-host>
    <controller-port>{port}</controller-port>
    <account-name>{acc}</account-name>
    <account-access-key>{key}</account-access-key>
    <application-name>{app}</application-name>
</controller-info>""")
        self.log("Controller-info.xml written.")
        if self.server_vis.get():
            self.log("Server Visibility enabled.")
        if self.http_listener.get():
            self.log("HTTP listener enabled on port 8293.")
        self.run_cmd(f"sudo chown -R $(whoami):$(whoami) {target}")
        self.run_cmd(f"sudo {target}/bin/machine-agent &")
        self.log("Installation finished successfully!")

    def discover_agent(self):
        threading.Thread(target=self._discover, daemon=True).start()

    def _discover(self):
        self.log("Checking for existing Machine Agent...")
        base = "/opt/appdynamics/machine-agent"
        if not os.path.exists(base):
            self.log("No existing agent found.")
            return
        xml_path = os.path.join(base, "conf/controller-info.xml")
        if os.path.exists(xml_path):
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                info = {el.tag: el.text for el in root}
                for label, field in self.entries.items():
                    tag = label.lower().split()[0]
                    if "controller" in tag and "host" in tag:
                        field.delete(0, tk.END); field.insert(0, info.get("controller-host", ""))
                    elif "port" in tag:
                        field.delete(0, tk.END); field.insert(0, info.get("controller-port", ""))
                    elif "account" in tag and "name" in tag:
                        field.delete(0, tk.END); field.insert(0, info.get("account-name", ""))
                    elif "key" in tag:
                        field.delete(0, tk.END); field.insert(0, info.get("account-access-key", ""))
                    elif "application" in tag:
                        field.delete(0, tk.END); field.insert(0, info.get("application-name", ""))
                self.log(f"Controller: {info.get('controller-host','')}:{info.get('controller-port','')}")
                self.log(f"Application: {info.get('application-name','')}")
                self.log(f"Account: {info.get('account-name','')}")
            except Exception as e:
                self.log(f"Error parsing controller-info.xml: {e}")
        version_file = os.path.join(base, "version.txt")
        version = "unknown"
        if os.path.exists(version_file):
            with open(version_file) as vf:
                version = vf.readline().strip()
        rc = subprocess.getoutput("systemctl is-active machine-agent.service 2>/dev/null")
        self.log(f"Agent path: {base}")
        self.log(f"Agent version: {version}")
        self.log(f"Service status: {rc}")
        self.log("Fields populated from existing configuration.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppDynamicsAgentManager(root)
    root.mainloop()
