import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import os
import json


class SeatingChartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("座位选择系统")
        self.groups = {}
        self.num_row = 0
        self.num_cell = 0

        with open(".\\settings.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            self.groups = data.get("groups", self.groups)
            self.num_row = data.get("num_row", self.num_row)
            self.num_cell = data.get("num_cell", self.num_cell)

        self.seats = [["" for _ in range(self.num_cell)] for _ in range(self.num_row)]
        self.group_colors = {
            "group1": "lightblue",
            "group2": "lightgreen",
            "group3": "lightcoral",
            "group4": "lightgoldenrod",
            "group5": "lightpink",
            "group6": "lightseagreen",
            "group7": "lightsalmon",
            "group8": "lightsteelblue",
        }
        self.group_selections = {}
        self.assigned_seats = {}
        self.leader_mode = {}  # 用于跟踪组长的选择模式

        self.load_seating_data()
        self.create_widgets()

    def create_widgets(self):
        self.name_label = tk.Label(self.root, text="姓名:")
        self.name_label.grid(row=0, column=0)
        self.name_entry = tk.Entry(self.root)
        self.name_entry.grid(row=0, column=1)

        self.select_button = tk.Button(
            self.root, text="选择座位", command=self.select_seat
        )
        self.select_button.grid(row=1, column=0, columnspan=2)

        self.clear_button = tk.Button(
            self.root, text="清空配置", command=self.clear_all
        )
        self.clear_button.grid(row=1, column=2, columnspan=2)

        self.seat_buttons = [
            [None for _ in range(self.num_cell)] for _ in range(self.num_row)
        ]
        for r in range(self.num_row):
            for c in range(self.num_cell):
                self.seat_buttons[r][c] = tk.Button(
                    self.root,
                    text="空",
                    width=5,
                    command=lambda r=r, c=c: self.choose_seat(r, c),
                )
                self.seat_buttons[r][c].grid(row=r + 2, column=c)
                if self.seats[r][c]:
                    if self.seats[r][c] in self.groups:
                        group_name = self.seats[r][c]
                        name = group_name
                    else:
                        name = self.seats[r][c]
                        group_name = self.find_group(name)
                    self.seat_buttons[r][c].config(
                        bg=self.group_colors[group_name], text=name
                    )
        # 添加一个新按钮来显示未分配座位的成员
        self.show_unassigned_button = tk.Button(
            self.root, text="显示未分配座位", command=self.show_unassigned_members
        )
        self.show_unassigned_button.grid(row=1, column=4, columnspan=2)
        self.show_all_button = tk.Button(
            self.root, text="显示所有成员", command=self.show_all_members
        )
        self.show_all_button.grid(row=1, column=6, columnspan=2)

    def find_group(self, name):
        for group_name, members in self.groups.items():
            if name in members:
                return group_name
        return None

    def is_leader(self, group_name, name):
        return self.groups.get(group_name, [None])[0] == name

    def select_seat(self):
        name = self.name_entry.get()
        if not name:
            messagebox.showerror("错误", "请输入姓名")
            return

        group_name = self.find_group(name)
        if not group_name:
            messagebox.showerror("错误", "找不到该组")
            return

        if self.is_leader(group_name, name):
            if group_name not in self.group_selections:
                self.leader_mode[group_name] = True
                messagebox.showinfo("组长", "请先为组选择座位区域")
            else:
                self.leader_mode[group_name] = False
                messagebox.showinfo("组长", "请为自己选择座位")
        else:
            if group_name not in self.group_selections:
                messagebox.showerror("错误", "组长尚未选择区域")
            else:
                messagebox.showinfo("成员", "请在组区域内选择座位")

    def choose_seat(self, row, col):
        name = self.name_entry.get()
        if not name:
            messagebox.showerror("错误", "请输入姓名")
            return

        group_name = self.find_group(name)
        if not group_name:
            messagebox.showerror("错误", "找不到该组")
            return

        if self.is_leader(group_name, name) and self.leader_mode.get(group_name, True):
            if [row, col] in self.group_selections.get(group_name, []):
                # 取消选择
                self.group_selections[group_name].remove([row, col])
                self.seats[row][col] = ""
                self.seat_buttons[row][col].config(bg="SystemButtonFace", text="空")
                self.save_seating_data()
                messagebox.showinfo("取消", f"取消了位置 ({row}, {col})")
            else:
                if name in self.assigned_seats:
                    messagebox.showinfo(
                        "提示", f"{name} 已选择座位 ({self.assigned_seats[name]})"
                    )
                    return
                if self.seats[row][col] != "" and self.seats[row][col] != group_name:
                    messagebox.showerror("错误", "该位置已被其他组占用")
                    return

                if group_name not in self.group_selections:
                    self.group_selections[group_name] = []

                if len(self.group_selections[group_name]) < len(
                    self.groups[group_name]
                ):
                    self.group_selections[group_name].append([row, col])
                    self.seats[row][col] = group_name
                    self.seat_buttons[row][col].config(bg=self.group_colors[group_name])
                    self.save_seating_data()
                    # messagebox.showinfo("成功", f"组 {group_name} 选择了位置 ({row}, {col})")
                else:
                    messagebox.showinfo("提示", f"组 {group_name} 已选择所有位置")
                    self.leader_mode[group_name] = False
        else:
            if group_name in self.group_selections:
                if [row, col] in self.group_selections[group_name]:
                    if self.assigned_seats.get(name) == [row, col]:
                        # 取消选择
                        self.seats[row][col] = group_name
                        del self.assigned_seats[name]
                        self.seat_buttons[row][col].config(text="空")
                        self.save_seating_data()
                        messagebox.showinfo("取消", f"{name} 取消了座位 ({row}, {col})")
                    elif name in self.assigned_seats:
                        messagebox.showinfo(
                            "提示", f"{name} 已选择座位 ({self.assigned_seats[name]})"
                        )
                        return
                    elif self.seats[row][col] == group_name:
                        self.seats[row][col] = name
                        self.assigned_seats[name] = [row, col]
                        self.seat_buttons[row][col].config(text=name)
                        self.save_seating_data()
                        # messagebox.showinfo("成功", f"{name} 已选择座位 ({row}, {col})")
                    else:
                        messagebox.showerror("错误", "座位已被占用")
                else:
                    messagebox.showerror("错误", "座位不在组的区域内")
            else:
                messagebox.showerror("错误", "组区域尚未选择")

    def load_seating_data(self):
        if os.path.exists("seating_data.json"):
            with open("seating_data.json", "r") as file:
                data = json.load(file)
                self.seats = data.get("seats", self.seats)
                self.group_selections = data.get(
                    "group_selections", self.group_selections
                )
                self.assigned_seats = data.get("assigned_seats", self.assigned_seats)
                self.leader_mode = data.get("leader_mode", self.leader_mode)

    def save_seating_data(self):
        data = {
            "seats": self.seats,
            "group_selections": self.group_selections,
            "assigned_seats": self.assigned_seats,
            "leader_mode": self.leader_mode,
        }
        with open("seating_data.json", "w") as file:
            json.dump(data, file)
        self.update_html()

    def update_html(self):
        html_content = """<!DOCTYPE html>
<html lang="zh-CN">

<head>
    <meta charset="UTF-8">
    <title>教室座位表</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
            user-select: none;
        }

        th,
        td {
            border: 1px solid black;
            padding: 8px;
            text-align: center;
        }

        th {
            background-color: #f2f2f2;
        }
        
        input {
            width: 5rem;
            text-align: center;
        }
    </style>
</head>
    <body>
        <h1>座位选择结果</h1>
        <table border='1' id="seatingTable">
"""
        for r in range(self.num_row):
            html_content += f"\n        <tr>"
            for c in range(self.num_cell):
                seat = self.seats[r][c]
                html_content += f"\n            <td>{seat if seat else '空'}</td>"
            html_content += f"\n        </tr>"
        html_content += """        </tr>
    </table>
</body>
</html>
"""

        with open("main.html", "w", encoding="utf-8") as file:
            file.write(html_content)
        self.update_unassigned_members()

    def clear_all(self):
        if messagebox.askyesno("清空", "确定要清空所有配置吗？") == True:
            self.seats = [
                ["" for _ in range(self.num_cell)] for _ in range(self.num_row)
            ]
            self.group_selections.clear()
            self.assigned_seats.clear()
            self.leader_mode.clear()
            self.save_seating_data()
            self.update_seat_buttons()
            messagebox.showinfo("清空", "所有配置已清空")
        else:
            messagebox.showinfo("取消", "操作已取消")

    def update_seat_buttons(self):
        for r in range(self.num_row):
            for c in range(self.num_cell):
                self.seat_buttons[r][c].config(text="空", bg="SystemButtonFace")

    def show_unassigned_members(self):
        # 创建一个新的窗口来显示未分配座位的成员
        self.unassigned_window = tk.Toplevel(self.root)
        self.unassigned_window.title("未分配座位的成员")

        self.tree = ttk.Treeview(
            self.unassigned_window, columns=("Name",), show="headings"
        )
        self.tree.heading("Name", text="成员名称")
        yscrollbar = ttk.Scrollbar(
            self.unassigned_window, orient=tk.VERTICAL, command=self.tree.yview
        )
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=yscrollbar.set)
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # 绑定双击事件以设置输入框中的名称
        self.tree.bind(
            "<Double-1>", lambda event: self.set_name_to_entry(self.tree, event)
        )

        self.update_unassigned_members()

    def update_unassigned_members(self):

        # 清空 Treeview
        if self.tree:
            for item in self.tree.get_children():
                self.tree.delete(item)

        # 添加数据到 Treeview
        for i in range(1, 9):
            group_name = f"group{i}"
            if group_name in self.groups:
                members = self.groups[group_name]
                # 检查哪些成员还没有被分配座位
                unassigned_members = [
                    member for member in members if member not in self.assigned_seats
                ]
                if unassigned_members:
                    # 添加组标题
                    group_item = self.tree.insert(
                        "",
                        "end",
                        text=group_name,
                        values=(f"{self.groups.get(group_name)[0]}组",),
                        tags=("group",),
                    )
                    self.tree.tag_configure(
                        "group",
                        font=("Arial", 10, "bold"),
                        foreground="blue",
                    )
                    self.tree.item(group_item, open=True)  # 默认展开组

                    # 添加未分配座位的成员
                    for member in unassigned_members:
                        # 判断是否为组长
                        if self.is_leader(group_name, member):
                            self.tree.insert(
                                group_item,
                                "end",
                                text="",
                                values=(member,),
                                tags=("leader",),
                            )
                        else:
                            self.tree.insert(
                                group_item,
                                "end",
                                text="",
                                values=(member,),
                                tags=("member",),
                            )

                    # 配置字体样式
                    self.tree.tag_configure("leader", font=("Arial", 10, "bold"))
                    self.tree.tag_configure("member", font=("Arial", 10))

        # 绑定双击事件
        self.tree.bind("<Double-1>", self.on_double_click)

    def show_all_members(self):
        # 创建一个新的窗口来显示所有成员
        self.all_members_window = tk.Toplevel(self.root)
        self.all_members_window.title("所有成员")

        self.tree = ttk.Treeview(
            self.all_members_window, columns=("Name",), show="headings"
        )
        self.tree.heading("Name", text="成员名称")
        yscrollbar = ttk.Scrollbar(
            self.all_members_window, orient=tk.VERTICAL, command=self.tree.yview
        )
        yscrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=yscrollbar.set)
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # 绑定双击事件以设置输入框中的名称
        self.tree.bind(
            "<Double-1>", lambda event: self.on_double_click(self.tree, event)
        )

        # 清空 Treeview
        if self.tree:
            for item in self.tree.get_children():
                self.tree.delete(item)

        # 添加数据到 Treeview
        for i in range(len(self.groups)):
            group_name = f"group{i}"
            if group_name in self.groups:
                members = self.groups[group_name]
                # 添加组标题
                group_item = self.tree.insert(
                    "",
                    "end",
                    text=group_name,
                    values=(f"{self.groups.get(group_name)[0]}组",),
                    tags=("group",),
                )
                self.tree.tag_configure(
                    "group",
                    font=("Arial", 10, "bold"),
                    foreground="blue",
                )
                self.tree.item(group_item, open=True)  # 默认展开组

                # 添加所有成员
                for member in members:
                    # 判断是否为组长
                    if self.is_leader(group_name, member):
                        self.tree.insert(
                            group_item,
                            "end",
                            text="",
                            values=(member,),
                            tags=("leader",),
                        )
                    else:
                        self.tree.insert(
                            group_item,
                            "end",
                            text="",
                            values=(member,),
                            tags=("member",),
                        )

                # 配置字体样式
                self.tree.tag_configure("leader", font=("Arial", 10, "bold"))
                self.tree.tag_configure("member", font=("Arial", 10))

        # 绑定双击事件
        self.tree.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            tags = self.tree.item(item)["tags"]
            values = self.tree.item(item)["values"]
            if values and tags and len(tags) > 0:
                if tags[0] != "group":
                    self.name_entry.delete(0, tk.END)
                    self.name_entry.insert(0, values[0])


if __name__ == "__main__":
    root = tk.Tk()
    app = SeatingChartApp(root)
    root.mainloop()
