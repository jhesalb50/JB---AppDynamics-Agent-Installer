
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

class AppDynamicsAgentManager:
    def __init__(self, root):
        self.root = root
        self.root.title("AppDynamics Agent Manager (Linux)")
        self.root.geometry("800x700")
        self.root.configure(bg="#f2f3f5")
        self.root.minsize(700, 600)

        # Header with logo placeholder
        header = tk.Frame(self.root, bg="#0B3D91", height=70)
        header.pack(fill="x")
        title_label = tk.Label(
            header,
            text="AppDynamics Agent Manager",
            bg="#0B3D91",
            fg="white",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(pady=15)

        # Configuration frame
        config_frame = ttk.LabelFrame(self.root, text="Controller and Agent Configuration")
        config_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(config_frame, text="Controller Host:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.host_entry = ttk.Entry(config_frame, width=40)
        self.host_entry.grid(row=0, column=1, pady=5)

        ttk.Label(config_frame, text="Controller Port:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.port_entry = ttk.Entry(config_frame, width=10)
        self.port_entry.insert(0, "443")
        self.port_entry.grid(row=0, column=3, pady=5)

        ttk.Label(config_frame, text="Account Name:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.account_entry = ttk.Entry(config_frame, width=40)
        self.account_entry.grid(row=1, column=1, pady=5)

        ttk.Label(config_frame, text="Account Key:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.account_key_entry = ttk.Entry(config_frame, width=20, show="*")
        self.account_key_entry.grid(row=1, column=3, pady=5)

        ttk.Label(config_frame, text="Application Name:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.appname_entry = ttk.Entry(config_frame, width=40)
        self.appname_entry.grid(row=2, column=1, pady=5)

        ttk.Label(config_frame, text="Download URL:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.url_entry = ttk.Entry(config_frame, width=60)
        self.url_entry.grid(row=3, column=1, columnspan=3, pady=5, sticky="we")

        # Checkbox options
        options_frame = ttk.LabelFrame(self.root, text="Agent Options")
        options_frame.pack(fill="x", padx=20, pady=10)
        self.server_vis = tk.BooleanVar()
        self.http_listener = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Enable Server Visibility", variable=self.server_vis).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Checkbutton(options_frame, text="Enable HTTP Listener (port 8293)", variable=self.http_listener).grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # Buttons frame
        button_frame = tk.Frame(self.root, bg="#f2f3f5")
        button_frame.pack(fill="x", padx=20, pady=10)
        install_btn = tk.Button(button_frame, text="Install", bg="#28a745", fg="white", width=15, command=self.install_agent)
        uninstall_btn = tk.Button(button_frame, text="Uninstall", bg="#dc3545", fg="white", width=15, command=self.uninstall_agent)
        clear_btn = tk.Button(button_frame, text="Clear Logs", bg="#6c757d", fg="white", width=15, command=self.clear_logs)
        install_btn.pack(side="left", padx=10)
        uninstall_btn.pack(side="left", padx=10)
        clear_btn.pack(side="right", padx=10)

        # Log output frame
        log_frame = ttk.LabelFrame(self.root, text="Activity Log")
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="disabled")
        self.log_area.pack(fill="both", expand=True)

    def log(self, message):
        self.log_area.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_area.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_area.configure(state="disabled")
        self.log_area.see(tk.END)

    def clear_logs(self):
        self.log_area.configure(state="normal")
        self.log_area.delete(1.0, tk.END)
        self.log_area.configure(state="disabled")

    def run_command(self, command):
        """Run shell command and stream output."""
        try:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in proc.stdout:
                self.log(line.strip())
            for err in proc.stderr:
                self.log(f"ERROR: {err.strip()}")
            proc.wait()
            return proc.returncode
        except Exception as e:
            self.log(f"Exception: {e}")
            return 1

    def uninstall_agent(self):
        threading.Thread(target=self._uninstall_agent, daemon=True).start()

    def _uninstall_agent(self):
        self.log("Starting uninstall process...")
        agent_path = "/opt/appdynamics/machine-agent"
        if not os.path.exists(agent_path):
            self.log("No existing agent installation found.")
            return
        backup_path = f"/opt/appdynamics/backup_machine_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.log(f"Backing up existing agent folder to: {backup_path}")
        self.run_command(f"sudo mv {agent_path} {backup_path}")
        self.log("Removing old service configs if any...")
        self.run_command("sudo systemctl stop machine-agent.service || true")
        self.run_command("sudo systemctl disable machine-agent.service || true")
        self.log("Uninstall completed successfully.")

    def install_agent(self):
        threading.Thread(target=self._install_agent, daemon=True).start()

    def _install_agent(self):
        host = self.host_entry.get().strip()
        port = self.port_entry.get().strip()
        account = self.account_entry.get().strip()
        key = self.account_key_entry.get().strip()
        appname = self.appname_entry.get().strip()
        url = self.url_entry.get().strip()
        vis_flag = self.server_vis.get()
        http_flag = self.http_listener.get()

        if not host or not account or not key or not appname:
            messagebox.showwarning("Missing Information", "Please fill all required configuration fields.")
            return

        self.log("Starting agent installation...")
        target_path = "/opt/appdynamics/machine-agent"
        self.run_command(f"sudo mkdir -p {target_path}")
        self.run_command(f"sudo chown $(whoami):$(whoami) {target_path}")

        if url:
            self.log(f"Downloading agent package from: {url}")
            filename = url.split("/")[-1]
            self.run_command(f"wget -q {url} -O /tmp/{filename}")
            self.log("Extracting agent package...")
            self.run_command(f"sudo tar -xzf /tmp/{filename} -C /opt/appdynamics/")
        else:
            self.log("No download URL provided. Skipping download step.")

        # Write controller configuration to conf/controller-info.xml
        ctrl_path = os.path.join(target_path, "conf")
        self.run_command(f"sudo mkdir -p {ctrl_path}")
        xml_content = f"""<controller-info>
    <controller-host>{host}</controller-host>
    <controller-port>{port}</controller-port>
    <account-name>{account}</account-name>
    <account-access-key>{key}</account-access-key>
    <application-name>{appname}</application-name>
</controller-info>"""
        conf_file = os.path.join(ctrl_path, "controller-info.xml")
        with open(conf_file, "w") as f:
            f.write(xml_content)
        self.log("Wrote controller-info.xml configuration.")

        if vis_flag:
            self.log("Server Visibility enabled.")
        if http_flag:
            self.log("HTTP Listener enabled on port 8293.")

        self.log("Setting permissions and ownership...")
        self.run_command(f"sudo chown -R $(whoami):$(whoami) {target_path}")

        self.log("Starting Machine Agent service...")
        self.run_command(f"sudo {target_path}/bin/machine-agent &")

        self.log("Installation process complete!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppDynamicsAgentManager(root)
    root.mainloop()
