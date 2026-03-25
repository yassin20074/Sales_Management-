import os
import platform
import csv
import matplotlib.pyplot as plt
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.clock import Clock

import database
import pdf_report

# نافذة التنبيهات
def show_popup(title, message):
    popup = Popup(title=title, content=Label(text=message, halign="center"), size_hint=(0.8, 0.4))
    popup.open()

# --- 1. شاشة الترحيب ---
class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.switch_to_main, 3)
    def switch_to_main(self, dt):
        self.manager.current = 'inv'
    def __init__(self, **kw):
        super().__init__(**kw)
        layout = BoxLayout(orientation='vertical', padding=50)
        layout.add_widget(Label(text="SMART POS SYSTEM", font_size='32sp', bold=True, color=(0, 0.7, 1, 1)))
        layout.add_widget(Label(text="Loading...", font_size='14sp', color=(0.5, 0.5, 0.5, 1)))
        self.add_widget(layout)

# --- 2. شاشة المخزون ---
class InventoryManagerScreen(Screen):
    def on_enter(self): self.refresh_list()
    def refresh_list(self):
        self.clear_widgets()
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # نموذج الإدخال
        input_area = GridLayout(cols=2, size_hint_y=None, height=160, spacing=5)
        self.txt_id = TextInput(hint_text="Auto ID", readonly=True, multiline=False)
        self.txt_name = TextInput(hint_text="Product Name", multiline=False)
        self.txt_price = TextInput(hint_text="Price", input_filter='float', multiline=False)
        self.txt_qty = TextInput(hint_text="Qty", input_filter='int', multiline=False)
        
        input_area.add_widget(Label(text="ID:")); input_area.add_widget(self.txt_id)
        input_area.add_widget(Label(text="Name:")); input_area.add_widget(self.txt_name)
        input_area.add_widget(Label(text="Price:")); input_area.add_widget(self.txt_price)
        input_area.add_widget(Label(text="Qty:")); input_area.add_widget(self.txt_qty)
        main_layout.add_widget(input_area)

        # أزرار التحكم
        btns = BoxLayout(size_hint_y=None, height=45, spacing=10)
        save_btn = Button(text="SAVE", background_color=(0, 0.8, 0.4, 1), on_press=self.save_data)
        clear_btn = Button(text="CLEAR", on_press=self.clear_inputs)
        btns.add_widget(save_btn); btns.add_widget(clear_btn)
        main_layout.add_widget(btns)

        # قائمة المنتجات
        scroll = ScrollView()
        self.grid = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        
        for p in database.get_inventory():
            row = BoxLayout(size_hint_y=None, height=40, spacing=5)
            row.add_widget(Label(text=str(p[0]), size_hint_x=0.1))
            row.add_widget(Label(text=str(p[1]), size_hint_x=0.4))
            row.add_widget(Label(text=f"${p[2]}", size_hint_x=0.2))
            
            actions = BoxLayout(size_hint_x=0.3, spacing=2)
            edit_b = Button(text="Edit"); edit_b.bind(on_press=lambda x, item=p: self.load_to_edit(item))
            del_b = Button(text="Del", background_color=(1,0,0,1)); del_b.bind(on_press=lambda x, pid=p[0]: self.delete_p(pid))
            actions.add_widget(edit_b); actions.add_widget(del_b)
            row.add_widget(actions); self.grid.add_widget(row)
            
        scroll.add_widget(self.grid); main_layout.add_widget(scroll)
        self.add_widget(main_layout)

    def load_to_edit(self, p):
        self.txt_id.text = str(p[0]); self.txt_name.text = p[1]
        self.txt_price.text = str(p[2]); self.txt_qty.text = str(p[3])
    def clear_inputs(self, *args):
        self.txt_id.text = ""; self.txt_name.text = ""; self.txt_price.text = ""; self.txt_qty.text = ""
    def delete_p(self, pid):
        database.delete_product(pid); self.refresh_list()
    def save_data(self, *args):
        if self.txt_name.text:
            if self.txt_id.text == "":
                database.add_new_product(self.txt_name.text, float(self.txt_price.text or 0), int(self.txt_qty.text or 0))
            else:
                database.update_product(int(self.txt_id.text), self.txt_name.text, float(self.txt_price.text or 0), int(self.txt_qty.text or 0))
            self.clear_inputs(); self.refresh_list()

# 3 شاشة المصروفات 
class ExpenseScreen(Screen):
    def on_enter(self): self.refresh_ui()
    def refresh_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        inp = GridLayout(cols=2, size_hint_y=None, height=120, spacing=5)
        self.cat = TextInput(hint_text="Category", multiline=False)
        self.amt = TextInput(hint_text="Amount", input_filter='float', multiline=False)
        self.desc = TextInput(hint_text="Notes", multiline=False)
        inp.add_widget(Label(text="Category:")); inp.add_widget(self.cat)
        inp.add_widget(Label(text="Amount:")); inp.add_widget(self.amt)
        inp.add_widget(Label(text="Note:")); inp.add_widget(self.desc)
        layout.add_widget(inp)
        
        btn = Button(text="ADD EXPENSE", size_hint_y=None, height=45, background_color=(1,0.5,0,1))
        btn.bind(on_press=self.save_exp)
        layout.add_widget(btn)

        scroll = ScrollView()
        grid = GridLayout(cols=3, size_hint_y=None, spacing=5)
        grid.bind(minimum_height=grid.setter('height'))
        total = 0
        for e in database.get_expenses():
            grid.add_widget(Label(text=str(e[1]), size_hint_y=None, height=35))
            grid.add_widget(Label(text=f"${e[2]}", size_hint_y=None, height=35))
            grid.add_widget(Label(text=str(e[4]), size_hint_y=None, height=35))
            total += e[2]
        scroll.add_widget(grid); layout.add_widget(scroll)
        layout.add_widget(Label(text=f"Total Expenses: ${total}", size_hint_y=None, height=40, color=(1,0,0,1), bold=True))
        self.add_widget(layout)

    def save_exp(self, *args):
        if self.cat.text and self.amt.text:
            database.add_expense(self.cat.text, float(self.amt.text), self.desc.text)
            self.cat.text = ""; self.amt.text = ""; self.desc.text = ""; self.refresh_ui()

