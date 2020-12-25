from apscheduler.schedulers.background import BackgroundScheduler #定时任务
import requests
schedulerdate = BackgroundScheduler()
schedulerdate.start()


#存库接口
Url01 = 'http://10.55.143.27/Unattended/TimingTask'  # 新增jobid到数据库接口
Url02 = 'http://10.55.143.27/Unattended/TimingTaskCheck'  # 新增jobsid到数据库接口

#监控项目生成脚本模版
monitor_tmp_script001 = '/mnt/monitor_product/temples/script_generation/monitor_script_temple.py' #业务脚本生成模版
monitor_tmp_script002 = '/mnt/monitor_product/temples/script_generation/monitor_script002_temple.py' #逻辑脚本生成模版
monitor_cmd_script001 = '/mnt/monitor_product/monitor_scripts/{username}-monitorscripts-implement001-{date}.py' #业务脚本生成
monitor_cmd_script002 = '/mnt/monitor_product/monitor_scripts/{username}-monitorscripts-implement-{date}.py' #逻辑脚本生成

#监控项目执行命令主机环境，默认web服务器那台
get_host = 'http://wenba-sba-web.in_prod.wenba100.com/instance/getInstanceByServiceNameForTestGroup'

class except_log:
    def putlog(self, tree_id,uid,operation_content,operation_result,project_type):
        datalog = {
            "tree_id": tree_id,
            "uid": uid,
            "operation_content": operation_content,
            "operation_result": operation_result,
            "project_type":project_type
        }
        url = 'http://quality.xueba100.com/LogApi/addoperationlog'
        req = requests.post(url, json=datalog)  # 请求权限接口获取对应接口列表
        req_result = req.json()
        print('result', req_result)
