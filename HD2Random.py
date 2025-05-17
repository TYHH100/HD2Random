import requests
import threading
import json
import random
import os
import sys
import tkinter as tk
import ttkbootstrap as ttk
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict
from tkinter import messagebox

UPDATE_URLS = [
    "https://raw.githubusercontent.com/TYHH100/HD2Random/master/hd2rd_config.json",
    "https://ts.tyhh10.xyz:58092/hd2rd_config.json"
]

@dataclass
class Loadout:
    strategems: List[str]
    primary: str
    primary_attachment: str
    secondary: str
    grenade: str
    armor: str
    enhancement: str

class ConfigManager:
    def __init__(self):
        self.excludes = {
            "strategems": [],
            "primary": [],
            "secondary": [],
            "grenades": [],
            "armors": [],
            "enhancements": [],
            "primary_attachments": {}
        }
        self.batch_size = 1

class LoadoutGenerator:
    def _load_or_create_config(self) -> Dict:
        def get_version(cfg):
            return cfg.get("version", "0.0.0")

        # 如果本地没有配置文件，直接走原有流程
        if not self.config_path.exists():
            for url in UPDATE_URLS:
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    new_config = response.json()
                    self._validate_config(new_config)
                    with open(self.config_path, 'w', encoding='utf-8') as f:
                        json.dump(new_config, f, ensure_ascii=False, indent=2)
                    messagebox.showinfo("配置文件已获取", f"已从在线源获取配置文件：\n{self.config_path}")
                    return new_config
                except Exception as e:
                    last_error = str(e)
            messagebox.showwarning("配置文件获取失败", f"在线获取配置失败，将使用默认配置。\n错误信息：{last_error}\n配置文件位置：{self.config_path}")

        # 本地有配置文件，检查版本号
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                local_config = json.load(f)
                self._validate_config(local_config)
        except (json.JSONDecodeError, PermissionError) as e:
            raise RuntimeError(f"配置文件错误: {str(e)}")

        local_version = get_version(local_config)
        server_config = None
        server_version = local_version

        # 检查服务器版本
        for url in UPDATE_URLS:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                remote_config = response.json()
                self._validate_config(remote_config)
                remote_version = get_version(remote_config)
                if remote_config == local_config:
                    messagebox.showinfo("配置检查", "本地配置已是最新，无需更新。")
                    return local_config
                if self._compare_version(remote_version, local_version) > 0:
                    server_config = remote_config
                    server_version = remote_version
                    break
            except Exception:
                continue

        if server_config:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(server_config, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("配置已更新", f"检测到新版本配置，已自动更新到 v{server_version}")
            return server_config

        return local_config

    @staticmethod
    def _compare_version(v1, v2):
        """比较两个版本号字符串 v1 > v2 返回1，等于返回0，小于返回-1"""
        def parse(v):
            return [int(x) for x in v.split('.')]
        a, b = parse(v1), parse(v2)
        for i in range(max(len(a), len(b))):
            ai = a[i] if i < len(a) else 0
            bi = b[i] if i < len(b) else 0
            if ai > bi:
                return 1
            elif ai < bi:
                return -1
        return 0

    def update_config_from_url(self, url: str):
        """从指定URL更新配置文件"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            new_config = response.json()
            self._validate_config(new_config)
            # 检查内容是否完全一致
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    local_config = json.load(f)
                if new_config == local_config:
                    messagebox.showinfo("配置检查", "本地配置已是最新，无需更新。")
                    return False
            # 保存新配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=2)
            self.config = new_config
            return True
        except Exception as e:
            raise RuntimeError(f"配置更新失败 {str(e)}")

    def __init__(self):
        self.script_dir = Path(os.path.dirname(os.path.abspath(sys.argv[0])))
        self.config_path = self.script_dir / "hd2rd_config.json"
        self.config = self._load_or_create_config()

    def _validate_config(self, config: Dict):
        required = {
            "strategems": ["patriotic-administration-center", "orbital-cannons", "hangar", "bridge", "engineering-bay", "robotics-workshop", "chemical-agents", "urban-lehends", "servants-of-freedom", "other"],
            "weapons": ["primary", "secondary", "grenades"],
            "armors": ["light", "medium", "heavy"],
            "enhancements": []
        }
        for section, keys in required.items():
            if section not in config:
                raise ValueError(f"配置缺少必须部分: {section}")
            for key in keys:
                if key not in config[section]:
                    raise ValueError(f"{section} 缺少必要字段: {key}")

    def generate_batch(self, config: ConfigManager, avoid_duplicate=True) -> List[Loadout]:
        loadouts = []
        seen = set()
        
        for _ in range(config.batch_size):
            retry = 0
            while True:
                loadout = self._generate_single(config.excludes)
                sig = (
                    f"{sorted(loadout.strategems)}"
                    f"{loadout.primary}"
                    f"{loadout.primary_attachment}"
                    f"{loadout.secondary}"
                    f"{loadout.grenade}"
                    f"{loadout.armor}"
                    f"{loadout.enhancement}"
                )
                if not avoid_duplicate or sig not in seen:
                    seen.add(sig)
                    loadouts.append(loadout)
                    break
                retry += 1
                if retry > 100:
                    raise RuntimeError("无法生成足够独特的配置")
        return loadouts

    def _random_choice(self, items: List, excludes: List, category: str) -> str:
        available = [i for i in items if i not in excludes]
        if not available:
            category_name = {
                "strategems": "战略配备",
                "weapons": "武器",
                "armors": "护甲",
                "enhancements": "强化"
            }[category]
            raise ValueError(f"没有可用的{category_name}选项，请调整排除设置")
        return random.choice(available)

    def _generate_single(self, excludes: Dict) -> Loadout:
        all_strat = [s for cat in self.config["strategems"].values() for s in cat]
        available_strat = [s for s in all_strat if s not in excludes["strategems"]]
        if len(available_strat) < 4:
            raise ValueError("可用的战略配备不足，请减少排除项")
        strats = random.sample(available_strat, 4)

        # 主武器
        primary_weapon_obj = random.choice([
            w for w in self.config["weapons"]["primary"]
            if w["name"] not in excludes["primary"]
        ])
        primary = primary_weapon_obj["name"]
        attachments_dict = primary_weapon_obj.get("attachments", {})
        primary_attachment = []
        for cat in ["准镜", "下挂", "枪囗", "弹匣"]:
            options = attachments_dict.get(cat, [])
            if options:
                primary_attachment.append(f"{cat}:{random.choice(options)}")
        primary_attachment_str = "，".join(primary_attachment) if primary_attachment else "无"

        # 副武器
        secondary = self._random_choice(
            self.config["weapons"]["secondary"],
            excludes["secondary"],
            "weapons"
        )
        while primary == secondary:
            secondary = self._random_choice(
                self.config["weapons"]["secondary"],
                excludes["secondary"],
                "weapons"
            )

        # 合并所有分组下的护甲
        all_armors = [armor for group in self.config["armors"].values() for armor in group]
        armor = self._random_choice(
            all_armors,
            excludes["armors"],
            "armors"
        )

        return Loadout(
            strategems=strats,
            primary=primary,
            primary_attachment=primary_attachment_str,
            secondary=secondary,
            grenade=self._random_choice(
                self.config["weapons"]["grenades"],
                excludes["grenades"],
                "weapons"
            ),
            armor=armor,  # 这里是具体护甲名
            enhancement=self._random_choice(
                self.config["enhancements"],
                excludes["enhancements"],
                "enhancements"
            )
        )

class LoadoutApp(ttk.Window):
    def __init__(self):
        super().__init__(themename="cosmo")
        self.title("HD2随机装备配置")
        self.geometry("800x600")
        self.config_manager = ConfigManager()
        self.exclude_vars = {}
        self.CATEGORY_MAP = {
            "战略配备": "strategems",
            "主武器": "primary",
            "副武器": "secondary",
            "投掷物": "grenades",
            "护甲": "armors",
            "强化": "enhancements"
        }
        self.batch_size_var = tk.IntVar(value=1)
        self.avoid_duplicate_var = tk.BooleanVar(value=True)  # 新增变量
        self.update_thread = None
        self.current_url_index = 0
        
        try:
            self.generator = LoadoutGenerator()
            self._create_ui()
        except Exception as e:
            messagebox.showerror("初始化失败", str(e))
            self.destroy()

    def _create_ui(self):
        menu_bar = tk.Menu(self)
        config_menu = tk.Menu(menu_bar, tearoff=0)
        config_menu.add_command(label="打开配置文件所在位置", command=self._open_config_file)
        config_menu.add_command(label="排除战略配备/武器/盔甲被动/强化", command=self.show_settings)
        config_menu.add_command(label="在线更新配置文件", command=self._start_config_update)
        menu_bar.add_cascade(label="配置", menu=config_menu)
        self.configure(menu=menu_bar)

        main_frame = ttk.Frame(self)
        main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)

        # 新增：避免重复组合勾选框
        avoid_cb = ttk.Checkbutton(
            control_frame,
            text="避免重复组合",
            variable=self.avoid_duplicate_var
        )
        avoid_cb.pack(side=tk.LEFT, padx=5)

        generate_button = ttk.Button(
            main_frame, 
            text="生成随机配置", 
            command=self.generate,
        )
        generate_button.pack(pady=20)

        batch_combo = ttk.Combobox(
            control_frame,
            textvariable=self.batch_size_var,
            values=["1", "3", "5", "10"],
            width=4,
            state="readonly"
        )
        ttk.Label(control_frame, text="生成次数:").pack(side=tk.LEFT, padx=5)
        batch_combo.pack(side=tk.LEFT, padx=5)

        self.result_text = tk.Text(
            main_frame, 
            height=25, 
            width=80, 
            font=("Consolas", 10), 
            wrap=tk.WORD
        )
        self.result_text.pack(fill=tk.BOTH, expand=True)
    
    def _start_config_update(self):
        """启动自动更新流程"""
        self._show_loading("正在检查更新...")
        self.update_thread = threading.Thread(target=self._try_update_config)
        self.update_thread.start()

    def _try_update_config(self):
        """尝试从多个源更新配置"""
        success = False
        last_error = "未知错误"
        while self.current_url_index < len(UPDATE_URLS):
            url = UPDATE_URLS[self.current_url_index]
            try:
                if self.generator.update_config_from_url(url):
                    success = True
                    break
                    break
            except requests.exceptions.RequestException as e:
                last_error = f"网络错误 {str(e)}"
            except json.JSONDecodeError as e:
                last_error = f"配置文件格式错误 {str(e)}"
            except ValueError as e:
                last_error = f"配置验证失败 {str(e)}"
            except Exception as e:
                last_error = f"意外错误 {str(e)}"
            finally:
                self.current_url_index += 1  # 切换到下一个源
        
        if success:
            self.after(0, lambda: messagebox.showinfo("成功", "配置已更新"))
        else:
            error_msg = f"所有更新源均不可用\n{last_error}"
            self.after(0, lambda: messagebox.showerror("更新失败", error_msg))
        self.after(0, self._hide_loading)

    def _update_config(self, url: str):
        """后台线程执行更新"""
        try:
            success = self.generator.update_config_from_url(url)
            if success:
                self.after(0, lambda: messagebox.showinfo("成功", "配置已更新并重新加载"))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("更新错误", str(e)))
        finally:
            self.after(0, self._hide_loading)

    def _show_loading(self, message: str):
        """显示加载状态"""
        self.loading_window = tk.Toplevel(self)
        self.loading_window.title("请稍候")
        
        ttk.Label(self.loading_window, text=message).pack(padx=20, pady=10)
        self.loading_window.grab_set()
        self.loading_window.transient(self)
        self.loading_window.update()

    def _hide_loading(self):
        """隐藏加载状态"""
        if hasattr(self, 'loading_window'):
            self.loading_window.destroy()


    def show_settings(self):
        if hasattr(self, 'settings_win') and self.settings_win.winfo_exists():
            self.settings_win.lift()
            return

        self.settings_win = ttk.Toplevel()
        self.settings_win.title("排除设置")
        self._build_settings_ui()

    def _build_settings_ui(self):
        # 优先读取本地排除设置
        excludes_path = Path(os.path.dirname(os.path.abspath(sys.argv[0]))) / "hd2rd_excludes.json"
        if excludes_path.exists():
            try:
                with open(excludes_path, "r", encoding="utf-8") as f:
                    self.config_manager.excludes = json.load(f)
            except Exception:
                pass  # 读取失败则忽略，继续用默认

        notebook = ttk.Notebook(self.settings_win)
        
        strat_tab = self._create_exclude_tab(
            notebook, "战略配备", 
            [s for cat in self.generator.config["strategems"].values() for s in cat]
        )
        primary_tab = self._create_exclude_tab(
            notebook, "主武器",
            [w["name"] for w in self.generator.config["weapons"]["primary"]]
        )
        secondary_tab = self._create_exclude_tab(
            notebook, "副武器",
            self.generator.config["weapons"]["secondary"]
        )
        grenade_tab = self._create_exclude_tab(
            notebook, "投掷物",
            self.generator.config["weapons"]["grenades"]
        )
        armor_tab = self._create_exclude_tab(
            notebook, "护甲",
            [s for cat in self.generator.config["armors"].values() for s in cat]
        )
        enhance_tab = self._create_exclude_tab(
            notebook, "强化",
            self.generator.config["enhancements"]
        )

        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        save_button = ttk.Button(
            self.settings_win, 
            text="保存设置", 
            command=self._save_settings,
        )
        save_button.pack(pady=10)

    def _create_exclude_tab(self, parent, title, items):
        tab = ttk.Frame(parent)
        parent.add(tab, text=title)
        
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        config_key = self.CATEGORY_MAP[title]
        self.exclude_vars[title] = {}
        for item in items:
            var = tk.BooleanVar(value=item in self.config_manager.excludes.get(config_key, []))
            frame = ttk.Frame(scroll_frame)
            frame.pack(anchor="w", fill="x")
            cb = ttk.Checkbutton(
                frame,
                text=item,
                variable=var,
            )
            cb.pack(side="left")
            self.exclude_vars[title][item] = var

            # 主武器增加配件排除按钮
            if title == "主武器":
                btn = ttk.Button(
                    frame,
                    text="设置配件排除",
                    command=lambda wname=item: self._show_attachment_exclude(wname)
                )
                btn.pack(side="left", padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tab

    def _show_attachment_exclude(self, weapon_name):
        # 查找该武器的配件
        weapon_obj = next(
            (w for w in self.generator.config["weapons"]["primary"] if w["name"] == weapon_name),
            None
        )
        if not weapon_obj:
            messagebox.showerror("错误", f"未找到武器：{weapon_name}")
            return

        win = tk.Toplevel(self)
        win.title(f"{weapon_name} 配件排除")
        win.geometry("350x400")

        # 读取已排除的配件
        excludes = self.config_manager.excludes.get("primary_attachments", {})
        if not isinstance(excludes, dict):
            excludes = {}
        selected = set(excludes.get(weapon_name, []))
        self.attachment_vars = {}

        row = 0
        for cat, options in weapon_obj.get("attachments", {}).items():
            ttk.Label(win, text=cat).grid(row=row, column=0, sticky="w", pady=2)
            row += 1
            for opt in options:
                var = tk.BooleanVar(value=opt in selected)
                cb = ttk.Checkbutton(win, text=opt, variable=var)
                cb.grid(row=row, column=0, sticky="w", padx=20)
                self.attachment_vars.setdefault(weapon_name, {})[f"{cat}:{opt}"] = var
                row += 1

        def save():
            checked = []
            for key, var in self.attachment_vars.get(weapon_name, {}).items():
                if var.get():
                    checked.append(key)
            # 更新到 excludes
            all_excludes = self.config_manager.excludes.get("primary_attachments", {})
            all_excludes[weapon_name] = checked
            self.config_manager.excludes["primary_attachments"] = all_excludes
            win.destroy()

        ttk.Button(win, text="保存", command=save).grid(row=row, column=0, pady=10)

    def _save_settings(self):
        try:
            new_excludes = {
                "strategems": [k for k,v in self.exclude_vars["战略配备"].items() if v.get()],
                "primary": [k for k,v in self.exclude_vars["主武器"].items() if v.get()],
                "secondary": [k for k,v in self.exclude_vars["副武器"].items() if v.get()],
                "grenades": [k for k,v in self.exclude_vars["投掷物"].items() if v.get()],
                "armors": [k for k,v in self.exclude_vars["护甲"].items() if v.get()],
                "enhancements": [k for k,v in self.exclude_vars["强化"].items() if v.get()]
            }

            error_msgs = []
            category_names = {
                "strategems": "战略配备",
                "primary": "主武器",
                "secondary": "副武器",
                "grenades": "投掷物",
                "armors": "护甲",
                "enhancements": "强化"
            }

            # 你可以分别设置每类最大排除数
            max_excludes = {
                "strategems": 99,
                "primary": 99,
                "secondary": 99,
                "grenades": 99,
                "armors": 99,
                "enhancements": 99
            }

            for category in new_excludes:
                max_allowed = max_excludes[category]
                current_count = len(new_excludes[category])
                if current_count > max_allowed:
                    error_msgs.append(
                        f"{category_names[category]}最多排除{max_allowed}个（当前：{current_count}）"
                    )

            if error_msgs:
                raise ValueError("\n".join(error_msgs))

            # 保留 primary_attachments 字段
            self.config_manager.excludes.update({
                "strategems": new_excludes["strategems"],
                "primary": new_excludes["primary"],
                "secondary": new_excludes["secondary"],
                "grenades": new_excludes["grenades"],
                "armors": new_excludes["armors"],
                "enhancements": new_excludes["enhancements"]
            })

            excludes_path = Path(os.path.dirname(os.path.abspath(sys.argv[0]))) / "hd2rd_excludes.json"
            with open(excludes_path, "w", encoding="utf-8") as f:
                json.dump(self.config_manager.excludes, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("成功", f"排除设置已保存\n文件位置：{excludes_path}")
        except Exception as e:
            messagebox.showerror("保存错误", str(e))

    def _open_config_file(self):
        try:
            if os.name == 'nt':
                os.startfile(self.generator.config_path.parent)
            #else:
            #    os.system(f'open "{self.generator.config_path.parent}"')
        except Exception as e:
            messagebox.showwarning("打开目录失败", f"无法打开文件目录：\n{str(e)}")

    def generate(self):
        try:
            self.config_manager.batch_size = self.batch_size_var.get()
            if not 1 <= self.config_manager.batch_size <= 10:
                raise ValueError("生成次数需在1-10之间")

            self.result_text.delete(1.0, tk.END)
            # 传递是否避免重复
            loadouts = self.generator.generate_batch(self.config_manager, avoid_duplicate=self.avoid_duplicate_var.get())
            
            output = []
            separator = "\n" + "═"*60 + "\n"
            output = [f"=== 已生成 {len(loadouts)} 种配置 ==="]
            for i, loadout in enumerate(loadouts, 1):
                output.append(f"\n[配置] #{i}")
                output.append("[战略配备]")
                output.extend(f"- {s}" for s in loadout.strategems)
                output.append("\n[武器]")
                output.append(f"主武器：{loadout.primary}")
                output.append(f"主武器配件：{loadout.primary_attachment}")
                output.append(f"副武器：{loadout.secondary}")
                output.append(f"投掷物：{loadout.grenade}")
                output.append("\n[盔甲被动]")
                output.append(f"盔甲被动加成：{loadout.armor}")
                output.append("\n[强化]")
                output.append(f"强化：{loadout.enhancement}")
                output.append(separator)
            
            self.result_text.insert(tk.END, "\n".join(output).rstrip(separator))
        except Exception as e:
            messagebox.showerror("生成错误", str(e))

if __name__ == "__main__":
    app = LoadoutApp()
    app.mainloop()