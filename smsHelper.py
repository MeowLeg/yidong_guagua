# -*- coding:utf-8 -*-

import httplib, urllib
import random, string
import json
import requests
import traceback
import sqlite3

class SmsHelper:
	def __init__(self):
		self.token = "Jh2044695"
		self.apikey = 'c9bdf4fd56932b00dca7857f08c036b1'
		self.sent = {}
		self.host = 'yunpian.com'
		self.port = 80
		self.timeout = 10
		self.sms_send_uri = "/v1/sms/send.json"
		self.db = sqlite3.connect("./middle.db")
		self.cur = self.db.cursor()
		
	def genCode(self):
		return ''.join([random.choice(string.digits) for i in range(6)])

	def _set(self,phone,code):
		r = []
		for rr in self.cur.execute("select * from buffer where phone = ?", (phone,)):
			r.append(rr)
		if len(r) > 0:
			self.cur.execute("update buffer set code = ? where phone = ?", (code,phone))
		else:
			self.cur.execute("insert into buffer values(?,?)",(phone,code))
		self.db.commit()

	def _get(self,phone):
		for r in self.cur.execute("select code from buffer where phone = ?",(phone,)):
			return r[0]
		return ''

	def send_code(self, mobile):
		'''
		【新蓝广科】您的验证码是%d。如非本人操作，请忽略本短信
		'''
		code = self.genCode()
		self._set(str(mobile),str(code))
		self._sms(u"【新蓝广科】您的验证码是%s。如非本人操作，请忽略本短信" % (code,), mobile)
		return code

	def verifyCode(self, phone, code):
		try:
			print phone
			print code
			print type(phone)
			print type(code)
			print self._get(str(phone)) 
			return str(self._get(str(phone))) == str(code)
		except Exception,e:
			traceback.print_exc()
			return False

	def _sms(self, text, mobile):
		params = urllib.urlencode({
				'apikey':self.apikey,
				'text': text.encode('utf8'),
				'mobile': mobile,
				})
		header = {
			'Content-type': 'application/x-www-form-urlencoded',
			'Accept': 'text/plain',
		}
		conn = httplib.HTTPConnection(self.host, port=self.port, timeout=self.timeout)
		conn.request('POST', self.sms_send_uri, params, header)
		response = conn.getresponse()
		response_str = response.read()	
		conn.close()
		ret = json.loads(response_str)
		print ret
		if ret['code'] == 0:
			self.sent[str(id)] = ''

if __name__=='__main__':
	sms = SmsHelper()
# print sms.send_code(13857207697)
	print sms.verifyCode("13857207697", "12345")
