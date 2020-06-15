(window["webpackJsonp"]=window["webpackJsonp"]||[]).push([["chunk-21439fa6"],{2017:function(t,n,e){"use strict";var s=e("b12d"),o=e.n(s);o.a},5310:function(t,n,e){},5379:function(t,n,e){"use strict";var s=e("5310"),o=e.n(s);o.a},9067:function(t,n,e){},"9ed6":function(t,n,e){"use strict";e.r(n);var s=function(){var t=this,n=t.$createElement,e=t._self._c||n;return e("div",{staticClass:"login-container"},[e("el-form",{ref:"loginForm",staticClass:"login-form",attrs:{model:t.loginForm,rules:t.loginRules,autocomplete:"on","label-position":"left"}},[e("div",{staticClass:"title-container"},[e("h3",{staticClass:"title"},[t._v("登录")])]),t._v(" "),e("el-form-item",{attrs:{prop:"username"}},[e("span",{staticClass:"svg-container"},[e("svg-icon",{attrs:{"icon-class":"user"}})],1),t._v(" "),e("el-input",{ref:"username",attrs:{placeholder:"请输入用户名",name:"username",type:"text",tabindex:"1",autocomplete:"on"},model:{value:t.loginForm.username,callback:function(n){t.$set(t.loginForm,"username",n)},expression:"loginForm.username"}})],1),t._v(" "),e("el-tooltip",{attrs:{content:"Caps lock is On",placement:"right",manual:""},model:{value:t.capsTooltip,callback:function(n){t.capsTooltip=n},expression:"capsTooltip"}},[e("el-form-item",{attrs:{prop:"password"}},[e("span",{staticClass:"svg-container"},[e("svg-icon",{attrs:{"icon-class":"password"}})],1),t._v(" "),e("el-input",{key:t.passwordType,ref:"password",attrs:{type:t.passwordType,placeholder:"请输入密码",name:"password",tabindex:"2",autocomplete:"on"},on:{blur:function(n){t.capsTooltip=!1}},nativeOn:{keyup:[function(n){return t.checkCapslock(n)},function(n){return!n.type.indexOf("key")&&t._k(n.keyCode,"enter",13,n.key,"Enter")?null:t.handleLogin(n)}]},model:{value:t.loginForm.password,callback:function(n){t.$set(t.loginForm,"password",n)},expression:"loginForm.password"}}),t._v(" "),e("span",{staticClass:"show-pwd",on:{click:t.showPwd}},[e("svg-icon",{attrs:{"icon-class":"password"===t.passwordType?"eye":"eye-open"}})],1)],1)],1),t._v(" "),e("el-button",{staticStyle:{width:"100%","margin-bottom":"30px"},attrs:{loading:t.loading,type:"primary"},nativeOn:{click:function(n){return n.preventDefault(),t.handleLogin(n)}}},[t._v("登陆")])],1),t._v(" "),e("el-dialog",{attrs:{title:"Or connect with",visible:t.showDialog},on:{"update:visible":function(n){t.showDialog=n}}},[t._v("\n      Can not be simulated on local, so please combine you own business simulation! ! !\n      "),e("br"),t._v(" "),e("br"),t._v(" "),e("br"),t._v(" "),e("social-sign")],1)],1)},o=[],i=(e("ac6a"),e("456d"),e("61f7")),a=function(){var t=this,n=t.$createElement,e=t._self._c||n;return e("div",{staticClass:"social-signup-container"},[e("div",{staticClass:"sign-btn",on:{click:function(n){return t.wechatHandleClick("wechat")}}},[e("span",{staticClass:"wx-svg-container"},[e("svg-icon",{staticClass:"icon",attrs:{"icon-class":"wechat"}})],1),t._v("\n    WeChat\n  ")]),t._v(" "),e("div",{staticClass:"sign-btn",on:{click:function(n){return t.tencentHandleClick("tencent")}}},[e("span",{staticClass:"qq-svg-container"},[e("svg-icon",{staticClass:"icon",attrs:{"icon-class":"qq"}})],1),t._v("\n    QQ\n  ")])])},r=[],c={name:"SocialSignin",methods:{wechatHandleClick:function(t){alert("ok")},tencentHandleClick:function(t){alert("ok")}}},l=c,u=(e("d9fb"),e("2877")),p=Object(u["a"])(l,a,r,!1,null,"7309fbbb",null),d=p.exports,f={name:"Login",components:{SocialSign:d},data:function(){var t=function(t,n,e){Object(i["d"])(n)?e():e(new Error("请输入正确的邮箱地址"))},n=function(t,n,e){n.length<6?e(new Error("密码不少于6个字符")):e()};return{loginForm:{username:"",password:""},loginRules:{username:[{required:!0,trigger:["blur","change"],validator:t}],password:[{required:!0,trigger:["blur","change"],validator:n}]},passwordType:"password",capsTooltip:!1,loading:!1,showDialog:!1,redirect:void 0,otherQuery:{}}},watch:{$route:{handler:function(t){var n=t.query;n&&(this.redirect=n.redirect,this.otherQuery=this.getOtherQuery(n))},immediate:!0}},created:function(){},mounted:function(){""===this.loginForm.username?this.$refs.username.focus():""===this.loginForm.password&&this.$refs.password.focus()},destroyed:function(){},methods:{handleToRegister:function(){this.$router.push("/register")},checkCapslock:function(t){var n=t.key;this.capsTooltip=n&&1===n.length&&n>="A"&&n<="Z"},showPwd:function(){var t=this;"password"===this.passwordType?this.passwordType="":this.passwordType="password",this.$nextTick((function(){t.$refs.password.focus()}))},handleLogin:function(){var t=this;this.$refs.loginForm.validate((function(n){if(!n)return console.log("error submit!!"),!1;t.loading=!0,t.$store.dispatch("user/login",t.loginForm).then((function(){t.$router.push({path:t.redirect||"/",query:t.otherQuery}),t.loading=!1})).catch((function(){t.loading=!1}))}))},getOtherQuery:function(t){return Object.keys(t).reduce((function(n,e){return"redirect"!==e&&(n[e]=t[e]),n}),{})}}},g=f,h=(e("2017"),e("5379"),Object(u["a"])(g,s,o,!1,null,"3b469ea0",null));n["default"]=h.exports},b12d:function(t,n,e){},d9fb:function(t,n,e){"use strict";var s=e("9067"),o=e.n(s);o.a}}]);