# 4. شاشة الإحصائيات 
class Charts(Screen):
    def on_enter(self): self.refresh_ui()
    def refresh_ui(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        stats = database.get_sales_stats()
        expenses = database.get_expenses()
        total_sales_val = sum([s[1] * 10 for s in stats]) 
        total_exp_val = sum([e[2] for e in expenses])
        profit = total_sales_val - total_exp_val

        summary = BoxLayout(size_hint_y=None, height=50)
        summary.add_widget(Label(text=f"Sales: ${total_sales_val}", color=(0,1,0,1)))
        summary.add_widget(Label(text=f"Exp: ${total_exp_val}", color=(1,0,0,1)))
        summary.add_widget(Label(text=f"Net: ${profit}", bold=True))
        layout.add_widget(summary)

        if stats:
            names = [str(s[0]) for s in stats] 
            values = [s[1] for s in stats]
            fig, ax = plt.subplots(figsize=(5,3))
            ax.bar(names, values, color=['gold'] + ['skyblue']*(len(stats)-1))
            layout.add_widget(FigureCanvasKivyAgg(fig)); plt.close(fig)
        
        exp_btn = Button(text="EXPORT CSV", size_hint_y=None, height=50, background_color=(0.2,0.7,0.2,1))
        exp_btn.bind(on_press=self.export_csv); layout.add_widget(exp_btn)
        self.add_widget(layout)

    def export_csv(self, *args):
        data = database.get_all_sales_detailed()
        if data:
            with open("Report.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Product", "Qty", "Total"])
                writer.writerows(data)
            show_popup("Done", "Excel Report Saved!")

# 5. شاشة البيع (POS) 
class AddSaleScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.cart = [] 

    def on_enter(self): self.refresh()

    def refresh(self):
        self.clear_widgets()
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        inp = BoxLayout(size_hint_y=None, height=45, spacing=5)
        self.pid = TextInput(hint_text="ID", multiline=False)
        self.pqty = TextInput(hint_text="Qty", multiline=False)
        add_b = Button(text="ADD", on_press=self.add_to_cart, size_hint_x=0.3)
        inp.add_widget(self.pid); inp.add_widget(self.pqty); inp.add_widget(add_b)
        layout.add_widget(inp)
        
        # عرض السلة
        cart_display = "Current Cart:\n" + "\n".join([f"Item ID {c['id']} x{c['qty']}" for c in self.cart])
        layout.add_widget(Label(text=cart_display))
        
        btns = BoxLayout(size_hint_y=None, height=50, spacing=10)
        btns.add_widget(Button(text="CLEAR", on_press=self.clear_cart))
        btns.add_widget(Button(text="FINISH", background_color=(0,0.8,0,1), on_press=self.checkout))
        layout.add_widget(btns); self.add_widget(layout)

    def add_to_cart(self, *args):
        if self.pid.text and self.pqty.text:
            self.cart.append({'id': int(self.pid.text), 'qty': int(self.pqty.text)})
            self.pid.text = ""; self.pqty.text = ""; self.refresh()

    def clear_cart(self, *args):
        self.cart = []; self.refresh()

    def checkout(self, *args):
        if not self.cart: return
        res = database.process_bulk_sale(self.cart)
        if res[0]:
            pdf_report.print_bulk_invoice(res[1], res[2], res[3])
            self.cart = []; self.refresh(); show_popup("Success", "Invoice Ready!")
        else:
            show_popup("Error", str(res[1]))

# --- التنقل الرئيسي ---
class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.sm = ScreenManager()
        self.sm.add_widget(SplashScreen(name='splash'))
        self.sm.add_widget(InventoryManagerScreen(name='inv'))
        self.sm.add_widget(AddSaleScreen(name='sell'))
        self.sm.add_widget(ExpenseScreen(name='exp'))
        self.sm.add_widget(Charts(name='stat'))
        
        nav = BoxLayout(size_hint_y=0.1)
        nav.add_widget(Button(text="Stock", on_press=lambda x: setattr(self.sm, 'current', 'inv')))
        nav.add_widget(Button(text="Sale", on_press=lambda x: setattr(self.sm, 'current', 'sell')))
        nav.add_widget(Button(text="Exp", on_press=lambda x: setattr(self.sm, 'current', 'exp')))
        nav.add_widget(Button(text="Stats", on_press=lambda x: setattr(self.sm, 'current', 'stat')))
        self.add_widget(self.sm); self.add_widget(nav)
 
 

