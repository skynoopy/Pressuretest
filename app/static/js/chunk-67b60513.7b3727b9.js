(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-67b60513"],{"0be0":function(t,e,n){"use strict";n.r(e);var i=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",{attrs:{id:"ipManagement"}},[n("el-tabs",{staticClass:"tab",attrs:{type:"card"},on:{"tab-click":t.handleClick},model:{value:t.activeName,callback:function(e){t.activeName=e},expression:"activeName"}},t._l(t.menulist,(function(e){return n("el-tab-pane",{key:e.label,attrs:{label:e.label,name:e.name}},[n("iplist",{attrs:{currentlabel:t.currentlabel,tableData:t.tableData,environmentallist:t.environmentallist,typeIndex:t.typeIndex},on:{refresh:function(e){return t.getEnvIpInfoFn(t.typeIndex)}}})],1)})),1),t._v(" "),n("el-button",{staticClass:"addip",attrs:{type:"primary"},on:{click:function(e){t.$refs.addip.dialogFormVisible=!0}}},[t._v("添加IP")]),t._v(" "),n("addip",{ref:"addip",attrs:{typeIndex:t.typeIndex},on:{refresh:function(e){return t.getEnvIpInfoFn(t.typeIndex)}}})],1)},r=[],a=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",{attrs:{id:"addip"}},[n("el-dialog",{attrs:{title:"添加IP",visible:t.dialogFormVisible},on:{"update:visible":function(e){t.dialogFormVisible=e}}},[n("el-form",{attrs:{model:t.form}},[n("el-form-item",{attrs:{label:"环境","label-width":"80"}},[n("el-select",{attrs:{placeholder:"请选择环境"},model:{value:t.form.ip_type,callback:function(e){t.$set(t.form,"ip_type",e)},expression:"form.ip_type"}},[n("el-option",{attrs:{label:"测试环境",value:"0"}}),t._v(" "),n("el-option",{attrs:{label:"预发布环境",value:"1"}}),t._v(" "),n("el-option",{attrs:{label:"线上环境",value:"2"}}),t._v(" "),n("el-option",{attrs:{label:"开发环境",value:"3"}})],1)],1),t._v(" "),n("el-form-item",{attrs:{label:"IP地址","label-width":"80"}},[n("el-input",{staticClass:"ip",attrs:{autocomplete:"off"},model:{value:t.form.ip_name,callback:function(e){t.$set(t.form,"ip_name",e)},expression:"form.ip_name"}})],1)],1),t._v(" "),n("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[n("el-button",{on:{click:function(e){t.dialogFormVisible=!1}}},[t._v("取 消")]),t._v(" "),n("el-button",{attrs:{type:"primary"},on:{click:t.addipok}},[t._v("确 定")])],1)],1)],1)},o=[],u=n("337a");function l(t){return Object(u["a"])({url:"/AuthorityApi/envip",method:"post",data:t})}function s(t){return Object(u["a"])({url:"/AuthorityApi/envip",method:"put",data:t})}function d(t){return Object(u["a"])({url:"/AuthorityApi/envip",method:"DELETE",data:{ip_id:t}})}function c(t){return Object(u["a"])({url:"/AuthorityApi/userenv",method:"DELETE",data:t})}var p={data:function(){return{dialogFormVisible:!1,form:{ip_name:"",ip_type:""}}},methods:{addipok:function(){var t=this;l(this.form).then((function(e){if(200!==e.statusCode)return t.$message.warning(e.msg);t.dialogFormVisible=!1,t.$emit("refresh",t.form.ip_type),t.$message.success(e.msg),t.form.ip_type="",t.form.ip_name="",console.log(e)}))}}},f=p,m=(n("4df1"),n("2877")),b=Object(m["a"])(f,a,o,!1,null,"3f2f798b",null),h=b.exports,v=function(){var t=this,e=t.$createElement,n=t._self._c||e;return n("div",{attrs:{id:"iplist"}},[n("el-row",[n("el-col",{attrs:{span:12}},[n("div",[n("el-table",{staticStyle:{width:"90%"},attrs:{data:t.tableData}},[n("el-table-column",{attrs:{label:"ID",width:"80"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("span",{staticStyle:{"margin-left":"0px"}},[t._v(t._s(e.row.id))])]}}])}),t._v(" "),n("el-table-column",{attrs:{label:"IP",width:"280"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-tag",{attrs:{size:"medium"}},[t._v(t._s(e.row.ip_name))])]}}])}),t._v(" "),n("el-table-column",{attrs:{label:"操作"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-button",{attrs:{size:"mini"},on:{click:function(n){return t.handleEdit(e.row)}}},[t._v("编辑")]),t._v(" "),n("el-button",{attrs:{size:"mini",type:"danger"},on:{click:function(n){return t.handleDelete(e.$index,e.row)}}},[t._v("删除")])]}}])})],1)],1)]),t._v(" "),n("el-col",{attrs:{span:12}},[n("div",[n("el-table",{staticStyle:{width:"90%"},attrs:{data:t.environmentallist}},[n("el-table-column",{attrs:{label:"ID",width:"80"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("span",{staticStyle:{"margin-left":"0px"}},[t._v(t._s(e.row.id))])]}}])}),t._v(" "),n("el-table-column",{attrs:{label:"name",width:"80"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-tag",{attrs:{size:"medium"}},[t._v(t._s(e.row.name))])]}}])}),t._v(" "),n("el-table-column",{attrs:{label:"UID",width:"80"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-tag",{attrs:{size:"medium"}},[t._v(t._s(e.row.uid))])]}}])}),t._v(" "),n("el-table-column",{attrs:{label:"username",width:"200"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-tag",{attrs:{size:"medium"}},[t._v(t._s(e.row.username))])]}}])}),t._v(" "),n("el-table-column",{attrs:{label:"操作"},scopedSlots:t._u([{key:"default",fn:function(e){return[n("el-button",{attrs:{size:"mini",type:"danger"},on:{click:function(n){return t.handleDeleteperson(e.$index,e.row)}}},[t._v("删除")])]}}])})],1)],1)])],1),t._v(" "),n("el-dialog",{staticClass:"edidialog",attrs:{title:"编辑IP",visible:t.isedidialog},on:{"update:visible":function(e){t.isedidialog=e}}},[n("el-form",{attrs:{model:t.form}},[n("el-form-item",{attrs:{label:"所在环境","label-width":"100px"}},[n("el-select",{attrs:{clearable:"",placeholder:"请选择"},model:{value:t.selectdefault,callback:function(e){t.selectdefault=e},expression:"selectdefault"}},[n("el-option",{attrs:{label:"测试环境",value:"0"}}),t._v(" "),n("el-option",{attrs:{label:"预发布环境",value:"1"}}),t._v(" "),n("el-option",{attrs:{label:"线上环境",value:"2"}}),t._v(" "),n("el-option",{attrs:{label:"开发环境",value:"3"}})],1)],1),t._v(" "),n("el-form-item",{attrs:{label:"IP地址","label-width":"100px"}},[n("el-input",{staticClass:"ediinput",attrs:{autocomplete:"off"},model:{value:t.form.ip_name,callback:function(e){t.$set(t.form,"ip_name",e)},expression:"form.ip_name"}})],1)],1),t._v(" "),n("div",{staticClass:"dialog-footer",attrs:{slot:"footer"},slot:"footer"},[n("el-button",{on:{click:function(e){t.isedidialog=!1}}},[t._v("取 消")]),t._v(" "),n("el-button",{attrs:{type:"primary"},on:{click:t.ediipok}},[t._v("确 定")])],1)],1)],1)},_=[],g={props:{tableData:{default:[]},environmentallist:{default:[]},typeIndex:{default:""},currentlabel:""},data:function(){return{isedidialog:!1,selectdefault:"测试环境",form:{ip_name:"",ip_type:0}}},created:function(){},methods:{handleEdit:function(t){console.log(this.currentlabel),this.isedidialog=!0,this.form.ip_name=t.ip_name,console.log(this.currentlabel),""!==this.currentlabel&&(this.selectdefault=this.currentlabel,this.form.ip_type=this.typeIndex),this.form.ip_id=t.id,console.log(this.form)},ediipok:function(){var t=this;s(this.form).then((function(e){if(200!==e.statusCode)return t.$message.warning("编辑失败");t.isedidialog=!1,t.$emit("refresh",t.form.ip_type)}))},handleDelete:function(t,e){var n=this;this.$alert("您是否要删除？","删除IP",{confirmButtonText:"确定",callback:function(t){console.log(t,"这个是cb"),"confirm"===t?d(e.id).then((function(t){if(200==t.statusCode){var e=n.typeIndex;n.$emit("refresh",e)}})):n.$message.warning("删除已取消")}}),console.log(t,e)},handleDeleteperson:function(t,e){var n=this;this.$alert("您是否要删除？","删除人员",{confirmButtonText:"确定",callback:function(t){"confirm"===t?c({uid:e.uid,ip_type:n.typeIndex}).then((function(t){if(200!==t.statusCode)return n.$message.warning("删除失败");if(200===t.statusCode){var e=n.typeIndex;n.$emit("refresh",e)}})):n.$message.warning("删除已取消")}})}}},y=g,A=(n("9951"),Object(m["a"])(y,v,_,!1,null,"7b787fb4",null)),k=A.exports,j=n("1472"),O={components:{iplist:k,addip:h},data:function(){return{activeName:0,tableData:[],environmentallist:[],index:"",typeIndex:0,currentlabel:"",menulist:[{label:"测试环境",name:"0"},{label:"预发布环境",name:"1"},{label:"线上环境",name:"2"},{label:"开发环境",name:"3"}]}},created:function(){this.getEnvIpInfoFn(0)},methods:{handleClick:function(t){this.typeIndex=t.index,this.currentlabel=t.label,this.getEnvIpInfoFn(t.index)},getEnvIpInfoFn:function(t){var e=this;console.log(this.typeIndex,"当前index"),Object(j["m"])(t).then((function(t){e.tableData=t.data.ip_list,console.log(e.tableData),e.environmentallist=t.data.pers_list}))}}},x=O,I=(n("11e2"),Object(m["a"])(x,i,r,!1,null,"393c0cc7",null));e["default"]=I.exports},"11e2":function(t,e,n){"use strict";var i=n("4e07"),r=n.n(i);r.a},1472:function(t,e,n){"use strict";n.d(e,"f",(function(){return r})),n.d(e,"n",(function(){return a})),n.d(e,"p",(function(){return o})),n.d(e,"k",(function(){return u})),n.d(e,"o",(function(){return l})),n.d(e,"v",(function(){return s})),n.d(e,"e",(function(){return d})),n.d(e,"a",(function(){return c})),n.d(e,"g",(function(){return p})),n.d(e,"q",(function(){return f})),n.d(e,"b",(function(){return m})),n.d(e,"h",(function(){return b})),n.d(e,"s",(function(){return h})),n.d(e,"t",(function(){return v})),n.d(e,"l",(function(){return _})),n.d(e,"r",(function(){return g})),n.d(e,"d",(function(){return y})),n.d(e,"j",(function(){return A})),n.d(e,"u",(function(){return k})),n.d(e,"c",(function(){return j})),n.d(e,"i",(function(){return O})),n.d(e,"m",(function(){return x}));n("7f7f");var i=n("337a");function r(t){var e=t.group_name,n=t.project_id;return Object(i["a"])({url:"/AuthorityApi/group",method:"post",data:{group_name:e,project_id:n}})}function a(){return Object(i["a"])({url:"/AuthorityApi/group",method:"get"})}function o(){return Object(i["a"])({url:"/AuthorityApi/project",method:"get"})}function u(t){var e=t.group_id,n=t.group_name,r=t.project_id;return Object(i["a"])({url:"/AuthorityApi/group",method:"PUT",data:{group_id:e,group_name:n,project_id:r}})}function l(t){return Object(i["a"])({url:"/AuthorityApi/groupuser",method:"get",params:{group_id:t}})}function s(t){var e=t.username,n=void 0===e?"":e;return Object(i["a"])({url:"/AuthorityApi/groupuseradd",method:"post",data:{username:n}})}function d(t){var e=t.group_id,n=t.uid,r=t.type,a=void 0===r?1:r;return Object(i["a"])({url:"/AuthorityApi/checkgroupuser",method:"post",data:{group_id:e,uid:n,type:a}})}function c(t){var e=t.group_id,n=t.uid;return Object(i["a"])({url:"/AuthorityApi/groupuser",method:"POST",data:{group_id:e,uid:n}})}function p(t){var e=t.group_id,n=t.uid;return Object(i["a"])({url:"/AuthorityApi/groupuser",method:"DELETE",data:{group_id:e,uid:n}})}function f(){return Object(i["a"])({url:"/AuthorityApi/user",method:"get"})}function m(t){var e=t.name,n=t.username,r=t.role,a=t.ip_type;return Object(i["a"])({url:"/AuthorityApi/user",method:"POST",data:{name:e,username:n,role:r,ip_type:a}})}function b(t){return Object(i["a"])({url:"/AuthorityApi/user",method:"DELETE",data:{uid:t}})}function h(t){return Object(i["a"])({url:"/AuthorityApi/userinfo",method:"get",params:{uid:t}})}function v(t){return Object(i["a"])({url:"/AuthorityApi/usergroup",method:"get",params:{uid:t}})}function _(t){var e=t.uid,n=t.name,r=t.role,a=t.type;return Object(i["a"])({url:"/AuthorityApi/user",method:"put",data:{uid:e,name:n,role:r,type:a}})}function g(t){return Object(i["a"])({url:"/AuthorityApi/usergroupadd",method:"POST",data:{uid:t}})}function y(t){var e=t.uid,n=t.group_id;return Object(i["a"])({url:"/AuthorityApi/usergroup",method:"POST",data:{uid:e,group_id:n}})}function A(t){var e=t.uid,n=t.group_id;return Object(i["a"])({url:"/AuthorityApi/usergroup",method:"DELETE",data:{uid:e,group_id:n}})}function k(t){var e=t.uid;return Object(i["a"])({url:"/AuthorityApi/checkuserenv",method:"post",data:{uid:e}})}function j(t){var e=t.uid,n=t.ip_type;return Object(i["a"])({url:"/AuthorityApi/userenv",method:"post",data:{uid:e,ip_type:n}})}function O(t){var e=t.uid,n=t.ip_type;return Object(i["a"])({url:"/AuthorityApi/userenv",method:"DELETE",data:{uid:e,ip_type:n}})}function x(t){return Object(i["a"])({url:"/AuthorityApi/envipinfo",method:"POST",data:{ip_type:t}})}},"4df1":function(t,e,n){"use strict";var i=n("7088"),r=n.n(i);r.a},"4e07":function(t,e,n){},7088:function(t,e,n){},9951:function(t,e,n){"use strict";var i=n("c4b8"),r=n.n(i);r.a},c4b8:function(t,e,n){}}]);