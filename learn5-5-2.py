#coding=utf-8
#something wrong
from HTMLParser import HTMLParser
import urllib,urllib2,cookielib
import re,os,sys
import platform
import base64
import logging,getpass,time

type = sys.getfilesystemencoding()
reload(sys)
sys.setdefaultencoding('utf-8')
						
id_name = []
file_link = []
bbs_link = []
hw_link = []
temp_link = []
title_content = []
order_package = []
title_score = []
hw_score = []
temp_title_content = []
temp_order_package = []
hw_link_deadline = []
hw_score = []
packname = ''
logfile = 'log'
logger = logging.getLogger()
hdlr = logging.FileHandler(logfile)
formatter = logging.Formatter('%(asctime)s%(levelname)s%(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.NOTSET)
logger.info(' start ')
systeminfo = platform.system()


def clearscreen():
	if systeminfo == 'Windows':
		os.system('cls')
		return
	if systeminfo == 'Linux':
		os.system('clear')
		return
	if systeminfo == 'darwin':
		os.system('clear')
	else:#Unix like system eg.os X
		try:
			os.system('clear')
		except:
			pass
		return

class getIdName(HTMLParser):                   #get the name and ID num of every course
	global id_name
	in_target = False
	temp_name = ''
	temp_id = ''
	temp_tuple = () 
	base = 'http://learn.tsinghua.edu.cn'
	name_pattern = re.compile(r'\(\d+\)$')
	id_pattern=re.compile(r'\d+$')
	def handle_starttag(self,tag,attrs):
		if tag == 'a':
			for name,value in attrs:
				if name == 'target' and value == '_blank':
					self.in_target = True
					for href,link in attrs:
						if href == 'href':
							handle = re.search(self.id_pattern,link)
							if handle:
								self.temp_id = handle.group(0) 
							else:
								logger.info(' id search fail,check the url:%s'%(link)) 
	def handle_data(self,data):
		if self.in_target:
			logger.info(data[0:-23].strip().decode('utf-8').encode(type))
			self.temp_name = data[0:-23].strip().decode('utf-8').encode(type)  
			self.temp_name = re.sub(self.name_pattern,'',self.temp_name)
			self.temp_tuple = tuple([self.temp_id,self.temp_name])
			id_name.append(self.temp_tuple)
	def handle_endtag(self,tag):
		if tag == 'a' and self.in_target:
			self.in_target = False

class getFileLink(HTMLParser):             #get the link of every file page 
	global file_link
	global temp_link
	in_target = False
	base = 'http://learn.tsinghua.edu.cn'
	def handle_starttag(self,tag,attrs):
		if tag == 'a':
			for name,value in attrs:
				if name == 'target' and value == '_top':
					self.in_target = True
					for href,link in attrs:
						if href == 'href':
							temp = self.base + link
							temp_link.append(temp)
	def handle_endtag(self,tag):
		if tag == 'a' and self.in_target:
			self.in_target = False
		if tag == 'html':
			pass
		#	file_link.append(self.temp_link)
	#		temp_link = []
	

class getBbsLink(HTMLParser):
	global temp_bbs_link  
	temp_bbs_link = []
	in_table = False
	base = 'http://learn.tsinghua.edu.cn/MultiLanguage/public/bbs/'
	def handle_starttag(self,tag,attrs):
		if tag == 'table':
			for name,value in attrs:
				if name == 'id' and value == 'table_box':
					self.in_table = True
		if tag == 'a' and self.in_table:
			for href,link in attrs:
				if href == 'href':
					temp = self.base + link
					temp_bbs_link.append(temp)
	def handle_endtag(self,tag):
		if tag == 'table' and self.in_table:
			self.in_table = False
		if tag == 'html':
			pass
			#bbs_link.append(self.temp_bbs_link)
			#self.temp_bbs_link = []

class getHomeworkLink(HTMLParser):
	global temp_hw_link_deadline	
	temp_hw_link_deadline = []
	temp_title_deadline = []
	in_table = False    #flag showing whether in table or not
	in_tr = False		#flag showing whether in homework information section or not              
	in_a = False
	count = 0
	deadline_flag = True 
	temp_link = ''
	hwtitle = ''
	deadline = ''
	base = 'http://learn.tsinghua.edu.cn/MultiLanguage/lesson/student/'
	def handle_starttag(self,tag,attrs):
		if tag == 'table':
			for name,value in attrs:
				if name == 'id' and value == 'table_box':
					self.in_table = True
		if tag == 'tr' and self.in_table:
			for name,value in attrs:
				if name == 'class' and value == 'tr1':
					self.in_tr = True
				if name == 'class' and value == 'tr2':
					self.in_tr = True
		if tag == 'a' and self.in_tr:
			self.in_a = True	
			for href,link in attrs:
				if href == 'href':
					self.temp_link = self.base + link
					#print self.temp_link
		if tag == 'td' and self.in_tr:
			for name,value in attrs:
				if name == 'width' and value == '10%':   #get the deadline
					self.count = (self.count+1)%3
	def handle_data(self,data):				
		if self.in_a:
			self.hwtitle = data.strip()
		if self.count == 2 and self.deadline_flag:      
			self.deadline = data.strip()
			#print 'the deadline '+ self.deadline
			#print 'the title ' + self.hwtitle	
			self.temp_title_deadline = [self.hwtitle,self.deadline]
			self.deadline_flag = False
			temp_hw_link_deadline.append(tuple([self.temp_link,self.temp_title_deadline]))  #the link and the deadline 
	def handle_endtag(self,tag):
		if tag == 'table' and self.in_table:
			self.in_table = False
		if tag == 'tr' and self.in_tr:
			self.in_tr = False
			self.deadline_flag = True
		if tag == 'a' and self.in_tr:
			self.in_a = False
		#if tag == 'html':
		#	hw_link_deadline.append(self.temp_hw_link_deadline)
	
class getHomeworkScore(HTMLParser): #return the list of the score :[[homework_name,score],...]
	global hw_score
	hw_score = []
	in_table = False	
	in_title = False
	in_score = False
	in_tr = False
	in_a = False
	in_td = False
	title = ''
	score = ''
	def handle_starttag(self,tag,attrs):
		if tag == 'table':
			for name,value in attrs:
				if name == 'id' and value == 'table_box':
					self.in_table = True
		if tag == 'tr' and self.in_table:
			for name,value in attrs:
				if name == 'class' and value == 'tr2':
					self.in_tr = True
				if name == 'class'and value == 'tr1':
					self.in_tr = True
		if tag == 'td' and self.in_tr:
			for name,value in attrs:
				if name == 'width' and value == '20%':
					self.in_title = True
				if name == 'width' and value == '10%':
					self.in_score = True
		if tag == 'a' and self.in_title:
			self.in_a = True
	def handle_data(self,data):
		if self.in_a:
			self.title = data.strip().decode('utf8').encode(type)
		if self.in_score:
			self.score = data.strip().decode('utf8').encode(type)
	def handle_endtag(self,tag):
		if tag == 'tr' and self.in_tr:
			hw_score.append(tuple([self.title,self.score]))
			self.in_tr = False
		if tag == 'td':
			self.in_title = False
			self.in_score = False
			self.in_td = False
		if tag == 'a' and self.in_title:
			self.in_a = False
		if tag == 'table' and self.in_table:
			self.in_table = False
	
class getOrderPackage(HTMLParser):   #get the homework order and the homework files
	global order_package
	global submit_link
	global temp_order_package
	global temp_submit_link
	temp_submit_link = []
	temp_order = ''
	temp_package = ''
	temp_assign_package = ''
	temp_submit_package = ''
	temp_submit_text = ''
	in_order = False
	in_package = False
	in_table = False
	in_order_area = False
	in_submit_area = False
	in_td = False
	td_count = 0
	base = 'http://learn.tsinghua.edu.cn'
	def handle_starttag(self,tag,attrs):
		if tag == 'table':
			for name,value in attrs:
				if name == 'id' and value == 'table_box':
					self.in_table = True
		if tag == 'td' and self.in_table:
			for name,value in attrs:
				if name == 'class' and value == 'tr_2':
					self.td_count = (self.td_count+1)%5
		if tag == 'a' and self.in_table:
			if self.td_count == 3:
				for href,link in attrs:
					if href == 'href':
						#print 'assignment ' + link
						self.temp_assign_package  = self.base + link
			if self.td_count == 0:
				for href,link in attrs:
					if href == 'href':
						#print 'submit ' + link
						self.temp_submit_package = self.base + link				
		if tag == 'textarea' and self.in_table:
			if self.td_count == 2:
				self.in_order_area = True
			if self.td_count == 4:
				self.in_submit_area = True

	def handle_data(self,data):
		if self.in_order_area:
			#print 'test decode error' + data.strip().encode(type)
			try:
				self.temp_order += data.strip().decode('gb18030').encode(type)
			except:
				self.temp_order += data.strip().encode(type)
		if self.in_submit_area:
			try:
				self.temp_submit_text += data.strip().decode('gb18030').encode(type)
			except:
				self.temp_submit_text += data.strip().encode(type)

	def handle_endtag(self,tag):
		if tag == 'table':
			self.in_table = False
		if tag == 'textarea':
			self.in_order_area = False
			self.in_submit_area = False
		if tag == 'html':
			temp_order_package.append(tuple([self.temp_order,self.temp_assign_package]))
			temp_submit_link.append(tuple([self.temp_submit_text,self.temp_submit_package]))
			self.temp_order = ''
			self.temp_submit_text = ''
			self.temp_assign_package = ''
			self.temp_submit_package = ''

class getBbsTitleContent(HTMLParser):
	global title_content
	global temp_title_content
	temp_title = ''
	temp_content = ''
	in_content = False
	in_title = False
	in_tr = False
	def handle_starttag(self,tag,attrs):
		if tag == 'td':
			for name,value in attrs:
				if name == 'class' and value == 'tr_l2':
					self.in_tr = True
					for style,css in attrs:
						if style == 'style':
							self.in_content = True
							self.in_title = False
						elif self.in_tr:
							self.in_content = False
							self.in_title = True
	def handle_data(self,data):
		if self.in_title:
			self.temp_title = data.strip().decode('utf8').encode(type)
		if self.in_content:
			self.temp_content += data.strip().decode('utf8').encode(type)
	def handle_endtag(self,tag):
		if tag == 'td' and self.in_title:
			self.in_title = False
		if tag == 'td' and self.in_content:
			self.in_content = False
		if tag == 'html':
			temp_title_content.append(tuple([self.temp_title,self.temp_content]))
			self.temp_content = ''
			self.temp_title = ''

class MakeTidy():
	def add_html_end(self,src):
		tidysrc = src + '</html>'
		return tidysrc

class UI():
	def view_bar(self,num,total,symbol):
		rate = float(num)/float(total)
		rate_num = int(rate*100)
		print '\r%*s'%(45,']'),
		print '\r%3s%% : ' %(rate_num),
		print '[' + symbol * ((rate_num/3)+1),
		sys.stdout.flush()	

class MyLearn():
	global id_name,file_link,temp_bbs_link,bbs_link
	global bbs,homework
	#global path
	def __init__(self):
		self.base_url = 'http://learn.tsinghua.edu.cn' 
		self.login_url = self.base_url + '/MultiLanguage/lesson/teacher/loginteacher.jsp'               #the login url
		self.past_course_url = self.base_url + '/MultiLanguage/lesson/student/MyCourse.jsp?typepage=2'      #the course list url
		self.current_course_url = self.base_url + '/MultiLanguage/lesson/student/MyCourse.jsp?language=cn'      #the course list url
		self.file_url = self.base_url + '/MultiLanguage/lesson/student/download.jsp?course_id='			#the file url base 
		self.bbs_url = self.base_url + '/MultiLanguage/public/bbs/getnoteid_student.jsp?course_id='     #the bbs url base
		self.hw_url = self.base_url + '/MultiLanguage/lesson/student/hom_wk_brw.jsp?course_id='         #the homwwork url base
		self.hw_score_url = self.base_url + '/MultiLanguage/lesson/student/hom_wk_recmark.jsp?course_id='
		self.cookie = cookielib.LWPCookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
		urllib2.install_opener(self.opener)
		self.name = ''
		self.password = ''
		self.path = ''
		self.size_limit = 100*1024*1024                    #default size limit 100mb
		self.era_choice =  'c'                               #default download the current semester 
		self.working_path = os.getcwd()
		self.temp_name = ''
		self.temp_password = ''
		self.swap_path = ''
		self.swap_name = ''
		self.swap_password = ''
		self.temp_setting_path = ''	
		self.temp_setting_size_limit = ''
		self.temp_era_choice = ''
		self.request = ''
		self.result = ''
		self.content = ''
		self.filename = ''				
		self.PostData = {}
		self.login_success_flag = False
		self.check_login_success_flag = False
		self.config_open_success_flag = False
		self.path_change_success_flag = False
		self.size_change_success_flag = False
		self.era_change_success_flag = False
		self.ui = UI()
	
	def __login(self,option):
		if option == 0 or option == 2 or option == 3:                   #normal login
			self.swap_name = self.name
			self.swap_password = self.password
		if option == 1:
			self.swap_name = self.temp_name
			self.swap_password = self.temp_password
		PostData = {
				'userid':self.swap_name,
				'userpass':self.swap_password,
				'submit1': '%B5%C7%C2%BC'
				}
		try:
			self.request = urllib2.Request(self.login_url,urllib.urlencode(PostData))
			self.result = urllib2.urlopen(self.request,timeout=20)
			self.content = self.result.read()	
		except:
			self.__link_fail_alarm(self.login_url)
			return
		if 'loginteacher_action.jsp' in self.content:
			if option == 0 or option == 2 or option == 3:
				if option == 0:
					print "login succeeded"
					logger.info(' login succeeded')
				if option == 3:
					logger.info(' reconnect succeeded')
				self.login_success_flag = True
			if option == 1:
				self.check_login_success_flag = True
		else:
			if option == 0 or 3:
				self.login_success_flag = False
				if option == 0:
					logger.info(' login failed')
				if option == 3:
					logger.info(' reconnect failed') 
			if option == 1:
				self.check_login_success_flag = False

	def __safe_urlopen_read(self,cnt,url,time): #to open the link with error detection
		link_try_count = cnt
		link_flag = True
		trial_url = url
		content = ''
		while link_flag and link_try_count > 0:
			try:
				src = urllib2.urlopen(trial_url,timeout=time)
				content = src.read()
				link_flag = False
			except:
				self.__error_message(0,'link failure occurs,time ' + str(1+cnt-link_try_count))
				logger.info(' link failure occurs, time ' + str(1+cnt-link_try_count))
				self.__login(3)   #try to reconnect
				link_try_count = link_try_count -1
		if link_flag == True:
			logger.info(' link failure at ' + trial_url)
		return content

	def __course_id_name(self):
		#global path
		if self.era_choice == 'p':                        #download past file                              
			content = self.__safe_urlopen_read(3,self.past_course_url,20)		
			if content == '':
				os._exit(1)
		elif self.era_choice == 'c':                      #download present file
			content = self.__safe_urlopen_read(3,self.current_course_url,20)
			if content == '':
				os._exit(1)
		else:
			content = self.__safe_urlopen_read(3,self.past_course_url,20)#the default 
		get_id_name = getIdName()
		get_id_name.feed(content)
	
	def __course_file_link(self):
		global temp_link
		global file_link
		print '\ngetting file information...'
		get_file_link = getFileLink()
		for i in range(0,len(id_name)):
			self.ui.view_bar(i,len(id_name),'=')
			fileurl = self.file_url + id_name[i][0]
			content = self.__safe_urlopen_read(10,fileurl,20)
			if content == '':
				 #bug exists!! if not open what about the file link?
				self.__error_message(0,' cannot get file link of course ' + id_name[i][1])
				file_link.append([])
				continue
			get_file_link.feed(content)
			file_link.append(temp_link)
			temp_link = []
		self.ui.view_bar(1,1,'=')
		print '\n'

	def __course_bbs_link(self):
		print '\ngetting announcement information...'
		global bbs_link
		global temp_bbs_link
		get_bbs_link = getBbsLink()
		tidify = MakeTidy()
		for i in range(0,len(id_name)):
			self.ui.view_bar(i,len(id_name),'=')
			bbsurl = self.bbs_url + id_name[i][0]
			content = self.__safe_urlopen_read(10,bbsurl,20)
			if content == '':
				logger.info('announcement related url failed %s'%(bbsurl))
				bbs_link.append([])
				continue
			tidysrc = tidify.add_html_end(content)
			get_bbs_link.feed(tidysrc)
			bbs_link.append(temp_bbs_link)
			temp_bbs_link = []
		self.ui.view_bar(1,1,'=')
		print '\n'


	def __course_bbs_title_content(self):
		global temp_title_content
		global title_content
		print 'getting announcement link...'
		get_bbs_title_content = getBbsTitleContent()
		tidify = MakeTidy()
		for i in range(0,len(id_name)):
			self.ui.view_bar(i,len(id_name),'=')
			if len(bbs_link[i]) == 0:
				title_content.append([])
				continue
			for j in range(0,len(bbs_link[i])):
				src = self.__safe_urlopen_read(3,bbs_link[i][j],20)
				if src == '':
					logger.info('announcement related url failed %s'%(bbs_link[i][j]))
					continue
				tidysrc = tidify.add_html_end(src)
				get_bbs_title_content.feed(tidysrc)
			title_content.append(temp_title_content)
			temp_title_content = []
		self.ui.view_bar(1,1,'=')
		print '\n'

	
	def __course_homework_link(self):
		global hw_link_deadline
		global temp_hw_link_deadline
		print 'getting homework information...'
		get_homework_link = getHomeworkLink()
		tidify = MakeTidy()
		#logger.info('course number: id_name %s'%(len(id_name)))
		for i in range(0,len(id_name)):
			self.ui.view_bar(i,len(id_name),'=')
			temp_hw_link_deadline = []
			hwurl = self.hw_url + id_name[i][0]
			content = self.__safe_urlopen_read(3,hwurl,20)
			if content == '':
				logger.info(' homework related url fail %s'%(hwurl))
				hw_link_deadline.append([])
				continue
			tidysrc = tidify.add_html_end(content)
			get_homework_link.feed(tidysrc)
			hw_link_deadline.append(temp_hw_link_deadline)
		self.ui.view_bar(len(id_name),len(id_name),'=')
		print '\n'
		#logger.info('the length of hw_link_deadline %s'%(len(hw_link_deadline)))

	def __course_homework_order_package(self):
		global temp_order_package
		global temp_submit_link
		global order_package
		global submit_link
		global hw_score
		global title_score
		submit_link = []
		get_homework_order_package = getOrderPackage()
		#logger.info('hw_link_deadline length %s'%(len(hw_link_deadline)))
		get_homework_score = getHomeworkScore()
		print 'getting download link...'
		for i in range(0,len(id_name)):
			self.ui.view_bar(i,len(id_name),'=')				
			if len(hw_link_deadline[i])== 0:
				#logger.info('%s has no homework'%(id_name[i][1]))
				order_package.append([])
				submit_link.append([])		
				title_score.append([])
				continue
			score_sourse = self.__safe_urlopen_read(5,self.hw_score_url + id_name[i][0],20)
			if score_sourse == '':
				logger.info(' fail to open score link %s '%(id_name[i][1]))
				title_score.append([])
			get_homework_score.feed(score_sourse)
			title_score.append(hw_score)
			hw_score = []
			for j in range(0,len(hw_link_deadline[i])):
				#print 'HW_LINK_DEADLINE: ' + hw_link_deadline[i][j][1][1]
				src = self.__safe_urlopen_read(5,hw_link_deadline[i][j][0],20)
				if src == '':
					logger.info(' fail to open homework link %s '%(hw_link_deadline[i][j][0])) 
					continue
				get_homework_order_package.feed(src)
			order_package.append(temp_order_package)
			submit_link.append(temp_submit_link)						
			temp_order_package = []
			temp_submit_link = []
				
		self.ui.view_bar(1,1,'=')
		print '\n'
	
	def __error_message(self,opt,msg):
		if opt == 0:
			print '\nerror:' + msg
		if opt == 1:
			print 'warning:' + msg
		if opt == 2:
			print 'info:' + msg
	
	def __check_path(self):
		print self.swap_path
		if os.path.isabs(self.swap_path) == True:
			try:
				os.makedirs(self.swap_path)
				self.valid_path = True
			except:
				if self.swap_path == '':
					self.__error_message(1,'path is empty')
					self.valid_path = False
					return
				self.__error_message(1,'file path conflicts')	
				self.valid_flag = False
				while not self.valid_flag:		
					self.choice = raw_input('are you sure to cover the file path?(y|n)\n') 			
					if self.choice == 'y':
						self.valid_path = True
						self.valid_flag = True	
					elif self.choice == 'n':
						self.valid_path = False
						self.valid_flag = True			
					else:
						self.__error_message(1,'please input y or n')	
		else:
			self.__error_message(1,'Please input abosolute path\nexample:\nWindows:D:\my\download\path\nLinux:/home/user/my/download/path\n')
			self.valid_path = False

	def __get_valid_path(self,option):
		self.valid_path = False
		if option == 0:                       #for first time input
			while not self.valid_path:
				self.path = raw_input('please input the download path:')
				self.swap_path = self.path
				self.__check_path()
		if option == 1:                       #for changing the download path
			while not self.valid_path:
				print 'please input new download path or press q to quit\n'
				self.temp_setting_path = raw_input()
				if self.temp_setting_path == 'q':
					self.path_change_success_flag = False
					return
				self.swap_path = self.temp_setting_path
				self.__check_path()
			self.path_change_success_flag = True

	def __set_past_or_current(self,option): #todo: download past or the current file page; s
		self.valid_flag = False
		if option == 0:
			while not self.valid_flag:		
				self.choice = raw_input('Past semesters or Current semester:(c|p)\n') 			
				if self.choice == 'c':
					self.era_choice = 'c' 
					self.valid_flag = True	
				elif self.choice == 'p':
					self.era_choice = 'p' 	
					self.valid_flag = True	#set the configuration page:let the user change the setting
				else:
					self.__error_message(1,'please input c for current and p for past')
		if option == 1:
			while not self.valid_flag:
				self.choice = raw_input('Past semesters or Current semester:(c|p),press q to quit\n')
				if self.choice == 'c':
					self.temp_era_choice = 'c'
					self.valid_flag = True
				elif self.choice == 'p':
					self.temp_era_choice = 'p'
					self.valid_flag = True
				elif self.choice == 'q':
					self.era_change_success_flag = False
					return
				else:
					self.__error_message(0,'please input c for current and p for past') 
			self.era_change_success_flag = True
				
	def __get_valid_size_limit(self,option):
		pattern = re.compile(r'^\d+(\.\d+)?$')
		#pattern = re.compile(r'^\d+$')
		if option == 0:
			self.size_limit = raw_input('the maximum file size(mb):')
			while not pattern.search(self.size_limit):
				self.size_limit = raw_input('invalid input,the maximum file size(mb):')
		if option == 1:
			self.temp_setting_size_limit = raw_input('the maximum file size(mb):')
			while not pattern.search(self.temp_setting_size_limit):
				self.__error_message(1,'invalid input,enter again or press q to quit')
				self.temp_setting_size_limit = raw_input()		
				if self.temp_setting_size_limit == 'q':
					self.size_change_success_flag = False
					return
			self.size_change_success_flag = True	
				
	def __check_download_directories(self):
		valid_directory = False
		while not valid_directory:
			try:
				os.chdir(self.path)
				valid_directory = True
			except:
				print 'cannot find directory:%s do you want to create one?(y|n):'%(self.path)
				choice = raw_input()
				if choice == 'y':
					clearscreen()
					os.makedirs(self.path)
					os.chdir(self.path)
					valid_directory = True
				elif choice == 'n':
					os._exit(1)
				else:
					print 'please input y or n'

	def __set_download_directories(self):
		self.__check_download_directories()
		for i in range(0,len(id_name)):
			try:
				os.makedirs(id_name[i][1])
			except:
				continue
	
	def __course_save_bbs(self):
		global title_content
		print '\rgenerating announcement...'
		for i in range(0,len(id_name)):
			tempdir = os.path.join(self.path,id_name[i][1])	
		#	print 'temp_dir ' + tempdir  
			os.chdir(tempdir)
			if title_content[i] == []:
				continue
			try:
				os.makedirs('announcement')
			except:
				pass
			os.chdir('announcement')	
			bbs = file(id_name[i][1]+'.html','w')
			bbs.write('<ol>')
			for j in range(0,len(title_content[i])):
				logger.info(id_name[i][1])
				logger.info(title_content[i][j][0])
				bbs.write('<li><h4>'+title_content[i][j][0]+'</h4>')
				bbs.write('<p>'+title_content[i][j][1]+'</p></li>')
			bbs.close()
	
	def __link_fail_alarm(self,url):
		self.__error_message(1,'link failure occurs')
		logger.info(' link failure at ' + url)

	def __course_download_homework(self):
		unsubmit_count = 0
		filename_get = ''
		filename_sent = ''
		head_format = '<table border="1"><caption><b>%s</b></caption><tr><th>%s</th><th>%s</th></tr>'
		line_format = '<tr><td>%s</td><td>%s</td></tr>'
		os.chdir(self.path)
		try:
			os.makedirs('todo')
		except:
			pass
		os.chdir('todo')
		todo = file('todo.txt','wt')
		todo.truncate()
		os.chdir(self.path)
		for i in range(0,len(id_name)):
			unsubmit_count = 0		
			if order_package[i] == []:          #if no assignment,continue  
				continue             
			todo.write('\n%s:\n'%(id_name[i][1]))
			tempdir = os.path.join(self.path,id_name[i][1])		
			os.chdir(tempdir)
			try:
				os.makedirs('report')
			except:
				pass
			os.chdir('report')
			inform = file('homework_report.txt','wt')	
			inform.truncate()
			inform.write(id_name[i][1] + ' unsubmitted:\n')
			score = file('homework_score.html','wt')
			score.truncate()
			score.write(head_format%(id_name[i][1],'Title','Score'))
			for n in range(0,len(title_score[i])):
				score.write(line_format%(title_score[i][n][0],title_score[i][n][1]))
			score.close()
			os.chdir(tempdir)
			try:
				os.makedirs('homework')
			except:
				pass
			os.chdir('homework')				
			for j in range(0,len(order_package[i])):
				os.chdir(os.path.join(tempdir,'homework'))
				self.deadline = hw_link_deadline[i][j][1][1]	
				self.title = hw_link_deadline[i][j][1][0]
				if (j+1) < 10:
					digit = '00%d'%(j+1)
				if (j+1) >= 10 and (j+1) < 100:
					digit = '0%d'%(j+1)
				temp_path = digit  + '-' + self.title.strip().decode('utf-8').encode(type) #add number to prevent same name
				try:
					os.makedirs(temp_path)
				except:
					pass
				os.chdir(temp_path)
				if order_package[i][j][0] != '':
					order = file('order-' + self.deadline + '.txt','w')
					order.write('******deadline ' + self.deadline + ' ******\n')
					order.write(order_package[i][j][0])
					order.close()
				if order_package[i][j][1] != '':
					content = ''
					location = ''
					length = ''
					try:
						content = urllib2.urlopen(order_package[i][j][1])
					except:
						logger.info(' link failure at ' + order_package[i][j][1])
						content = ''	
					if content != '':
						try:
							location = content.headers['Content-Disposition']
						except KeyError:
							logger.info(' header failure at ' + order_package[i][j][1])
							location = ''
					if location != '':
						try:
							length = content.headers['Content-Length']
						except KeyError:
							logger.info(' header hailure at ' + order_package[i][j][1])
							length = ''
					if length != '':
						filename_get = location[21:-1].strip().decode('gb18030').encode(type)
						pattern = re.compile(r'^\d+_\d+_')
						logger.info("FILENAME BEFORE AMMENDMENT" + filename_get)	
						filename_get = re.sub(pattern,'',filename_get)
						logger.info("filename_get " + filename_get)
						filelist = os.listdir(os.path.join(tempdir,'homework',temp_path))
						if filename_get not in filelist:
							filecontent = ''
							try:
								filecontent = content.read()
							except:
								self.__error_message(2,'fail to download : ' + filename_get) 
								logger.info('fail to download: %s\n'%(filename_get))
								filecontent = ''
							if filecontent != '':
								print 'downloading: ' + filename_get
								filepath = file(filename_get,'wb')
								filepath.writelines(filecontent)
						else:
							local_length = os.path.getsize(filename_get)		
							if int(length) == local_length:
								self.__error_message(2,'%s: has been downloaded,move on'%(filename_get))
							else:
								filecontent = ''
								try:
									filecontent = content.read()
								except:
									self.__error_message(2,'fail to update : ' + filename_get)
									logger.info('fail to update: %s\n'%(filename_get))
								if filecontent != '':
									print 'updating: ' + filename_get
									filepath = file(filename_get,'wb')
									filepath.writelines(filecontent)

				if submit_link[i][j] != tuple(['','']):     #if homework submitted
					try:
						os.makedirs('submit')
					except:
						pass
					os.chdir(os.path.join(tempdir,'homework',temp_path,'submit'))
					if submit_link[i][j][0] != '':
						sub = file('submit-text.txt','w')
						sub.write(submit_link[i][j][0])	
						sub.close()
					if submit_link[i][j][1] != '':
						pattern = re.compile(r'^\d+_\d+_\d+_')
						try:
							content = urllib2.urlopen(submit_link[i][j][1])
							location = content.headers['Content-Disposition']
							logger.info('submit content' + location[21:-1])
							filename_sent = location[21:-1].strip().decode('gb18030').encode(type)	
							filename_sent = re.sub(pattern,'',filename_sent)
							logger.info('after ammendment' + filename_sent)
							filelist = os.listdir(os.path.join(tempdir,'homework',temp_path , 'submit'))
							if filename_sent not in filelist:      #different submit all downloaded
								print 'downloading: ' + filename_sent
								filepath = file(filename_sent,'wb')
								filepath.writelines(content.read())
						except:
							logger.info(' homework submit file %s not downloaded'%(filename_sent))
				else:
					unsubmit_count += 1
					todo.write('deadline: %s  %s \n'%(self.deadline,self.title.strip().decode('utf-8').encode(type)))
					inform.write('deadline: %s  %s \n'%(self.deadline,self.title.strip().decode('utf-8').encode(type)))

			if unsubmit_count == 0:
				#tempdir = os.path.join(self.path,id_name[i][1])		
				todo.write('all clear\n')
				inform.write('all clear')
			inform.close()
		#self.ui.view_bar(1,1,'#')
	
	def __course_download_file(self):
		print '\ndownloading file...'
		if self.size_limit == '':
			print 'Warning:size limit == null,set to 10mb'
			self.size_limit = '10'
		limit = float(self.size_limit)*1024*1024
		pattern = re.compile(r'_\d+\.')
		report_flag = False	
		for i in range(0,len(id_name)):
			report_flag = False
			tempdir = os.path.join(self.path,id_name[i][1])
			print tempdir
			os.chdir(tempdir)
			try:
				os.makedirs('report')
			except:
				pass
			os.chdir('report')
			inform = file('file_report.txt','wt')
			inform.truncate()
			inform.write('file report:\n')
			os.chdir(tempdir)
			try:
				os.makedirs('file')
			except:
				pass
			os.chdir('file')
			for j in range(0,len(file_link[i])):
				try:
					src = urllib2.urlopen(file_link[i][j],timeout=20)
				except:
					self.__link_fail_alarm(file_link[i][j])		
					inform.write(' link failure at ' + file_link[i][j] + '\n')	
					report_flag = True	
					continue
				try:
					location = src.headers['Content-Disposition']
				except KeyError:
					inform.write('cannot get file name: ' + file_link[i][j] + '\n')
					logger.info(' header failure at ' + file_link[i][j])	
					continue
				try:
					length = src.headers['Content-Length']
				except KeyError:
					inform.write('cannot get file size: ' + file_link[i][j] + '\n')	
					logger.info(' header failure at ' + file_link[i][j])
					report_flag = True	
					continue
				self.filename = location[21:-1].strip().decode('gb18030').encode(type)
				self.filename = re.sub(pattern,'.',self.filename)
				filelist = os.listdir(os.path.join(tempdir,'file'))
				if self.filename not in filelist:
					if (int(length)>limit):
						self.__error_message(2,'%s: file size larger than limit,move on'%(self.filename))
						inform.write('exceeds size limit: ' +  self.filename + '\n')
						report_flag = True
						continue
					try:
						content = src.read()   # the download core 
					except:
						inform.write('fail to download: ' + self.filename + '\n')
						report_flag = True
						continue
					print 'downloading: ' + self.filename	
					filepath = file(self.filename,'wb')
					filepath.writelines(content)
				else:                        #if filename already existed
					local_length = os.path.getsize(self.filename)
					if int(length) == local_length:
						self.__error_message(2,'%s: has been downloaded,move on'%(self.filename))
					else:
						self.__error_message(1,'%s: file size has been changed'%(self.filename))				
						inform.write('check for update:'+ self.filename + '\n')	
						if(int(length)>limit):
							self.__error_message('exceeds size limit: %s\n'%(self.filename))
							report_flag = True
							continue
						else:
							try:
								content = src.read()
							except:
								inform.write('fail to update: %s\n'%(self.filename))
								report_flag = True
								continue
							print 'downloading: ' + self.filename	
							filepath = file(self.filename,'wb')
							filepath.writelines(content)
			if report_flag ==  False:
				#print 'ALL DOWNLOADED ALL DOWNLOADED ALL DOWNLOADED '
				inform.write('all downloaded\n')
		

	def __input_login_message(self,option):
		if option == 0:                       #first login 
			self.name = raw_input('Name:')
			self.password = getpass.getpass()
		if option == 1:                      # change the config
			self.temp_name = raw_input('Name:')
			self.temp_password = getpass.getpass()

	def __logincontrol(self,option):  #login control with option
		if option == 0:               #login using the existing config data
			self.__login(0)
		if option == 1:               #first login
			self.__input_login_message(0)
			self.__login(0)
		while not self.login_success_flag:
			control = raw_input('login failed,try again?(y|n) ')
			if control == 'y':
				if option == 0:
					self.__login(0)
				if option == 1:
					self.__input_login_message(0)	
					self.__login(0)
			elif control == 'n':
				os._exit(1)
				#sys.exit(1)
			else:
				print 'please input y or n'

	def __getconfig(self,flag):    #get the config data, if file not exists, create the file
		os.chdir(self.working_path)         
		try:
			config = open('config.dat','r')
			self.name = base64.b64decode(config.readline().strip('\n'))
			self.password = base64.b64decode(config.readline().strip('\n'))
			self.path = base64.b64decode(config.readline().strip('\n'))
			self.size_limit = base64.b64decode(config.readline().strip('\n'))
			self.era_choice = base64.b64decode(config.readline().strip('\n'))
			config.close()
			if flag == 0:
				self.__logincontrol(0)
			elif flag == 1:
				return
		except IOError:
			if flag == 0:
				self.__logincontrol(1)
				config = file('config.dat','w')
				config.write(base64.b64encode(self.name) + '\n')
				config.write(base64.b64encode(self.password) + '\n')
				self.__get_valid_path(0)
				self.__get_valid_size_limit(0)
				self.__set_past_or_current(0)
				config.write(base64.b64encode(self.path) + '\n')
				config.write(base64.b64encode(self.size_limit) + '\n')
				config.write(base64.b64encode(self.era_choice) + '\n')
			elif flag == 1:
				logger.info(' configure file lost')
				self.__error_message(0,'configure file lost')	
	

	def __clearvar(self):
		global temp_link
		del temp_link[:]

		global hw_score
		del hw_score[:]

		global title_score 
		del title_score[:]

		global id_name
		del id_name[:]
		#id_name = []
		global file_link
		del file_link[:]
		#file_link = []
		global bbs_link
		del bbs_link[:]
		#bbs_link = []
		global hw_link
		del hw_link[:]
		#hw_link = []
		global title_content
		del title_content[:]
		#title_content = []
		global order_package
		del order_package[:]
		#order_package = []
		global temp_title_content
		del temp_title_content[:]
		#temp_title_content = []
		global temp_order_package	
		del temp_order_package[:]
		#temp_order_package = []
		global hw_link_deadline	
		del hw_link_deadline[:]
		#hw_link_deadline = []

	def __setconfig(self):
		self.opt = 0
		while self.opt != 5:
			print 'set the configure'
			print '1.change name and password'
			print '2.change save path'
			print '3.change size limit'
			print '4.change period'
			print '5.quit setting'
			self.opt = raw_input()   
			if self.opt == '1':
				self.__set_name_password()
				clearscreen()
				if not self.check_login_success_flag:
					self.__error_message(1,'wrong name or password setting')
				continue
			if self.opt == '2':
				clearscreen()
				self.__set_path()
				self.__getconfig(1)    #refresh the config data
				clearscreen()
				continue
			if self.opt == '3':
				clearscreen()
				self.__set_size_limit()
				self.__getconfig(1)
				clearscreen()
				continue
			if self.opt == '4':
				clearscreen()
				self.__set_era_choice()
				self.__getconfig(1)
				clearscreen()
				continue
			if self.opt == '5':
				break
			else:
				clearscreen()
				continue

	def __get_temp_config_data(self):
		os.chdir(self.working_path)          #change directory to the working path
		try:
			config = open('config.dat','r')
		except:
			self.__error_message(0,'open config file failed')
			self.config_open_success_flag = False
			return
		self.config_open_success_flag = True 
		self.now_name = config.readline().strip('\n')
		self.now_password = config.readline().strip('\n')
		self.now_path = config.readline().strip('\n')
		self.now_size_limit = config.readline().strip('\n')
		self.now_era_choice = config.readline().strip('\n')
		config.close()
	
	def __set_temp_config_data(self):
		os.chdir(self.working_path)
		try:
			config = open('config.dat','w')
		except:
			self.__error_message(0,'open config file failed')		
			self.__error_message(1,'cannot rewrite config file')
			self.config_open_success_flag = False
			return
		self.config_open_success_flag = True
		config.write(self.now_name + '\n')
		config.write(self.now_password + '\n')
		config.write(self.now_path + '\n')
		config.write(self.now_size_limit + '\n')
		config.write(self.now_era_choice + '\n')
		config.close()
		
	def __set_name_password(self):
		self.config_open_success_flag = False
		self.__get_temp_config_data()
		if not self.config_open_success_flag:
			return
		self.__input_login_message(1)            #change the login information
		self.__login(1)                          #try to login and check the information
		self.__login(2)							 #turn back to the current id user 
		if not self.check_login_success_flag:
			return
		if self.check_login_success_flag:
			self.now_name = base64.b64encode(self.temp_name) 
			self.now_password = base64.b64encode(self.temp_password)
			self.__set_temp_config_data()

	def __set_path(self):
		self.config_open_success_flag = False
		self.__get_temp_config_data()
		if not self.config_open_success_flag:
			return
		print 'now path: ' + base64.b64decode(self.now_path)
		self.__get_valid_path(1)     #input the new download path
		if self.path_change_success_flag:
			self.now_path = base64.b64encode(self.temp_setting_path)
			self.__set_temp_config_data()
		else:
			self.__error_message(1,'path not changed')
	
	def __set_size_limit(self):
		self.config_open_success_flag = False
		self.__get_temp_config_data()
		if not self.config_open_success_flag:
			return
		print 'now size limit: ' + base64.b64decode(self.now_size_limit)
		self.__get_valid_size_limit(1)
		if self.size_change_success_flag:
			self.now_size_limit = base64.b64encode(self.temp_setting_size_limit)
			self.__set_temp_config_data()
		else:
			self.__error_message(1,'size limit not changed')
	
	def __set_era_choice(self):
		self.config_open_success_flag = False
		self.__get_temp_config_data()
		if not self.config_open_success_flag:
			return
		era_choice = base64.b64decode(self.now_era_choice)
		if era_choice == 'c':
			print 'now period: current semester'
		if era_choice == 'p':
			print 'now period: past semesters'
		self.__set_past_or_current(1)
		if self.era_change_success_flag:
			self.now_era_choice = base64.b64encode(self.temp_era_choice)
			self.__set_temp_config_data()
		else:
			self.__error_message(1,'period choice not changed')
	
	def __initialize(self):
		if not self.login_success_flag:
			return
		self.__clearvar()
		self.__check_download_directories()
		self.__course_id_name()
		self.__set_download_directories()
	
	def startup(self):
		self.__getconfig(0) #get the config and login
		#self.__initialize()

	def get_file(self):
		if not self.login_success_flag:
			return
		self.__initialize()	   
		self.__course_file_link()
		self.__course_download_file()

	def get_bbs(self):
		if not self.login_success_flag:
			return
		self.__initialize()
		self.__course_bbs_link()
		self.__course_bbs_title_content()
		self.__course_save_bbs()

	def get_homework(self):
		if not self.login_success_flag:
			return
		self.__initialize()	
		self.__course_homework_link()
		self.__course_homework_order_package()
		self.__course_download_homework()
		
	def set_config(self):
		if not self.login_success_flag:
			return
		self.__setconfig()


def main_control():
	control = raw_input('Please select the option:\n1.download all \
	    \n2.download course files\n3.download homework\n4.download announcement\n5.setting\n6.exit\n')
	return control

mylearn = MyLearn()
mylearn.startup()

control = main_control()
while control != '6':
	if control == '1':
		print 'begin to download all '
		mylearn.get_bbs()
		mylearn.get_homework()
		mylearn.get_file()
		print '\nall completed!'
		control = main_control()
		continue
	if control == '2':
		print '\nbegin to download course files'
		mylearn.get_file()
		print '\ncourse file download completed'
		control = main_control()
		continue
	if control == '3':
		print '\nbegin to download homework'
		mylearn.get_homework()
		print '\nhomework download completed'
		control = main_control()
		continue
	if control == '4':
		print '\nbegin to download announcement'
		mylearn.get_bbs()
		print '\nannouncement download completed'
		control = main_control()
		continue
	if control == '5':
		clearscreen()
		mylearn.set_config()
		clearscreen()
		control = main_control()
		continue
	if control == '6':
		break
	else:
		clearscreen()
		print 'illegal input,please select from 1 to 6'
		control = main_control()
	
'''
mylearn.get_bbs()
mylearn.get_homework()
mylearn.get_file()
'''

