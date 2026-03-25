from kivy.app import App
from kivy.core.window import Window
from ui import MainLayout
import database

class SmartPOSApp(App):
    def build(self):
        # إعداد قاعدة البيانات والجداول عند التشغيل
        database.create_tables() 
        database.create_expense_table() 
        
        
        Window.clearcolor = (0.1, 0.1, 0.1, 1) # خلفية 
        self.title = "Smart POS System v2.0"
        
        return MainLayout()

if __name__ == "__main__":
    SmartPOSApp().run()