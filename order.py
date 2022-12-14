from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.button import MDFillRoundFlatButton
from login import LogInCard
from decimal import Decimal
import requests
import json

Builder.load_file('kv/order.kv')


class OrderMDFillRoundFlatButton(MDFillRoundFlatButton):

	def __init__(self, **kwargs):
		super(OrderMDFillRoundFlatButton, self).__init__(**kwargs)
		self.text_color=(1, 1, 1, 0.3)
	
	def on_disabled(self, instance, value):
		'''musted to overwrite it because It overwrites the green marked button to primary_color '''
		pass


class CoffeOrder(MDGridLayout):
	
	def __init__(self, **kwargs):
		super(CoffeOrder, self).__init__(**kwargs)
		self.ordered = [[],[],[],[]]
		self.ware_step_lst = [0,0,0,0]
		self.app = MDApp.get_running_app()
		self.scr2 = self.app.root.ids.scr2_message_lbl
		self.log_card = LogInCard()
		self.active_token = self.log_card.load_token()
		self.active_user, self.act_pkey, self.act_staff = self.log_card.read_user()
		self.mess_text1 = "O R D E R"
		Clock.schedule_once(self.load_data_ware, 0)


	def ware_ordr_btn(self, btn_id, *args):
		''' carussel button => select material from requested db'''
		w_order = self.ordered[btn_id]
		self.active_token = self.log_card.load_token()
		if self.active_token == "Empty":
			self.mess_text1 = "Isn't valid login. Log In First!"
			Clock.schedule_once(self.fresh_ord_mess, 1.5)
			Clock.schedule_once(self.go_scr4, 2)
		elif w_order != [] and self.active_token != "Empty":
			btn_text = "order_btn_" + str(btn_id)
			lbl_text = "order_end_label_A_" + str(btn_id)
			tuple_len = len(w_order)
			# stepper
			self.ware_step_lst[btn_id] += 1 				
			if self.ware_step_lst[btn_id] > tuple_len:
				self.ware_step_lst[btn_id] = 1
			w_step = self.ware_step_lst[btn_id]-1
			# ware type by button id number
			ware = json.loads(w_order[w_step])
			w_id = ware['w_id']
			w_name = ware['w_name']
			w_name.replace(',','')
			w_dose = Decimal(ware['w_dose'])
			texte = w_name + " | " + str(w_dose) +" dose"
			self.ids[btn_text].text = texte
			self.ids[btn_text].text_color = self.log_card.my_color(5)
			self.ids[btn_text].md_bg_color = self.log_card.my_color(2)
			self.ids[btn_text].value = w_id
			# able the next buttons
			self.ids[lbl_text].text = texte
			self.mess_text1  = texte
			self.dose_button_able(btn_id, w_id, w_dose)
			Clock.schedule_once(self.fresh_ord_mess, 2)
			Clock.schedule_once(self.fresh_ord_mess, 0)
			Clock.schedule_once(self.save_btn_able, 1)
			# self.save_btn_able()
		else:
			self.mess_text1  = "Something went wrong. No ware data"	
			Clock.schedule_once(self.fresh_ord_mess, 3)
			Clock.schedule_once(self.fresh_ord_mess, 0)


	def ware_btn_able(self, *args):
		'''buttun disabled if not authenticated '''
		if self.active_token == "Empty" or self.ids["order_btn_0"].value == 0:
			able1 = True
		else:
			able1 = False
		for i in range(1,4,1):
			btn_id = "order_btn_" + str(i)
			self.ids[btn_id].disabled = able1


	def save_btn_able(self, *args):
		'''buttun disabled if not choice all  '''
		if (self.ids["order_btn_0"].text ==  "Choice Coffee" or
			self.ids["order_btn_1"].text ==  "Choice Sugar" or 
			self.ids["order_btn_2"].text ==  "Choice Milk" or
			self.ids["order_btn_3"].text ==  "Choice Flavour"):
			self.ids["order_save_btn"].disabled = True
		else:
			self.ids["order_save_btn"].disabled =  False
			self.mess_text1 = "You can save your order"
			Clock.schedule_once(self.fresh_ord_mess, 3)
			Clock.schedule_once(self.fresh_ord_mess, 0)

	def oreder_press_dose(self, act_choice, btn_id):
		'''One Choice button selection function'''
		dose_grid = "dose_grid_" + str(btn_id)
		self.ids[dose_grid].value = 0
		for dose_but in self.ids[dose_grid].children:
			dose_but.text_color = self.log_card.my_color(3)
			dose_but.md_bg_color = self.app.theme_cls.primary_dark # [0.4, 0.4, 0.4, 1]
		act_choice.text_color = self.log_card.my_color(5)
		act_choice.md_bg_color = self.log_card.my_color(2) #(0, 0.5, 0, 1)
		self.ids[dose_grid].value = act_choice.value
		if btn_id == "0" and self.ids["dose_grid_0"].value != 0:
			self.ware_btn_able()
		# messages: 
		lbl_text = "order_end_label_B_" + str(btn_id)
		self.ids[lbl_text].text = "Dose: " + "{:.1f}".format(act_choice.value) 
		order_label = ["COFFEE", "SUGAR", "MILK", "FLAVOUR"]
		self.mess_text1  = order_label[int(btn_id)] + " ORDER : " + str(act_choice.value) + " dose"
		Clock.schedule_once(self.fresh_ord_mess, 1.5)
		Clock.schedule_once(self.fresh_ord_mess, 0)		


	def dose_button_able(self, btn_id, w_id, w_dose, *args):
		'''buttun disabled if not authenticated 
			disabled SAVE button if all option isn't selected.
		'''
		# print("btn_id, w_id", btn_id, w_id)
		dose_grid = "dose_grid_" + str(btn_id)
		# print("dose:          ", w_dose)
		if w_dose == 0:
			able2 = True
		else:
			able2 = False
		# print('able2: ',able2)
		for button1 in self.ids[dose_grid].children:
			if button1.value > w_dose:
				button1.disabled = True
			else: 
				button1.disabled = able2


	def load_data_ware(self, *args):
		print('coffe order data')
		try:
			wares = requests.get('http://jupieter.pythonanywhere.com/c_app/order_tastes/').json()
			# wares = requests.get('http://coffeeanteportas.herokuapp.com/c_app/order_tastes/').json()
			# wares = requests.get('http://127.0.0.1:8000/c_app/order_tastes/').json()
			print("-----------------wares----------------------")
			for i in range(4):
				self.ordered[i] = wares[i]	
			# print('store ware: ', self.ordered)	
			self.mess_text1 = "Order a Coffee with tastes"
		except:
			print("-----------------problem----------------------")
			print("Problem with internet conection")
			self.mess_text1  = "Something went wrong. No ware data"	
		Clock.schedule_once(self.fresh_ord_mess, 2)
		Clock.schedule_once(self.fresh_ord_mess, 0)


	def order_save(self, *args):
		sends = {
			"coffee_selected": self.ids.order_btn_0.value,
			"coffee_dose": self.ids.dose_grid_0.value,
			"sugar_choice": self.ids.order_btn_1.value if self.ids.order_btn_1.value != 0 else None,
			"sugar_dose": self.ids.dose_grid_1.value,
			"milk_choice": self.ids.order_btn_2.value if self.ids.order_btn_2.value != 0 else None,
			"milk_dose": self.ids.dose_grid_2.value,
			"flavour_choice": self.ids.order_btn_3.value if self.ids.order_btn_3.value != 0 else None,
			"flavour_dose": self.ids.dose_grid_3.value,
			"coffe_user": self.act_pkey
		}
		print("sends:     -----------------------------------------------------")
		print(sends)
		print("sends:     -----------------------------------------------------")
		try:
			token_str = 'Token ' + self.active_token
			hd_token = {'Authorization':token_str}
			if self.active_token != "Empty":
				print('LOG ware_save Token', self.active_token)
				requests.post('https://jupieter.pythonanywhere.com/c_app/order_save/', headers=hd_token, data=sends)
				# requests.post('http://127.0.0.1:8000/c_app/order_save/', headers=hd_token, data=sends)
				# requests.post('https://coffeeanteportas.herokuapp.com/c_app/order_save/', headers=hd_token, data=sends)
				self.ids["order_save_btn"].text_color = self.log_card.my_color(5)
				self.ids["order_save_btn"].md_bg_color = self.log_card.my_color(2)
				self.mess_text1 = "New coffee order saved."
				Clock.schedule_once(self.fresh_ord_mess, 0)
				Clock.schedule_once(self.go_home, 2)
		except:
			self.mess_text1 = "It seems, there is no internet"
			Clock.schedule_once(self.fresh_ord_mess, 2)
			Clock.schedule_once(self.fresh_ord_mess, 0)
	
	
	def fresh_ord_mess(self, *args, **kwargs):
		self.scr2.text = self.mess_text1
		self.mess_text1 = "Ordering"


	def go_home(self, *args):
		sm = self.app.root.ids.nav_bottom
		sm.switch_tab('screen 1')

	def go_scr4(self, *args):
		sm = self.app.root.ids.nav_bottom
		sm.switch_tab('screen 4')