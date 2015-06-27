# -*- coding:utf-8 -*-

import json ,web, time, os, random, traceback, requests
import sqlite3 as sqlite
from smsHelper import SmsHelper
from captcha import Captcha

class Guagua:
	def __init__(self):
		self.token = "Jh2044695"
		self.db = self.__gen_db("./middle.db")
		self.baseRange = 10
		self.target = 5
		self.sms = SmsHelper()
		self.captcha = Captcha()
		
	def __gen_db(self, nm):
		db = sqlite.connect(nm)
		return {'db':db, 'cur':db.cursor()}

	def __get_callback(self, d):
		return 'cmd' in d and hasattr(self, d['cmd']) \
			and getattr(self, d['cmd']) \
			or self.__callback_default

	def __result_default(self, r):
		ret = {
			'success':False, 
			'data':[], 
			'errMsg':'',
		}
		ret.update(r)
		return ret

	def __callback_default(self,r={}):
		return self.__result_default(r)
		
	def __watch_dog(self, d):
		ret = {'success':False}
		ret['success'] = d['token'] == self.token
		return self.__result_default(ret)
			
	def __to_json(self, r):
		web.header('Content-Type', 'application/json; charset=utf-8')
		return json.dumps(r, ensure_ascii=False)

	def __gen_jsonp_cb(self, d, r):
		cb = 'callback' in d and d['callback'] or 'callback'
		return cb+"("+self.__to_json(r)+")"

	def __exec_sql(self, sql, parameters=(), if_commit=False):
		ret = []
		for r in self.db['cur'].execute(sql, parameters):
			ret.append(r)
		if if_commit:
			ret = self.db['cur'].lastrowid
			self.db['db'].commit()
		return ret

	def __gen_with_keys(self, keys, vals):
		try:
			ret = {'success':True, 'data':[]}
			ret['data'] = []
			for l in vals:
				r = {}
				for i,c in enumerate(keys):
					r[c] = l[i]
				ret['data'].append(r)
		except Exception,e:
			print e
			ret = {}
		return self.__result_default(ret)
	
	###################	

	def authorize(self,d):
		# deviceToken
		try:
			strs, captcha = self.captcha.getCode()
			for r in self.__exec_sql("select phone, left, flows from flows where deviceToken = ?", (d["deviceToken"],)):
				return {"success":True, "phone":r[0], "left":r[1], "flows":r[2]}
			return {"success":False, "captchaData":captcha, "captchaStr":strs}
		except Exception,e:
			traceback.print_exc()
			return {"success":False}

	def getCode(self,d):
		# phone
		try:
			code = self.sms.send_code(d["phone"])
			return {"success":True, "code":code}
		except Exception,e:
			traceback.print_exc()
			return {"success":False}

	def binding(self,d):
		# deviceToken, phone, code
		try:
			if not self.sms.verifyCode(d["phone"],d["code"]):
				return {"success":False, "errMsg":u"验证失败！"}
			ret = self.__exec_sql("select * from flows where deviceToken = ?", (d["deviceToken"],))
			if len(ret) > 0:
				self.__exec_sql("update flows set phone = ? where deviceToken = ?", (d["phone"],d["deviceToken"]),1)
			else:
				self.__exec_sql("insert into flows(phone,deviceToken) values(?,?)", (d["phone"],d["deviceToken"]),1)
			return {"success":True, "errMsg":u"绑定成功！"}
		except Exception,e:
			traceback.print_exc()
			return {"success":False, "errMsg":u"绑定失败！"}

	def getFlow(self,d):
		# deviceToken
		try:
			for r in self.__exec_sql("select flows from flows where deviceToken = ?", (d["deviceToken"],)):
				return {"success":True, "flows":r[0]}
			return {"success":False}
		except Exception,e:
			traceback.print_exc()
			return {"success":False}

	def randomFlow(self, d):
		# deviceToken
		ret = {"success":True}
		gain = int(random.random()*self.baseRange+1)
		self.__exec_sql("update flows set left = (select left from flows where deviceToken = ?)-1 where deviceToken = ?",(d["deviceToken"],d["deviceToken"]),1)
		if gain == self.target:
			ret["gain"] = 5 
			ret["errMsg"] = u"恭喜获得了5M流量！"
		else:
			ret["gain"] = 0
			ret["errMsg"] = u"很可惜，一无所获啊！"
		return ret

	def renewFlow(self,d):
		# deviceToken, newFlow
		try:
			self.__exec_sql("update flows set flows = ? where deviceToken = ?",(d["newFlow"],d["deviceToken"]),1)
			return {"success":True, "errMsg":u"领取成功！"}
		except Exception,e:
			traceback.print_exc()
			return {"success":False, "errMsg":u"领取失败！"}

	def gainFlow(self,d):
		# deviceToken
		try:
			r = self.__exec_sql("select flows, ifGained from flows where deviceToken = ?",(d["deviceToken"],))
			flows = int(r[0][0]) - 20
			ifGained = int(r[0][1]) == 1
			print flows
			if flows < 0:
				return {"success":False, "errMsg":u"流量不足20M，无法兑换！"}
			elif ifGained:
				return {"success":False, "errMsg":u"您已经领取了！"}
			else:
				r = requests.post('http://www.ptweixin.com/api/1fd502b0d8/reserve/detail/9312/./', \
						data="InputValue_0=%d&RId=9312&do_action=reserve.reserve" % int(d["phone"]))
				if json.loads(r.text)["ret"] == 1:
					self.__exec_sql("update flows set flows = ?, ifGained = 1 where deviceToken = ?",(flows,d["deviceToken"]),1)
					return {"success":True, "errMsg":u"兑换成功！"}
				else:
					return {"success":False, "errMsg":u"移动接口调用失败！"}
		except Exception,e:
			traceback.print_exc()
			return {"success":False, "errMsg":u"兑换失败！"}

	def moveFlows(self,d):
		# deviceToken, phone(toWho)
		try:
			r = self.__exec_sql("select flows from flows where phone = ?", (d["phone"],))
			if len(r) == 0: return {"success":False, "errMsg":u"该电话号码尚未参加活动！"}
			self.__exec_sql("update flows set flows = (select flows from flows where phone = ?)+5 where phone = ?", \
					(d["phone"],d["phone"]),1)
			self.__exec_sql("update flows set flows = (select flows from flows where deviceToken = ?)-5 where deviceToken = ?", \
					(d["deviceToken"],d["deviceToken"]),1)
			return {"success":True, "errMsg":u"转移流量成功！"}
		except Exception,e:
			traceback.print_exc()
			return {"success":False, "errMsg":u"转移流量失败，请重试！"}

	def GET(self):
		d = web.input()
		print d # DEBUG

		ret = self.__watch_dog(d)
		if not ret['success']:
			return ret
		return self.__gen_jsonp_cb(d,(self.__get_callback(d))(d))
