from time import timezone
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.uix.card import MDCard

from kivymd.uix.picker import MDTimePicker, MDDatePicker
from kivymd.uix.button import MDFillRoundFlatButton

from kivy.properties import BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen

from datetime import time, datetime, timedelta
import requests
import sqlite3, random


Builder.load_file('kv/coffee_make.kv')

class DoseButton(MDFillRoundFlatButton):
	print('DoseButton 0')
	font_size = 25
	selected = BooleanProperty()

	def __init__(self, **kwargs):
		super(DoseButton, self).__init__(**kwargs)
		self.selected = False
		self.text_color=(1, 1, 1, 0.6)
		

class CoffeWare(MDCard): # the.boss@staff.com    Enter1
	print('CoffeWare 0')

	def __init__(self, **kwargs):
		super(CoffeWare, self).__init__(**kwargs)
		self.load_data()
		print('add dose btn')
		# self.add_dose_button()		
		magam = self
		Clock.schedule_once(magam.load_data, 0)
		#Clock.schedule_interval(magam.load_data, 5) 

	def d_on_save(self, instance, value, date_range):
		print('d_on_save:',instance, value, date_range)
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
		# date_dialog = MDDatePicker()
		# date_dialog.min_date=min_date
		# date_dialog.max_date=max_date
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
			print ("token = ", active_token)
		return active_token
	

	def load_data(self, *args):
		# print('recycle ware')
		active_token = self.load_token()
		# print('LOG Token', active_token)
		token_str = 'Token ' + active_token
		hd_token = {'Authorization':token_str}
		# print('HEAD Token', hd_token)
		if active_token == 'Empty':
			print('token print',self.ids.coffe_ware_label.parent)
			self.ids.coffe_message_label.text = "Isn't valid login"
		else:	
			print('Request')
			store = requests.get('https://coffeeanteportas.herokuapp.com/c_app/act_ware/', headers=hd_token).json()
			print('store', store)
			self.ids.coffe_message_label.text = "van kávé"
			st = []
			for item in store:
				# sti = item["w_name"])
				print('st', item)
			print(self.ids.coffe_ware_label.text)
			print(self.ids.coffe_message_label.text)
			self.add_dose_button()
			print(self.ids.items)
	
	def add_dose_button(self):
		dose_b = ['2 dose','4 dose','6 dose','8 dose',]
		for i in dose_b:
			bt = DoseButton()
			bt.text = i
			bt.id=i
			self.ids.dose_grid.add_widget(bt)
			# parnt = self.ids.coffe_ware_label.parent
			# bt.on_press = 'coffee_ware_card.press_dose(self)'

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
	
	def button_able(self, able=False):
		prnt = self.ids.coffe_ware_label.parent
		print('children3', prnt.ids.btn_box.children)
		for button in prnt.ids.dose_grid.children:
			button.disabled = able
			print(button.disabled)
		for button in prnt.ids.btn_box.children:
			button.disabled = able
			print(button.disabled)
		

			
		