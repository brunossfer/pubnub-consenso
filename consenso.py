from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
import time
import os
import json

pnconfig = PNConfiguration()
pnconfig.publish_key = ''
pnconfig.subscribe_key = ''
pnconfig.ssl = True
pubnub = PubNub(pnconfig)

badSign= False

def my_publish_callback(envelope, status):
	# Check whether request successfully completed or not
	if not status.is_error():
		pass
		
class MySubscribeCallback(SubscribeCallback):
	def presence(self, pubnub, presence):
		pass # aqui saberia quem esta conectando, pulei
	def status(self, pubnub, status):
		pass
	def message(self, pubnub, message):
		global badSign
		jsonlike = json.loads(str(message.message).replace("\'","\"")) # me retorna o dict que é enviado
		if jsonlike["sender"] != str(pubnub.uuid):
			print ("\n"+ str(jsonlike["sender"]+":"+jsonlike["msg"])) # recebe mensagem e printa uuid (sender): msg	
			if "deu ruim" in str(jsonlike["msg"]) and badSign ==True:
				consenso(jsonlike)				
			
pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels("canal").with_presence().execute()

# criar o trem de consenso... ler a mensagem de entrada, se deu merda checar aí diz se deu merda mesmo
concur= 0
def consenso (jsonMsg):
	# jsonMsg["sender"] # sei lá como definir parentesco entre os caras
	global concur
	concur+=1
	print("alguem concorda")

def startService():	
	while True:
		try:		
			pubnub.publish().channel("canal").message({"sender":pubnub.uuid,"msg":"tudo ok"}).pn_async(my_publish_callback)
			time.sleep(20)
		except KeyboardInterrupt: # ctrl+c
			print("Alert: algo de errado nao esta certo, sou :"+pubnub.uuid)
			try:
				global badSign
				badSign = True
				pubnub.publish().channel("canal").message({"sender":pubnub.uuid,"msg":"deu ruim"}).pn_async(my_publish_callback)
				alert()		
				badSign = False
			except KeyboardInterrupt: # ctrl+c
				pubnub.unsubscribe().channels("canal").execute()
				os._exit(1) # isso fecha o programa

def alert():
	time.sleep(15)
	definirconsenso = 2
	global concur
	if concur >= definirconsenso:
		pubnub.publish().channel("canal").message({"sender":pubnub.uuid,"msg":"fudeu de vez"}).pn_async(my_publish_callback)
		print("socorro, deu ruim mesmo")
	else:
		pubnub.publish().channel("canal").message({"sender":pubnub.uuid,"msg":"alarme falso"}).pn_async(my_publish_callback)
		print("opa, alarme falso")
	concur = 0
	
startService()	
