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

host = '10.2.1.145'
port = '3306'
database = 'fudao_qatest_quality'
username = 'quality'
password = 'ntSmlzGNRJuYt9wzyMBE'
'''

host = 'rm-2zec97m16pwzo3t82.mysql.rds.aliyuncs.com'
port = '3306'
database = 'fudao_quality'
username = 'admin_product'
password = 'admin@product123456'


DB_URL = "mysql+pymysql://{username}:{password}@{host}:{port}/{database}?charset=utf8".format(username=username,password=password,host=host,port=port,database=database)
SQLALCHEMY_DATABASE_URI = DB_URL

SQLALCHEMY_COMMIT_ON_TEARDOWN = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_ECHO= True





class KEY_TOKEN:
    #session 迷药
    SECRET_KEY = 'nihaomeinihaomei'
    # 过期时间
    EXPIRATION = 1800000


SECRET_KEY = 'ni zhen mei'

