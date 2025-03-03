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

DEFAULT_CONFIG = {
    "strategems": {
    "patriotic-administration-center": [
      "机枪",
      "盟友",
      "重机枪",
      "反器材步枪",
      "消耗性反坦克武器",
      "无后坐力步枪",
      "火焰喷射器",
      "机炮",
      "空爆火箭弹发射器",
      "突击兵",
      "磁轨炮",
      "飞矛",
      "StA-X3 W.A.S.P.发射器"
    ],
    "orbital-cannons": [
      "轨道空爆攻击",
      "轨道激光炮",
      "轨道炮攻击",
      "轨道游走火力网",
      "轨道加特林火力网",
      "轨道凝固汽油弹火力网",
      "轨道120MM高爆弹火力网",
      "轨道380MM高爆弹火力网"
    ],
    "hangar": [
      "“飞鹰”机枪扫射",
      "“飞鹰”空袭",
      "“飞鹰”集束炸弹",
      "“飞鹰”凝固汽油弹空袭",
      "“飞鹰”烟雾攻击",
      "“飞鹰”110MM火箭巢",
      "“飞鹰”500KG炸弹",
      "喷射肯包",
      "快速侦察载具"
    ],
    "bridge": [
      "轨道精准攻击",
      "轨道毒气攻击",
      "轨道电磁冲击波攻击",
      "轨道烟雾攻击",
      "重机枪部署支架",
      "防护罩生成中继器",
      "特斯拉塔"
    ],
    "engineering-bay":[
      "补给背包",
      "榴弹发射器",
      "激光大炮",
      "“护卫犬”漫游车",
      "防弹护盾肖包",
      "电弧发射器",
      "反坦克地雷",
      "燃烧地雷",
      "反步兵地雷",
      "类星体加衣炮",
      "防护罩生成包",
      "毒气地雷"
    ],
    "robotics-workshop":[
      "哨戒机枪",
      "加特林哨戒炮",
      "迫击哨戒炮",
      "“护卫犬”",
      "自动哨戒炮",
      "火箭哨戒炮",
      "电磁冲击波迫击哨戒炮",
      "“爱国者”外骨骼装甲",
      "“解放者”外骨骼装甲"
    ],
    "chemical-agents":[
      "灭菌器",
      "“护卫犬”腐息"
    ],
    "urban-lehends":[
      "定向护盾",
      "火焰喷射哨戒炮",
      "反坦克炮台"
    ],
    "servants-of-freedom":[
      "便携式地狱火炸弹"
    ]
  },
  "weapons": {
    "primary": [
      "AR-23解放者",
      "AR-23P穿甲解放者",
      "AR-23C震荡解放者",
      "AR-61肉锤",
      "AR-23A“解放者”卡宾枪",
      "R-63勤勉",
      "R-63CS反狙击“勤勉”",
      "SMG-37防卫者",
      "SMG-72暴击斗土",
      "SMG-32训斤",
      "SG-8制裁者",
      "SG-8S重炮手",
      "SG-8P等离子”制裁者”",
      "SG-451野炊",
      "SG-225破裂者",
      "SG-225SP弥漫于祷告”破裂者”",
      "SG-225IE高燃”破裂者”",
      "SG-20止息",
      "R-36爆裂铳",
      "R-2124宪法"
      "LAS-5C长柄镰",
      "LAS-16镰刀",
      "LAS-17双刃镰刀",
      "PLAS-39加速步枪",
      "PLAS-1焦土",
      "PLAS-101净化者",
      "ARC-12雷霆",
      "FLAM-66火炬手",
      "StA-11冲锋枪",
      "StA-52突击步枪",
      "BR-14审判者",
      "CB-9爆燃弩",
      "JAR-5主宰",
      "MP-98骑士"
    ],
    "secondary": [
      "P-2和平制造者",
      "P-19救世主",
      "P-4参议员",
      "P-113裁决",
      "P-72迅击",
      "P-11治疗剂手枪",
      "LAS-7匕首",
      "PLAS-15忠诚者",
      "GP-31榴弹手枪",
      "GP-31最后通牒",
      "CQC-19眩晕长矛",
      "CQC-30眩晕短棍",
      "CQC-5战斗短柄斧",
      "SG-22游击兵"
    ],
    "grenades": [
      "G-6破片手雷",
      "G-12高爆弹",
      "G-10燃烧弹",
      "G-16冲击弹",
      "G-23眩晕弹",
      "G-3烟雾弹",
      "G-123铝热弹",
      "G-13燃烧冲击弹",
      "G-4毒气榴弹",
      "K-2飞刀"
    ]
  },
  "enhancements": [
    "生命力强化",
    "耐力强化",
    "肌肉强化",
    "UAV侦察强化资源",
    "提高増援预箅",
    "灵活增援预算",
    "绝地喧射舱空间优化",
    "定位混淆",
    "专业撤离飞行员",
    "激励性冲击",
    "试验性注射剂",
    "火焰炸弹绝地喷射舱",
    "死亡冲刺",
    "武装重新补给舱"
  ],
  "armors": [
    "工程包(轻甲)",
    "强化(轻甲)",
    "电路导管(轻甲)",
    "伺服辅助(轻甲)",
    "急救包(轻甲)",
    "额外垫料(轻甲)",
    "侦察(轻甲)",
    "集成炸药(轻甲)",
    "毫不畏缩(轻甲)",
    "蓄势出击(轻甲)",
    "易燃易爆(轻甲)",
    "应变自如(轻甲)",
    "高级过能力(轻甲)",
    "健壮体格(轻甲)",
    
    "工程包(中甲)",
    "强化(中甲)",
    "电路导管(中甲)",
    "伺服辅助(中甲)",
    "急救包(中甲)",
    "额外垫料(中甲)",
    "侦察(中甲)",
    "集成炸药(中甲)",
    "毫不畏缩(中甲)",
    "易燃易爆(中甲)",
    "应变自如(中甲)",
    "高级过能力(中甲)",
    "健壮体格(中甲)",

    "工程包(重甲)",
    "强化(重甲)",
    "伺服辅助(重甲)",
    "急救包(重甲)",
    "额外垫料(重甲)",
    "蓄势出击(重甲)",
    "易燃易爆(重甲)",
    "高级过能力(重甲)",
    "健壮体格(重甲)"
  ]
}

