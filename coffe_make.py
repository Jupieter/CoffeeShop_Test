from time import timezone
from kivy.lang import Builder
from kivy.app import App
from kivy.clock import Clock
from kivymd.uix.card import MDCard

from kivymd.uix.picker import MDTimePicker, MDDatePicker
from kivymd.uix.button import MDFillRoundFlatButton

from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen

from datetime import time, datetime, timedelta
import requests
import sqlite3, random, json
from kivy.uix.screenmanager import ScreenManager

Builder.load_file('kv/coffee_make.kv')

class DoseButton(MDFillRoundFlatButton):
	print('DoseButton 0')
	font_size = 25
	selected = BooleanProperty()

	def __init__(self, **kwargs):
		super(DoseButton, self).__init__(**kwargs)
		self.selected = False
		self.text_color=(1, 1, 1, 0.6)
		sm = ScreenManager
		self.sm = sm
		

class CoffeWare(MDCard): # the.boss@staff.com    Enter1
	print('CoffeWare 0')
	

	def __init__(self, **kwargs):
		super(CoffeWare, self).__init__(**kwargs)
		# self.add_dose_button()
		# self.load_data()
		self.stor = None
		self.ware_step = 0	
		Clock.schedule_once(self.load_data, 0)
		# Clock.schedule_interval(self.load_data_clk, 5)
		# self.r_fresh()
		self.message = ""
		Clock.schedule_once(self.button_able, 0)
		# Clock.schedule_interval(self.button_able, 3)
		# Clock.schedule_once(self.r_fresh, 0)
		# Clock.schedule_interval(self.r_fresh, 5) 

	def d_on_save(self, instance, value, date_range):
# 		print('d_on_save:',instance, value, date_range)
		self.ids.date_btn.text = str(value)
		self.ids.date_btn.md_bg_color=(0, 0.5, 0, 1)

	def show_date_picker(self):
		act_t = datetime.now()
		end_t = act_t + timedelta(days = 5)
		act_date = str(act_t)[0:10].replace("-", ":")
		end_date =  str(end_t)[0:10].replace("-", ":")
		print('act_t', act_date, end_date)
		min_date = datetime.strptime(act_date, '%Y:%m:%d').date()
		max_date = datetime.strptime(end_date, '%Y:%m:%d').date()
		print(min_date, max_date)
		date_dialog = MDDatePicker(
			min_date=min_date,
			max_date=max_date,
    		)
		date_dialog.bind(on_save=self.d_on_save)
		date_dialog.open()

	def t_on_save(self, instance, value):
		print(instance, value)
		self.ids.time_btn.text = str(value)
		self.ids.time_btn.md_bg_color=(0, 0.5, 0, 1)

	def show_time_picker(self):
		'''Open time picker dialog.'''	
		time_dialog = MDTimePicker()
		# now = datetime.now()
		# current_time = now.strftime("%H:%M:%S").time()
		# print(now, '  :  ',current_time)
		# time_dialog.set_time = current_time
		# time_dialog._set_current_time
		time_dialog.bind(on_save=self.t_on_save)
		time_dialog.open()
		
	
	def load_token(self, *args):
		conn = sqlite3.connect('coffe_app.db')
		active_tok = conn.execute("SELECT act_token from act_tokens")
		for row in active_tok:
			active_token = row[0]
			# print ("token = ", active_token)
		return active_token
	
	def load_data(self, *args):
		Clock.schedule_once(self.load_data_clk, 0)

	def load_data_clk(self, *args):
		print('coffe make data')
		active_token = self.load_token()
		token_str = 'Token ' + active_token
		hd_token = {'Authorization':token_str}
		if active_token == 'Empty':
			print('token print',self.ids.coffe_ware_label.parent)
		else:	
			print('Request')
			store = requests.get('https://coffeeanteportas.herokuapp.com/c_app/act_ware/', headers=hd_token).json()
			print('store', store)			
			self.stor = self.ware_json(store)
			print(self.stor)
		return self.stor
	
	def ware_json(self, store_d):
		store = []
		for item in store_d:
			it = json.loads(item)
			print('st', item)
			print('it', it)
			store.append(it)
		return store
	
	def ware_button(self, *args):
		print("self.stor", self.stor)
		tuple_len = len(self.stor)
		self.ware_step += 1
		if self.ware_step > tuple_len:
			self.ware_step = 1
		id = self.stor[self.ware_step-1]['w_id']
		name = self.stor[self.ware_step-1]['w_name'].replace('Coffee','')
		name.replace(',','')
		dose = self.stor[self.ware_step-1]['w_dose']
		print('self.ware_step',self.ware_step, id, name, dose)
		texte = str(id) + " " + name + " left " + str(dose) +" dose"
		print(texte)
		self.ids.ware_btn.text = texte
		self.ids.ware_btn.md_bg_color=(0, 0.5, 0, 1)




	def press_dose(self, act_choice):
		prnt = self.ids.coffe_ware_label.parent
		print('children1',prnt.ids.dose_grid.children)
		print('children2',self.ids.dose_grid.children)
		for dose_but in prnt.ids.dose_grid.children:
			print(dose_but)
			print(dose_but.text, dose_but.text_color)
			dose_but.selected = False
			dose_but.text_color=[0, 0, 0, 0.3]
			dose_but.md_bg_color = [0.5, 0.5, 0.5, 1]
			act_choice.text_color=(1, 1, 1, 1)
			act_choice.md_bg_color=(0, 0.5, 0, 1)
			print(act_choice.value)	
	
	def button_able(self, *args):
		active_token = self.load_token()
		print(active_token)
		if active_token == 'Empty':
			able = True
			self.ids.coffe_message_label.text = "Isn't valid login with staff status"
		else:
			able = False
			self.ids.coffe_message_label.text = "Set the parameters:"
		print('able',able)
		prnt = self.ids.coffe_ware_label.parent
		for button1 in prnt.ids.dose_grid.children:
			button1.disabled = able
		for button2 in prnt.ids.btn_box.children:
			button2.disabled = able
		self.ids.ware_save.disabled = able
		print('END able')
		
	def r_fresh(self, *args):
		print('FRESH')

			
		