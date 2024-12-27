#!/usr/bin/python3
#Coding:utf-8

from pathlib import Path
import sys,os
from wsgiref.simple_server import make_server
from wsgiref.validate import validator
from werkzeug.wrappers import Request

"""
	Cet module permet la gestion des données coté serveur.
	
	Les données envoyé au serveur doivent déjà être
	transformé et près pour l'enrégistement directe 
	dans les fichier .dav

	principe simple:
		le dossier doit être spécifier au niveau du 
		PATH_INFO et les autre informations doivent 
		être coder sous forme de formulaire.
"""
class myData:
	def __init__(self):
		pass

	def dump(self,fic,data):
		Data = data
		with open(fic,'wb') as fic:
			fic.write(Data.encode('utf8'))
		return len(Data)

	def load(self,fic):
		this_fic = fic
		with open(fic,'r',encoding = 'utf8') as fic:
			try:
				Read = fic.read()
			except UnicodeDecodeError:
				with open(this_fic,'r') as fic:
					R = fic.read()
				self.dump(this_fic,self.Trans.Restore(R))
				Read = R
		return Read

class Handler:
	Data_base = myData()

	@staticmethod
	def Create_doss(dossier,fichier):
		default_P = Path.cwd()
		dos = f"BASE_DIR/{dossier}/{fichier}"
		for path in dos.split("/"):
			default_P = default_P.joinpath(path)
			if not default_P.exists():
				os.mkdir(default_P)
		return default_P

	@staticmethod
	def Save_data(dossier,fichier,keys,data):
		"""
			Ici, dossier et fichier vont être considérer
			comme le dossier. la clé sera dont le fichier
		"""
		fichier = Handler.Create_doss(dossier,fichier)
		fichier = fichier.joinpath(keys)
		lenf = Handler.Data_base.dump(fichier,data)
		return lenf

	@staticmethod
	def Get_data(dossier,fichier,keys):
		fichier = Handler.Create_doss(dossier,fichier)
		fichier = fichier.joinpath(keys)
		try:
			data = Handler.Data_base.load(fichier)
		except FileNotFoundError:
			data = False
		return data

	@staticmethod
	def Sup_data(self,dossier,fichier,keys):
		fichier = Handler.Create_doss(dossier,fichier)
		fichier = fichier.joinpath(keys)
		if fichier.exists():
			os.remove(fichier)
			
class Data_hand:
	def __init__(self,dossier,URL):
	#
		"""
			L'URL est issu d'un GET et contient les
			informations suivant:
				fichier
				key
				request
				donner

			pour une méthode 'GET' et 'SUP' 
			la donner est vide

			les données traités doivent être tous des
			binaire
		"""
		self.DATA_HAND = Handler()
		self.dossier = dossier
		self.DATA_DIC = self.get_headers(URL)

		self.DATA = self.DATA_DIC['donner']
		self.FIC = self.DATA_DIC["fichier"]
		self.KEY = self.DATA_DIC["key"]
		self.METHOD = self.DATA_DIC["request"]

		self.HAND_DIC = {
			"GET":self.get_data,
			"SAVE":self.save_data,
			"SUP":self.sup_data,
		}

	def get_headers(self,URL):
		URL = URL.split("&")
		url = [i.split('=') for i in URL]
		dic = {i:j for i,j in url}
		return dic

	def get_data(self):
		data = self.DATA_HAND.Get_data(self.dossier,
			self.FIC,self.KEY)
		if not data:
			data = "bool:0"
		data = data.encode('utf-8')
		return [data]

	def save_data(self):
		self.DATA_HAND.Save_data(self.dossier,self.FIC,
			self.KEY,self.DATA)
		return [b"True"]

	def sup_data(self):
		self.DATA_HAND.Sup_data(self.dossier,self.FIC,
			self.KEY)
		return [b"True"]

	def Run(self):
		ret = self.HAND_DIC[self.METHOD]()
		return ret

def App(environ,start_response):
	status = "200 OK"
	headers = [('Content-type', 'text/plain')]
	args = status,headers
	start_response(status,headers)

	URL = Request(environ).url
	URL = URL.split("?")[1]
	dossier = environ["PATH_INFO"]
	Execution = Data_hand(dossier,URL)

	response = Execution.Run()
	'''
		Le format de response est une liste de deux information
		soit: fichier,data
	'''
	return response

if __name__ == "__main__":
	port = 5000
	validator_app = validator(App)
	with make_server("",port,validator_app) as httpd:
		print(f'En écoute sur le port {port}...')
		httpd.serve_forever()




