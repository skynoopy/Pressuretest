(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-8c970084"],{"015e":function(t,e,r){"use strict";r.d(e,"c",(function(){return s})),r.d(e,"d",(function(){return o})),r.d(e,"a",(function(){return a})),r.d(e,"h",(function(){return i})),r.d(e,"b",(function(){return c})),r.d(e,"g",(function(){return u})),r.d(e,"f",(function(){return p})),r.d(e,"e",(function(){return l}));var n=r("337a");function s(){return Object(n["a"])({url:"http://192.168.2.94:80/RestfulApi/Monitor",method:"get"})}function o(t){return Object(n["a"])({url:"http://192.168.2.94:80/account/checktree",method:"post",data:{uid:t}})}function a(t,e,r,s){return Object(n["a"])({url:"http://192.168.2.94:80/account/addtree",method:"post",data:{filename:t,pid:e,file_type:r,uid:s}})}function i(t,e,r,s,o,a,i,c){return Object(n["a"])({url:"http://192.168.2.94:80/account/updatatree",method:"put",data:{id:t,filename:e,file_type:r,meth:s,sc_ip:o,sc_path:a,sc_praameter:i,sc_name:c}})}function c(t){return Object(n["a"])({url:"http://192.168.2.94:80/account/deletetree",method:"DELETE",data:{id:t}})}function u(t,e,r){return Object(n["a"])({url:"http://192.168.2.94:80/RestfulApi/ScriptGeneration",method:"post",data:{hostip:t,hostpath:e,parameter:r}})}function p(t,e){return Object(n["a"])({url:"http://192.168.2.94:80/RestfulApi/Register",method:"post",data:{username:t,password:e}})}function l(t,e,r,s,o){return Object(n["a"])({url:"http://192.168.2.94:80/RestfulApi/Implement",method:"post",data:{Filename:t,Concurrent:e,Dx:r,Xz:s,Ip:o}})}},"182a":function(t,e,r){},4565:function(t,e,r){"use strict";var n=r("b195"),s=r.n(n);s.a},9202:function(t,e,r){"use strict";var n=r("182a"),s=r.n(n);s.a},b195:function(t,e,r){},d5c2:function(t,e,r){"use strict";r.r(e);var n=function(){var t=this,e=t.$createElement,r=t._self._c||e;return r("div",{staticClass:"login-container"},[r("el-form",{ref:"registerForm",staticClass:"login-form",attrs:{model:t.registerForm,rules:t.loginRules,autocomplete:"on","label-position":"left"}},[r("div",{staticClass:"title-container"},[r("h3",{staticClass:"title"},[t._v("注册")])]),t._v(" "),r("el-form-item",{attrs:{prop:"username"}},[r("span",{staticClass:"svg-container"},[r("svg-icon",{attrs:{"icon-class":"user"}})],1),t._v(" "),r("el-input",{ref:"username",attrs:{placeholder:"Username",name:"username",type:"text",tabindex:"1",autocomplete:"on"},model:{value:t.registerForm.username,callback:function(e){t.$set(t.registerForm,"username",e)},expression:"registerForm.username"}})],1),t._v(" "),r("el-tooltip",{attrs:{content:"Caps lock is On",placement:"right",manual:""},model:{value:t.capsTooltip,callback:function(e){t.capsTooltip=e},expression:"capsTooltip"}},[r("el-form-item",{attrs:{prop:"password"}},[r("span",{staticClass:"svg-container"},[r("svg-icon",{attrs:{"icon-class":"password"}})],1),t._v(" "),r("el-input",{key:t.passwordType,ref:"password",attrs:{type:t.passwordType,placeholder:"Password",name:"password",tabindex:"2",autocomplete:"on"},on:{blur:function(e){t.capsTooltip=!1}},nativeOn:{keyup:[function(e){return t.checkCapslock(e)},function(e){return!e.type.indexOf("key")&&t._k(e.keyCode,"enter",13,e.key,"Enter")?null:t.handleLogin(e)}]},model:{value:t.registerForm.password,callback:function(e){t.$set(t.registerForm,"password",e)},expression:"registerForm.password"}}),t._v(" "),r("span",{staticClass:"show-pwd",on:{click:t.showPwd}},[r("svg-icon",{attrs:{"icon-class":"password"===t.passwordType?"eye":"eye-open"}})],1)],1)],1),t._v(" "),r("el-button",{staticStyle:{width:"100%","margin-bottom":"30px"},attrs:{loading:t.loading,type:"primary"},nativeOn:{click:function(e){return e.preventDefault(),t.handleRegister(e)}}},[t._v("注册")]),t._v(" "),r("el-link",{staticStyle:{width:"100%","margin-bottom":"30px"},attrs:{loading:t.loading,underline:!1,type:"primary"},nativeOn:{click:function(e){return e.preventDefault(),t.handleToLogin(e)}}},[t._v("登录")])],1)],1)},s=[],o=r("61f7"),a=r("015e"),i={name:"Register",data:function(){var t=function(t,e,r){Object(o["d"])(e)?r():r(new Error("请输入正确的邮箱地址"))},e=function(t,e,r){e.length<6?r(new Error("密码不少于6个字符")):r()};return{registerForm:{username:"",password:""},loginRules:{username:[{required:!0,trigger:["blur","change"],validator:t}],password:[{required:!0,trigger:["blur","change"],validator:e}]},passwordType:"password",capsTooltip:!1,loading:!1,showDialog:!1,redirect:void 0,otherQuery:{}}},methods:{handleToLogin:function(){this.$router.push({path:"/login"})},checkCapslock:function(t){var e=t.key;this.capsTooltip=e&&1===e.length&&e>="A"&&e<="Z"},showPwd:function(){var t=this;"password"===this.passwordType?this.passwordType="":this.passwordType="password",this.$nextTick((function(){t.$refs.password.focus()}))},handleRegister:function(){var t=this;Object(a["f"])(this.registerForm.username,this.registerForm.password).then((function(e){console.log(e),200===e.code?(t.$message({message:"注册成功",type:"success"}),t.$router.push({path:"/login"})):t.$message({message:e.msg,type:"warning"})}))}}},c=i,u=(r("4565"),r("9202"),r("2877")),p=Object(u["a"])(c,n,s,!1,null,"668c4a4c",null);e["default"]=p.exports}}]);