from apscheduler.schedulers.background import BackgroundScheduler #定时任务
import requests
schedulerdate = BackgroundScheduler()

schedulerdate.start()

#存库接口
Url01 = 'http://192.168.2.94/Unattended/TimingTask'  # 新增jobid到数据库接口
Url02 = 'http://192.168.2.94/Unattended/TimingTaskCheck'  # 新增jobsid到数据库接口



#存放操作日志
# class except_log:
#     def putlog(self, data):
#         url = 'http://quality-test.xueba100.com/LogApi/addoperationlog'
#         req = requests.post(url, json=data)  # 请求权限接口获取对应接口列表
#         req_result = req.json()
#         print('l', req_result)



class except_log:
    def putlog(self, tree_id,uid,operation_content,operation_result,project_type):
        datalog = {
            "tree_id": tree_id,
            "uid": uid,
            "operation_content": operation_content,
            "operation_result": operation_result,
            "project_type":project_type
        }
        url = 'http://quality-test.xueba100.com/LogApi/addoperationlog'
        req = requests.post(url, json=datalog)  # 请求权限接口获取对应接口列表
        req_result = req.json()
        print('result', req_result)