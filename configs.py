
# host = '127.0.0.1'
# port = '3306'
# database = 'Flask_demo'
# username = 'root'
# password = 'bsk123'


#测试环境
'''
host = '10.2.1.203'
port = '3306'
database = 'fudao_quality'
username = 'wenba'
password = '2njkRQ3sUqW2Q8w2qoHvgVURQyjsK5hK'
'''


'''
host = '192.168.2.44'
port = '3306'
database = 'fudao_qatest_quality'
username = 'wenba_quality_rw'
password = 'ddc4bjiF2kx&45Ct2oCd'
'''



host = '10.2.1.145'
port = '3306'
database = 'fudao_qatest_quality'
username = 'quality'
password = 'ntSmlzGNRJuYt9wzyMBE'


DB_URL = "mysql://{username}:{password}@{host}:{port}/{database}?charset=utf8".format(username=username,password=password,host=host,port=port,database=database)
SQLALCHEMY_DATABASE_URI = DB_URL

SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO= True



#mysql -uquality -pntSmlzGNRJuYt9wzyMBE  -h10.2.1.145
#mysql -uwenba_quality_rw -pddc4bjiF2kx&45Ct2oCd -h192.168.2.44
class KEY_TOKEN:
    #session 迷药
    SECRET_KEY = 'nihaomeinihaomei'
    # 过期时间
    EXPIRATION = 1800000


SECRET_KEY = 'ni zhen mei'





