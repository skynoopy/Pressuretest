(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-4327ec05"],{1472:function(t,e,r){"use strict";r.d(e,"f",(function(){return o})),r.d(e,"n",(function(){return a})),r.d(e,"p",(function(){return n})),r.d(e,"k",(function(){return s})),r.d(e,"o",(function(){return u})),r.d(e,"v",(function(){return l})),r.d(e,"e",(function(){return d})),r.d(e,"a",(function(){return c})),r.d(e,"g",(function(){return f})),r.d(e,"q",(function(){return p})),r.d(e,"b",(function(){return m})),r.d(e,"h",(function(){return h})),r.d(e,"s",(function(){return g})),r.d(e,"t",(function(){return v})),r.d(e,"l",(function(){return b})),r.d(e,"r",(function(){return y})),r.d(e,"d",(function(){return _})),r.d(e,"j",(function(){return S})),r.d(e,"u",(function(){return O})),r.d(e,"c",(function(){return A})),r.d(e,"i",(function(){return j})),r.d(e,"m",(function(){return x}));r("7f7f");var i=r("337a");function o(t){var e=t.group_name,r=t.project_id;return Object(i["a"])({url:"/AuthorityApi/group",method:"post",data:{group_name:e,project_id:r}})}function a(){return Object(i["a"])({url:"/AuthorityApi/group",method:"get"})}function n(){return Object(i["a"])({url:"/AuthorityApi/project",method:"get"})}function s(t){var e=t.group_id,r=t.group_name,o=t.project_id;return Object(i["a"])({url:"/AuthorityApi/group",method:"PUT",data:{group_id:e,group_name:r,project_id:o}})}function u(t){return Object(i["a"])({url:"/AuthorityApi/groupuser",method:"get",params:{group_id:t}})}function l(t){var e=t.username,r=void 0===e?"":e;return Object(i["a"])({url:"/AuthorityApi/groupuseradd",method:"post",data:{username:r}})}function d(t){var e=t.group_id,r=t.uid,o=t.type,a=void 0===o?1:o;return Object(i["a"])({url:"/AuthorityApi/checkgroupuser",method:"post",data:{group_id:e,uid:r,type:a}})}function c(t){var e=t.group_id,r=t.uid;return Object(i["a"])({url:"/AuthorityApi/groupuser",method:"POST",data:{group_id:e,uid:r}})}function f(t){var e=t.group_id,r=t.uid;return Object(i["a"])({url:"/AuthorityApi/groupuser",method:"DELETE",data:{group_id:e,uid:r}})}function p(){return Object(i["a"])({url:"/AuthorityApi/user",method:"get"})}function m(t){var e=t.name,r=t.username,o=t.role,a=t.ip_type;return Object(i["a"])({url:"/AuthorityApi/user",method:"POST",data:{name:e,username:r,role:o,ip_type:a}})}function h(t){return Object(i["a"])({url:"/AuthorityApi/user",method:"DELETE",data:{uid:t}})}function g(t){return Object(i["a"])({url:"/AuthorityApi/userinfo",method:"get",params:{uid:t}})}function v(t){return Object(i["a"])({url:"/AuthorityApi/usergroup",method:"get",params:{uid:t}})}function b(t){var e=t.uid,r=t.name,o=t.role,a=t.type;return Object(i["a"])({url:"/AuthorityApi/user",method:"put",data:{uid:e,name:r,role:o,type:a}})}function y(t){return Object(i["a"])({url:"/AuthorityApi/usergroupadd",method:"POST",data:{uid:t}})}function _(t){var e=t.uid,r=t.group_id;return Object(i["a"])({url:"/AuthorityApi/usergroup",method:"POST",data:{uid:e,group_id:r}})}function S(t){var e=t.uid,r=t.group_id;return Object(i["a"])({url:"/AuthorityApi/usergroup",method:"DELETE",data:{uid:e,group_id:r}})}function O(t){var e=t.uid;return Object(i["a"])({url:"/AuthorityApi/checkuserenv",method:"post",data:{uid:e}})}function A(t){var e=t.uid,r=t.ip_type;return Object(i["a"])({url:"/AuthorityApi/userenv",method:"post",data:{uid:e,ip_type:r}})}function j(t){var e=t.uid,r=t.ip_type;return Object(i["a"])({url:"/AuthorityApi/userenv",method:"DELETE",data:{uid:e,ip_type:r}})}function x(t){return Object(i["a"])({url:"/AuthorityApi/envipinfo",method:"POST",data:{ip_type:t}})}},"346b":function(t,e,r){"use strict";r.r(e);var i=function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("el-card",[r("el-row",[r("el-col",{attrs:{span:10}},[r("el-card",{staticClass:"box-card"},[r("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[r("span",[t._v("员工列表")])]),t._v(" "),r("el-row",[r("el-col",{attrs:{span:15}},[r("el-input",{attrs:{placeholder:"搜索员工","suffix-icon":"el-icon-search",clearable:!0},on:{input:t.searchStaff},model:{value:t.staffKey,callback:function(e){t.staffKey=e},expression:"staffKey"}})],1),t._v(" "),r("el-col",{attrs:{span:6,offset:1}},[r("el-button",{attrs:{type:"primary",icon:"el-icon-plus"},on:{click:t.handleCreatStaff}},[t._v("新建员工")])],1)],1),t._v(" "),t._l(t.staffList,(function(e){return r("div",{key:e.id,staticClass:"text item",class:t.selUser.id===e.id?"isActive":"",staticStyle:{height:"24px","line-height":"24px"},on:{click:function(r){return t.showUserInfo(e)}}},[r("div",{staticStyle:{cursor:"pointer",width:"80%",overflow:"hidden","text-overflow":"ellipsis",float:"left"}},[t._v(t._s(e.name)+"（"+t._s(e.username)+"）")]),t._v(" "),r("div",{staticStyle:{cursor:"pointer",float:"right"},on:{click:function(){return t.handleDeleteStaff(e)}}},[r("i",{staticClass:"el-icon-delete"})])])}))],2)],1),t._v(" "),t.showRight?r("el-col",{attrs:{span:14}},[r("el-card",{staticClass:"box-card"},[r("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[r("span",[t._v("个人信息")]),t._v(" "),r("el-button",{staticStyle:{float:"right"},attrs:{type:"primary"},on:{click:t.handleEditMsg}},[t._v("编辑信息")])],1),t._v(" "),r("el-row",[r("el-col",{staticStyle:{"margin-bottom":"10px"},attrs:{span:8}},[t._v("UID: "),r("span",[t._v(t._s(t.curUserInfo.id))])]),t._v(" "),r("el-col",{staticStyle:{"margin-bottom":"10px"},attrs:{span:8}},[t._v("姓名: "),r("span",[t._v(t._s(t.curUserInfo.name))])]),t._v(" "),r("el-col",{staticStyle:{"margin-bottom":"10px"},attrs:{span:8}},[t._v("邮箱: "),r("span",[t._v(t._s(t.curUserInfo.username))])]),t._v(" "),r("el-col",{staticStyle:{"margin-bottom":"10px"},attrs:{span:8}},[t._v("角色: "),r("span",[t._v(t._s(0===t.curUserInfo.role?"开发":1===t.curUserInfo.role?"测试":""))])])],1)],1),t._v(" "),r("el-card",{staticClass:"box-card"},[r("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[r("span",[t._v("所属分组")]),t._v(" "),r("el-button",{staticStyle:{float:"right"},attrs:{type:"primary"},on:{click:t.handleAddGroup}},[t._v("添加分组")])],1),t._v(" "),r("el-row",t._l(t.userGroup,(function(e){return r("el-col",{key:e.id,staticStyle:{"margin-bottom":"10px"},attrs:{span:6}},[t._v("\n              "+t._s(e.group_name)+"\n              "),r("span",{on:{click:function(r){return t.handleDeleteGroup(e)}}},[r("i",{staticClass:"el-icon-delete"})])])})),1)],1),t._v(" "),r("el-card",{staticClass:"box-card"},[r("div",{staticClass:"clearfix",attrs:{slot:"header"},slot:"header"},[r("span",[t._v("授权环境")]),t._v(" "),r("el-button",{staticStyle:{float:"right"},attrs:{type:"primary"},on:{click:t.handleEditEnv}},[t._v("添加环境")])],1),t._v(" "),r("el-row",t._l(t.ipType,(function(e){return r("el-col",{key:e,staticStyle:{"margin-bottom":"10px"},attrs:{span:6}},[t._v(t._s(t.typeEnv[e])+"\n              "),r("i",{staticClass:"el-icon-delete",staticStyle:{"margin-left":"4px"},on:{click:function(r){return t.delUserEnv(e)}}})])})),1)],1)],1):t._e()],1),t._v(" "),r("el-dialog",{attrs:{title:"新建员工",visible:t.visible},on:{"update:visible":function(e){t.visible=e}}},[r("el-form",{ref:"addStaffEl",attrs:{model:t.addStaffForm,rules:t.addStaffRules}},[r("el-form-item",{attrs:{label:"登录邮箱","label-width":t.formLabelWidth,prop:"username"}},[r("el-input",{model:{value:t.addStaffForm.username,callback:function(e){t.$set(t.addStaffForm,"username",e)},expression:"addStaffForm.username"}})],1),t._v(" "),r("el-form-item",{attrs:{label:"姓名","label-width":t.formLabelWidth,prop:"name"}},[r("el-input",{model:{value:t.addStaffForm.name,callback:function(e){t.$set(t.addStaffForm,"name",e)},expression:"addStaffForm.name"}})],1),t._v(" "),r("el-form-item",{attrs:{label:"角色","label-width":t.formLabelWidth,prop:"role"}},[r("el-radio-group",{model:{value:t.addStaffForm.role,callback:function(e){t.$set(t.addStaffForm,"role",e)},expression:"addStaffForm.role"}},[r("el-radio",{attrs:{label:0,value:0}},[t._v("开发")]),t._v(" "),r("el-radio",{attrs:{label:1,value:1}},[t._v("测试")])],1)],1)],1),t._v(" "),r("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[r("el-button",{on:{click:t.cancleAdddStaff}},[t._v("取 消")]),t._v(" "),r("el-button",{attrs:{type:"primary"},on:{click:t.addStaffConfim}},[t._v("确 定")])],1)],1),t._v(" "),r("el-dialog",{attrs:{title:"个人信息",visible:t.msgVisible},on:{"update:visible":function(e){t.msgVisible=e}}},[r("el-form",{ref:"editUserInfoEl",attrs:{model:t.editUserInfo,rules:t.addStaffRules}},[r("el-form-item",{attrs:{label:"姓名","label-width":t.formLabelWidth,prop:"name"}},[r("el-input",{model:{value:t.editUserInfo.name,callback:function(e){t.$set(t.editUserInfo,"name",e)},expression:"editUserInfo.name"}})],1),t._v(" "),r("el-form-item",{attrs:{label:"角色","label-width":t.formLabelWidth,prop:"role"}},[r("el-radio-group",{model:{value:t.editUserInfo.role,callback:function(e){t.$set(t.editUserInfo,"role",e)},expression:"editUserInfo.role"}},[r("el-radio",{attrs:{label:0,value:0}},[t._v("开发")]),t._v(" "),r("el-radio",{attrs:{label:1,value:1}},[t._v("测试")])],1)],1)],1),t._v(" "),r("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[r("el-button",{on:{click:t.cancleEditUserInfo}},[t._v("取 消")]),t._v(" "),r("el-button",{attrs:{type:"primary"},on:{click:t.editUserInfoConfirm}},[t._v("确 定")])],1)],1),t._v(" "),r("el-dialog",{attrs:{title:"添加分组",visible:t.addGroupVisible},on:{"update:visible":function(e){t.addGroupVisible=e}}},[r("el-form",{ref:"addGrouformEl",attrs:{model:t.addGrouform,rules:t.addStaffRules}},[r("el-form-item",{attrs:{label:"选择分组","label-width":t.formLabelWidth,prop:"group"}},[r("el-select",{attrs:{placeholder:"请选择分组"},model:{value:t.addGrouform.group,callback:function(e){t.$set(t.addGrouform,"group",e)},expression:"addGrouform.group"}},t._l(t.groupList,(function(t){return r("el-option",{key:t.id,attrs:{label:t.group_name,value:t.id}})})),1)],1)],1),t._v(" "),r("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[r("el-button",{on:{click:t.cancleAddGroup}},[t._v("取 消")]),t._v(" "),r("el-button",{attrs:{type:"primary"},on:{click:t.addGroup}},[t._v("确 定")])],1)],1),t._v(" "),r("el-dialog",{attrs:{title:"添加环境",visible:t.editEnvVisible},on:{"update:visible":function(e){t.editEnvVisible=e}}},[r("el-form",{attrs:{model:t.form}},[r("el-form-item",{attrs:{label:"选择环境","label-width":t.formLabelWidth}},[r("el-select",{model:{value:t.form.type,callback:function(e){t.$set(t.form,"type",e)},expression:"form.type"}},t._l(t.userNotEnv,(function(e){return r("el-option",{attrs:{label:t.typeEnv[e],value:e}})})),1)],1)],1),t._v(" "),r("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[r("el-button",{on:{click:t.cancleIpTypes}},[t._v("取 消")]),t._v(" "),r("el-button",{attrs:{type:"primary"},on:{click:t.editIpTypes}},[t._v("确 定")])],1)],1)],1)},o=[],a=(r("28a5"),r("96cf"),r("3b8d")),n=(r("7f7f"),r("1472")),s={name:"StaffManagement",data:function(){return{editEnvVisible:!1,addGroupVisible:!1,msgVisible:!1,visible:!1,staffList:["员工1","员工2"],form:{type:""},formLabelWidth:"120px",addStaffForm:{type:[]},addStaffRules:{username:[{type:"email",message:"邮箱格式不正确",trigger:["blur","change"]},{required:!0,message:"请输入邮箱",trigger:["blur","change"]}],name:[{required:!0,message:"请输入姓名",trigger:["blur","change"]}],role:[{required:!0,message:"请选择角色",trigger:["blur","change"]}],type:[{type:"array",required:!0,message:"请选择环境",trigger:["blur","change"]}],group:[{required:!0,message:"请选择分组",trigger:["blur","change"]}]},showRight:!1,selUser:{id:""},curUserInfo:{id:"",name:"",username:""},userGroup:[],editUserInfo:{},addGrouform:{},groupList:[],ipType:[],typeEnv:["测试环境","预发布环境","线上环境","开发环境"],staffKey:"",searchList:[],userNotEnv:[]}},created:function(){this.getStaffList()},methods:{searchStaff:function(){console.log(t);var t=this.staffKey,e=this.searchList.filter((function(e){return null!==e.name&&null!==e.username?-1!==e.name.indexOf(t)||-1!==e.username.indexOf(t):null!==e.name?(console.log(2),-1!==e.name.indexOf(t)):(console.log(3),-1!==e.username.indexOf(t))}));this.staffList=e,console.log(e)},handleDeleteGroup:function(t){var e=this;console.log(t),this.$confirm("此操作将删除该分组, 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then((function(){Object(n["j"])({uid:e.curUserInfo.id,group_id:t.group_id}).then((function(r){200===r.statusCode?(e.userGroup.splice(e.userGroup.indexOf(t),1),e.$message({type:"success",message:"删除成功!"})):e.$message.error(r.msg)}))})).catch((function(){e.$message({type:"info",message:"已取消删除"})}))},handleEditEnv:function(){var t=this;this.editEnvVisible=!0,Object(n["u"])({uid:this.editUserInfo.id}).then((function(e){200===e.statusCode&&(t.userNotEnv=e.data[0].ip_type,t.form.type="")}))},delUserEnv:function(t){var e=this;console.log(t),this.$confirm("此操作将删除该环境, 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then((function(){Object(n["i"])({uid:e.editUserInfo.id,ip_type:t}).then((function(r){e.ipType.splice(e.ipType.indexOf(t),1),200===r.statusCode?e.$message({type:"success",message:"删除成功!"}):e.$message.error(r.msg)}))})).catch((function(){e.$message({type:"info",message:"已取消删除"})}))},handleAddGroup:function(){var t=this;this.addGroupVisible=!0,Object(n["r"])(this.curUserInfo.id).then((function(e){console.log(e),200===e.statusCode&&(t.groupList=e.data)}))},handleEditMsg:function(){this.msgVisible=!0},handleCreatStaff:function(){this.visible=!0},handleDeleteStaff:function(t){var e=this;console.log(t),this.$confirm("此操作将删除该员工, 是否继续?","提示",{confirmButtonText:"确定",cancelButtonText:"取消",type:"warning"}).then((function(){Object(n["h"])(t.id).then((function(t){200===t.statusCode?(e.$message({message:t.msg,type:"success"}),e.getStaffList()):e.$message.error(t.msg)}))})).catch((function(){e.$message({type:"info",message:"已取消删除"})}))},getStaffList:function(){var t=this;Object(n["q"])().then((function(e){if(console.log(e),200===e.statusCode){var r=JSON.stringify(e.data);t.staffList=JSON.parse(r),t.searchList=JSON.parse(r),t.searchStaff()}}))},cancleAdddStaff:function(){this.visible=!1,this.$refs.addStaffEl.resetFields()},addStaffConfim:function(){var t=this;console.log("add"),this.$refs.addStaffEl.validate((function(e){e&&Object(n["b"])({name:t.addStaffForm.name,username:t.addStaffForm.username,role:t.addStaffForm.role}).then((function(e){console.log(e),200===e.statusCode?(t.visible=!1,t.staffKey="",t.getStaffList(),t.$refs.addStaffEl.resetFields(),t.$message({message:e.msg,type:"success"})):t.$message.error(e.msg)}))}))},showUserInfo:function(t){var e=this;this.showRight=!0,this.selUser=t,Object(n["s"])(t.id).then((function(t){if(200===t.statusCode){var r=JSON.stringify(t.data[0]);e.curUserInfo=JSON.parse(r),e.editUserInfo=JSON.parse(r),e.ipType=t.data[0].ip_type,e.form.type=t.data[0].ip_type}})),Object(n["t"])(t.id).then((function(t){200===t.statusCode&&(e.userGroup=t.data)}))},cancleEditUserInfo:function(){var t=JSON.stringify(this.curUserInfo);this.editUserInfo=JSON.parse(t),this.msgVisible=!1},editUserInfoConfirm:function(){var t=this;this.$refs.editUserInfoEl.validate((function(e){e&&Object(n["l"])({uid:t.editUserInfo.id,name:t.editUserInfo.name,role:t.editUserInfo.role,type:1}).then(function(){var e=Object(a["a"])(regeneratorRuntime.mark((function e(r){return regeneratorRuntime.wrap((function(e){while(1)switch(e.prev=e.next){case 0:if(200!==r.statusCode){e.next=9;break}return Object(n["s"])(t.editUserInfo.id).then((function(e){200===e.statusCode&&(t.curUserInfo=e.data[0],t.editUserInfo=e.data[0])})),console.log(221),t.msgVisible=!1,e.next=6,t.getStaffList();case 6:t.$message({message:r.msg,type:"success"}),e.next=10;break;case 9:t.$message.error(r.msg);case 10:case"end":return e.stop()}}),e)})));return function(t){return e.apply(this,arguments)}}())}))},cancleAddGroup:function(){this.$refs.addGrouformEl.resetFields(),this.addGroupVisible=!1},addGroup:function(){var t=this;Object(n["d"])({uid:this.curUserInfo.id,group_id:this.addGrouform.group}).then((function(e){200===e.statusCode?(t.addGrouform.group="",t.addGroupVisible=!1,t.getStaffList(),Object(n["t"])(t.editUserInfo.id).then((function(e){200===e.statusCode&&(t.userGroup=e.data)})),t.$message({message:e.msg,type:"success"})):t.$message.error(e.msg)}))},cancleIpTypes:function(){var t=this.ipType.join(",");this.form.type=t.split(","),this.editEnvVisible=!1},editIpTypes:function(){var t=this;Object(n["c"])({uid:this.editUserInfo.id,ip_type:this.form.type}).then((function(e){200===e.statusCode?(t.editEnvVisible=!1,t.ipType.push(t.form.type),t.form.type="",t.$message({message:e.msg,type:"success"})):t.$message.error(e.msg)}))}}},u=s,l=(r("4232"),r("2877")),d=Object(l["a"])(u,i,o,!1,null,"5a9a58e8",null);e["default"]=d.exports},4232:function(t,e,r){"use strict";var i=r("a4f0"),o=r.n(i);o.a},a4f0:function(t,e,r){}}]);