@dataclass
class Loadout:
    strategems: List[str]
    primary: str
    secondary: str
    grenade: str
    armor: str
    enhancement: str

class ConfigManager:
    def __init__(self):
        self.excludes = {
            "strategems": [],
            "weapons": [],
            "armors": [],
            "enhancements": []
        }
        self.max_excludes = {
            "strategems": 10,
            "weapons": 15,
            "armors": 5,
            "enhancements": 5
        }
        self.batch_size = 1

class LoadoutGenerator:
    # 在现有类中添加以下方法
    def update_config_from_url(self, url: str):
        """从指定URL更新配置文件"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # 验证配置格式
            new_config = response.json()
            self._validate_config(new_config)
            
            # 保存新配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, ensure_ascii=False, indent=2)
            
            # 重新加载配置
            self.config = new_config
            return True
        except Exception as e:
            raise RuntimeError(f"配置更新失败: {str(e)}")

    def __init__(self):
        self.script_dir = Path(os.path.dirname(os.path.abspath(sys.argv[0])))
        self.config_path = self.script_dir / "hd2_config.json"
        self.config = self._load_or_create_config()

    def _load_or_create_config(self) -> Dict:
        if not self.config_path.exists():
            self._create_default_config()
            messagebox.showinfo("配置文件已创建", f"默认配置文件已生成在：\n{self.config_path}\n请根据需要修改")

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self._validate_config(config)
                return config
        except (json.JSONDecodeError, PermissionError) as e:
            raise RuntimeError(f"配置文件错误: {str(e)}")

    def _create_default_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
        except PermissionError:
            raise RuntimeError("无权限创建配置文件，请检查目录权限")
        except Exception as e:
            raise RuntimeError(f"创建配置文件失败: {str(e)}")

    def _validate_config(self, config: Dict):
        required = {
            "strategems": ["patriotic-administration-center", "orbital-cannons", "hangar", "bridge", "engineering-bay", "robotics-workshop", "chemical-agents", "urban-lehends", "servants-of-freedom"],
            "weapons": ["primary", "secondary", "grenades"],
            "armors": [],
            "enhancements": []
        }
        for section, keys in required.items():
            if section not in config:
                raise ValueError(f"配置缺少必须部分: {section}")
            for key in keys:
                if key not in config[section]:
                    raise ValueError(f"{section} 缺少必要字段: {key}")

    def generate_batch(self, config: ConfigManager) -> List[Loadout]:
        loadouts = []
        seen = set()
        
        for _ in range(config.batch_size):
            while True:
                loadout = self._generate_single(config.excludes)
                sig = f"{sorted(loadout.strategems)}{loadout.primary}{loadout.secondary}"
                if sig not in seen:
                    seen.add(sig)
                    loadouts.append(loadout)
                    break
                if len(seen) > 100:
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

        primary = self._random_choice(
            self.config["weapons"]["primary"], 
            excludes["weapons"],
            "weapons"
        )
        secondary = self._random_choice(
            self.config["weapons"]["secondary"], 
            excludes["weapons"],
            "weapons"
        )
        while primary == secondary:
            secondary = self._random_choice(
                self.config["weapons"]["secondary"], 
                excludes["weapons"],
                "weapons"
            )

        return Loadout(
            strategems=strats,
            primary=primary,
            secondary=secondary,
            grenade=self._random_choice(
                self.config["weapons"]["grenades"], 
                excludes["weapons"],
                "weapons"
            ),
            armor=self._random_choice(
                self.config["armors"], 
                excludes["armors"],
                "armors"
            ),
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
            "武器": "weapons",
            "护甲": "armors",
            "强化": "enhancements"
        }
        self.batch_size_var = tk.IntVar(value=1)
        self.update_thread = None  # 用于后台更新
        
        try:
            self.generator = LoadoutGenerator()
            self._create_ui()
        except Exception as e:
            messagebox.showerror("初始化失败", str(e))
            self.destroy()

        # 内置更新源列表
        self.update_urls = [
            "https://ts.tyhh10.xyz:58092/hd2_config.json"
            "https://raw.githubusercontent.com/TYHH100/HD2Random/refs/heads/master/hd2_config.json"
        ]
        self.current_url_index = 0

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
        last_error = None
        
        while self.current_url_index < len(self.update_urls):
            url = self.update_urls[self.current_url_index]
            try:
                if self.generator.update_config_from_url(url):
                    success = True
                    break
            except Exception as e:
                last_error = str(e)
                self.current_url_index += 1  # 切换到下一个源
        
        if success:
            self.after(0, lambda: messagebox.showinfo("成功", "配置已更新"))
        else:
            error_msg = f"所有更新源均不可用\n最后错误：{last_error}"
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
        notebook = ttk.Notebook(self.settings_win)
        
        strat_tab = self._create_exclude_tab(
            notebook, "战略配备", 
            [s for cat in self.generator.config["strategems"].values() for s in cat]
        )
        
        weapon_tab = self._create_exclude_tab(
            notebook,
            "武器",
            self.generator.config["weapons"]["primary"] +
            self.generator.config["weapons"]["secondary"] +
            self.generator.config["weapons"]["grenades"]
        )
        
        armor_tab = self._create_exclude_tab(
            notebook,
            "护甲",
            self.generator.config["armors"]
        )
        
        enhance_tab = self._create_exclude_tab(
            notebook,
            "强化",
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
            var = tk.BooleanVar(value=item in self.config_manager.excludes[config_key])
            cb = ttk.Checkbutton(
                scroll_frame,
                text=item,
                variable=var,
            )
            cb.pack(anchor="w")
            self.exclude_vars[title][item] = var
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        return tab

    def _save_settings(self):
        try:
            new_excludes = {
                "strategems": [k for k,v in self.exclude_vars["战略配备"].items() if v.get()],
                "weapons": [k for k,v in self.exclude_vars["武器"].items() if v.get()],
                "armors": [k for k,v in self.exclude_vars["护甲"].items() if v.get()],
                "enhancements": [k for k,v in self.exclude_vars["强化"].items() if v.get()]
            }
            
            error_msgs = []
            category_names = {
                "strategems": "战略配备",
                "weapons": "武器",
                "armors": "护甲",
                "enhancements": "强化"
            }
            
            for category in new_excludes:
                max_allowed = self.config_manager.max_excludes[category]
                current_count = len(new_excludes[category])
                if current_count > max_allowed:
                    error_msgs.append(
                        f"{category_names[category]}最多排除{max_allowed}个（当前：{current_count}）"
                    )
            
            if error_msgs:
                raise ValueError("\n".join(error_msgs))
            
            self.config_manager.excludes = new_excludes
            messagebox.showinfo("成功", "排除设置已保存")
        except Exception as e:
            messagebox.showerror("保存错误", str(e))

    def _open_config_file(self):
        try:
            if os.name == 'nt':
                os.startfile(self.generator.config_path.parent)
            else:
                os.system(f'open "{self.generator.config_path.parent}"')
        except Exception as e:
            messagebox.showwarning("打开目录失败", f"无法打开文件目录：\n{str(e)}")

    def generate(self):
        try:
            self.generator = LoadoutGenerator()
            self.config_manager.batch_size = self.batch_size_var.get()
            if not 1 <= self.config_manager.batch_size <= 10:
                raise ValueError("生成次数需在1-10之间")

            self.result_text.delete(1.0, tk.END)
            loadouts = self.generator.generate_batch(self.config_manager)
            
            output = []
            separator = "\n" + "═"*60 + "\n"
            output = [f"=== 已生成 {len(loadouts)} 种配置 ==="]
            for i, loadout in enumerate(loadouts, 1):
                output.append(f"\n[配置] #{i}")
                output.append("[战略配备]")
                output.extend(f"- {s}" for s in loadout.strategems)
                output.append("\n[武器]")
                output.append(f"主武器：{loadout.primary}")
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