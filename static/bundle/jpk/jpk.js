!function(n){var t={};function e(a){if(t[a])return t[a].exports;var o=t[a]={i:a,l:!1,exports:{}};return n[a].call(o.exports,o,o.exports,e),o.l=!0,o.exports}e.m=n,e.c=t,e.d=function(n,t,a){e.o(n,t)||Object.defineProperty(n,t,{enumerable:!0,get:a})},e.r=function(n){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(n,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(n,"__esModule",{value:!0})},e.t=function(n,t){if(1&t&&(n=e(n)),8&t)return n;if(4&t&&"object"==typeof n&&n&&n.__esModule)return n;var a=Object.create(null);if(e.r(a),Object.defineProperty(a,"default",{enumerable:!0,value:n}),2&t&&"string"!=typeof n)for(var o in n)e.d(a,o,function(t){return n[t]}.bind(null,o));return a},e.n=function(n){var t=n&&n.__esModule?function(){return n.default}:function(){return n};return e.d(t,"a",t),t},e.o=function(n,t){return Object.prototype.hasOwnProperty.call(n,t)},e.p="bundle/jpk/",e(e.s=5)}([function(n,t,e){var a=e(1);"string"==typeof a&&(a=[[n.i,a,""]]);var o={hmr:!0,transform:void 0,insertInto:void 0};e(3)(a,o);a.locals&&(n.exports=a.locals)},function(n,t,e){(n.exports=e(2)(!1)).push([n.i,"body {\n  min-height: 1000px;\n  padding-top: 70px;\n}\n\n\n.panel-jpk {\n\tdisplay: inline-block;\n\tvertical-align: top;\n\t\n\tpadding-left: 0;\n\tpadding-right: 0px;\n\twidth: 210px;\n\tmargin-right: 10px;\n}\n\n.glyphicon {\n\tcursor: pointer;\n\tmargin-left: 5px;\n}\n\n.navbar-right {\n\tmargin-right: 0px;\n}\n\n/*\n.jpk-icons, .paczka-icons {\n\tdisplay: none;\n}\n*/\n\n.jpk-heading .wybrany {\n\tborder-color: black;\n}\n\n.jpk-heading:hover .jpk-icons {\n\tdisplay:block;\n}\n\n.naglowek-paczki:hover .paczka-icons {\n\tdisplay: block;\n}\n \n.panel-jpk:hover {\n\tborder-color: #2893A9;\n}\n\n#rachunki, #magazyny, #sprawozdanie {\n  display: none;\n}\n\n.pliki-paczki {\n\tdisplay: none;\n}\n\nspan.tog {\n\tcursor: pointer;\n}\n\n.iko {\n\tmargin-left: 0;\n\tmargin-right: 5px;\n}\n\n.panel-upload td.etykieta {\n\twidth: 30%;\n}\n\n.panel-upload .panel-body {\n\tpadding: 0;\n}\n\n.panel-upload table {\n\tmargin-bottom: 0;\n}\n\ntable.dataTable thead th {\n\tpadding: 10px 10px;\n}\n\n/*\n#jpk_filter {\n\tfloat: left;\n\tposition: relative: \n\tleft: -5px;\n}\n#jpk_filter input {\n\tmargin-left: 0;\n}\n*/\n\n#jpk tr, #importy tr {\n\tcursor: pointer;\n}\n\n.jpk-details {\n\twidth: 150px;\n}\n\n.aaajpk-ctrl-table {\n\twidth: 50%;\n}\n\ntable.jpk-ctrl-table thead th, table.jpk-ctrl-table tbody td {\n\tpadding: 5px 10px;\n}\n\ntable.jpk-ctrl-table {\n\twidth: 400px;\n}\n\ntable.jpk-sf-table {\n\twidth: 450px;\n}\n\n.jpk-ctrl-table .r {\n\ttext-align: right;\n}\n\ntable {\n\tmargin-bottom: 10px;\n}\n\n.jpk-msg {\n\toverflow-wrap: break-word;\n}\n\ntd.hl_green {\n\tborder-left: 5px solid rgba(0, 255, 0, 0.5) !important;\n\tpadding-left: 5px !important;\n}\ntd.hl_red {\n\tborder-left: 5px solid rgba(255, 0, 0, 0.5) !important;\n\tpadding-left: 5px !important;\n}\n\ntd.hl_bledy {\n\tcolor: red;\n}\n\ntd.hl_warn {\n\tcolor: orange;\n}\n\nh3 {\n\tmargin-top: 0;\n\tmargin-bottom: 20px;\n}\n\n#upload-icon {\n\tmargin-left: 10px; \n\tposition: relative; \n\ttop: -3px;\n}\n\ntable.upo td.etykieta {\n    background-color: #e0e0e0;\n    border-bottom: 1px solid #c0c0c0;\n}\n\niframe {\n\twidth: 100%;\n\theight: 920px;\n}\n\n.alert {\n\tdisplay: none;\n\tmargin-bottom: 10px;\n\tposition: relative;\n\ttop: -5px;\n\tcursor: pointer;\n}\n\ndiv.pole label {\n\twidth: 100px;\n}\n\n#firmy tr {\n\tcursor: pointer;\n}\n\n#fakturyl tr {\n   cursor: pointer;\n   font-size: 12px;\n}\n\n#fakturyl td.ar, #importy td.ar {\n\ttext-align: right;\n}\n\n#fakturyl td span {\n\twhite-space: nowrap;\n}\n\ntable.isp {\n\twidth: 50%;\n\tfont-size: 10pt;\n}\n\ntable.isp td {\n\tborder: 1px solid #e0e0e0;\n\tpadding: 0px 5px;\n}\n\ntable.isp td.ar {\n\ttext-align: right;\n}\n\n.form-control[readonly] {\n    background-color: #f8f8f8;\n    opacity: 1;\n}\n\nli.danger {\n  background-color: #f2dede; \n}\n",""])},function(n,t,e){"use strict";n.exports=function(n){var t=[];return t.toString=function(){return this.map(function(t){var e=function(n,t){var e=n[1]||"",a=n[3];if(!a)return e;if(t&&"function"==typeof btoa){var o=(i=a,"/*# sourceMappingURL=data:application/json;charset=utf-8;base64,"+btoa(unescape(encodeURIComponent(JSON.stringify(i))))+" */"),r=a.sources.map(function(n){return"/*# sourceURL="+a.sourceRoot+n+" */"});return[e].concat(r).concat([o]).join("\n")}var i;return[e].join("\n")}(t,n);return t[2]?"@media "+t[2]+"{"+e+"}":e}).join("")},t.i=function(n,e){"string"==typeof n&&(n=[[null,n,""]]);for(var a={},o=0;o<this.length;o++){var r=this[o][0];null!=r&&(a[r]=!0)}for(o=0;o<n.length;o++){var i=n[o];null!=i[0]&&a[i[0]]||(e&&!i[2]?i[2]=e:e&&(i[2]="("+i[2]+") and ("+e+")"),t.push(i))}},t}},function(n,t,e){var a,o,r={},i=(a=function(){return window&&document&&document.all&&!window.atob},function(){return void 0===o&&(o=a.apply(this,arguments)),o}),l=function(n){var t={};return function(n,e){if("function"==typeof n)return n();if(void 0===t[n]){var a=function(n,t){return t?t.querySelector(n):document.querySelector(n)}.call(this,n,e);if(window.HTMLIFrameElement&&a instanceof window.HTMLIFrameElement)try{a=a.contentDocument.head}catch(n){a=null}t[n]=a}return t[n]}}(),s=null,d=0,c=[],u=e(4);function p(n,t){for(var e=0;e<n.length;e++){var a=n[e],o=r[a.id];if(o){o.refs++;for(var i=0;i<o.parts.length;i++)o.parts[i](a.parts[i]);for(;i<a.parts.length;i++)o.parts.push(b(a.parts[i],t))}else{var l=[];for(i=0;i<a.parts.length;i++)l.push(b(a.parts[i],t));r[a.id]={id:a.id,refs:1,parts:l}}}}function f(n,t){for(var e=[],a={},o=0;o<n.length;o++){var r=n[o],i=t.base?r[0]+t.base:r[0],l={css:r[1],media:r[2],sourceMap:r[3]};a[i]?a[i].parts.push(l):e.push(a[i]={id:i,parts:[l]})}return e}function h(n,t){var e=l(n.insertInto);if(!e)throw new Error("Couldn't find a style target. This probably means that the value for the 'insertInto' parameter is invalid.");var a=c[c.length-1];if("top"===n.insertAt)a?a.nextSibling?e.insertBefore(t,a.nextSibling):e.appendChild(t):e.insertBefore(t,e.firstChild),c.push(t);else if("bottom"===n.insertAt)e.appendChild(t);else{if("object"!=typeof n.insertAt||!n.insertAt.before)throw new Error("[Style Loader]\n\n Invalid value for parameter 'insertAt' ('options.insertAt') found.\n Must be 'top', 'bottom', or Object.\n (https://github.com/webpack-contrib/style-loader#insertat)\n");var o=l(n.insertAt.before,e);e.insertBefore(t,o)}}function m(n){if(null===n.parentNode)return!1;n.parentNode.removeChild(n);var t=c.indexOf(n);t>=0&&c.splice(t,1)}function g(n){var t=document.createElement("style");if(void 0===n.attrs.type&&(n.attrs.type="text/css"),void 0===n.attrs.nonce){var a=function(){0;return e.nc}();a&&(n.attrs.nonce=a)}return v(t,n.attrs),h(n,t),t}function v(n,t){Object.keys(t).forEach(function(e){n.setAttribute(e,t[e])})}function b(n,t){var e,a,o,r;if(t.transform&&n.css){if(!(r="function"==typeof t.transform?t.transform(n.css):t.transform.default(n.css)))return function(){};n.css=r}if(t.singleton){var i=d++;e=s||(s=g(t)),a=y.bind(null,e,i,!1),o=y.bind(null,e,i,!0)}else n.sourceMap&&"function"==typeof URL&&"function"==typeof URL.createObjectURL&&"function"==typeof URL.revokeObjectURL&&"function"==typeof Blob&&"function"==typeof btoa?(e=function(n){var t=document.createElement("link");return void 0===n.attrs.type&&(n.attrs.type="text/css"),n.attrs.rel="stylesheet",v(t,n.attrs),h(n,t),t}(t),a=function(n,t,e){var a=e.css,o=e.sourceMap,r=void 0===t.convertToAbsoluteUrls&&o;(t.convertToAbsoluteUrls||r)&&(a=u(a));o&&(a+="\n/*# sourceMappingURL=data:application/json;base64,"+btoa(unescape(encodeURIComponent(JSON.stringify(o))))+" */");var i=new Blob([a],{type:"text/css"}),l=n.href;n.href=URL.createObjectURL(i),l&&URL.revokeObjectURL(l)}.bind(null,e,t),o=function(){m(e),e.href&&URL.revokeObjectURL(e.href)}):(e=g(t),a=function(n,t){var e=t.css,a=t.media;a&&n.setAttribute("media",a);if(n.styleSheet)n.styleSheet.cssText=e;else{for(;n.firstChild;)n.removeChild(n.firstChild);n.appendChild(document.createTextNode(e))}}.bind(null,e),o=function(){m(e)});return a(n),function(t){if(t){if(t.css===n.css&&t.media===n.media&&t.sourceMap===n.sourceMap)return;a(n=t)}else o()}}n.exports=function(n,t){if("undefined"!=typeof DEBUG&&DEBUG&&"object"!=typeof document)throw new Error("The style-loader cannot be used in a non-browser environment");(t=t||{}).attrs="object"==typeof t.attrs?t.attrs:{},t.singleton||"boolean"==typeof t.singleton||(t.singleton=i()),t.insertInto||(t.insertInto="head"),t.insertAt||(t.insertAt="bottom");var e=f(n,t);return p(e,t),function(n){for(var a=[],o=0;o<e.length;o++){var i=e[o];(l=r[i.id]).refs--,a.push(l)}n&&p(f(n,t),t);for(o=0;o<a.length;o++){var l;if(0===(l=a[o]).refs){for(var s=0;s<l.parts.length;s++)l.parts[s]();delete r[l.id]}}}};var w,k=(w=[],function(n,t){return w[n]=t,w.filter(Boolean).join("\n")});function y(n,t,e,a){var o=e?"":a.css;if(n.styleSheet)n.styleSheet.cssText=k(t,o);else{var r=document.createTextNode(o),i=n.childNodes;i[t]&&n.removeChild(i[t]),i.length?n.insertBefore(r,i[t]):n.appendChild(r)}}},function(n,t){n.exports=function(n){var t="undefined"!=typeof window&&window.location;if(!t)throw new Error("fixUrls requires window.location");if(!n||"string"!=typeof n)return n;var e=t.protocol+"//"+t.host,a=e+t.pathname.replace(/\/[^\/]*$/,"/");return n.replace(/url\s*\(((?:[^)(]|\((?:[^)(]+|\([^)(]*\))*\))*)\)/gi,function(n,t){var o,r=t.trim().replace(/^"(.*)"$/,function(n,t){return t}).replace(/^'(.*)'$/,function(n,t){return t});return/^(#|data:|http:\/\/|https:\/\/|file:\/\/\/|\s*$)/i.test(r)?n:(o=0===r.indexOf("//")?r:0===r.indexOf("/")?e+r:a+r.replace(/^\.\//,""),"url("+JSON.stringify(o)+")")})}},function(n,t,e){"use strict";function a(n){$.ajax({dataType:"html",url:"/jpk/"+n.data().numer+"/rozwin/",success:function(t){n.child(t).show(),$(n).addClass("shown")}})}function o(n,t){var e=$(n).closest("tr"),a=table.row(e),o=a.data();a.child.isShown()?(a.child.hide(),e.removeClass("shown"),$.ajax({dataType:"json",url:"/jpk/"+(t||o.numer)+"/zwin/",success:function(n){a.child(n).show(),e.addClass("shown")}})):$.ajax({dataType:"html",url:"/jpk/"+(t||o.numer)+"/rozwin/",success:function(n){a.child(n).show(),e.addClass("shown")}})}e.r(t);var r=null,i=[];function l(n){var t=Math.round((new Date-i[n].browser)/1e3),e=i[n].serwer.split(":");e[0]=parseInt(e[0]),e[1]=parseInt(e[1]),e[2]=parseInt(e[2]),e[2]=e[2]+t,e[2]>=60&&(e[2]=e[2]-60,e[1]=e[1]+1,e[1]>=60&&(e[1]=e[1]-60,e[0]=e[0]+1));var a=e[0]+":"+c(e[1])+":"+c(e[2]),o=table.row(i[n].id).data().stan.match(/([A-Z ]+)/);table.row(i[n].id).data().stan=o[1].trim()+'<br/><span class="small">'+a+"</span>",table.row(i[n].id).invalidate()}function s(){if(i.length>0){for(var n=0;n<i.length;n++)l(n);r=setTimeout(s,500)}else clearTimeout(r)}function d(n,t,e){for(var a=0;a<i.length;a++)if(i[a].id==n)return i[a].serwer=e,void(i[a].browser=new Date);e&&(i.push({id:n,jpk_id:t,serwer:e,browser:new Date}),r&&clearTimeout(r),s())}function c(n){return n<10?"0"+n:n}function u(){var n=$.map(i,function(n,t){return n.jpk_id});n.length>0&&($.ajax({dataType:"json",url:"/jpk/"+n+"/task/",success:function(n){$.each(n,function(n,t){var e=function(n){for(var t=0;t<i.length;t++)if(i[t].jpk_id==n)return i[t].id}(n),o=table.row(e);"W KOLEJCE"!=t.stan&&"TWORZENIE"!=t.stan?(!function(n){for(var t=0;t<i.length;t++)i[t].jpk_id==n&&i.splice(t,1)}(n),o.data().stan=t.stan,a(o)):(d(e,n,t.czas),o.data().stan=t.stan+'<br/><span class="small">'+t.czas+"</span>"),o.invalidate()})},timeout:2e3}),setTimeout(u,3e3))}var p={jpk:["table",function(){return $("#jpk").on("init.dt",function(){u(),tr_id&&o($("tr#tr_"+tr_id)[0],tr_id)}).DataTable({language:{url:"/static/DataTables/Polish.json"},ajax:"/ajax"+window.location.pathname+"jpk/lista/",columns:[{data:"numer"},{data:"utworzony"},{data:"kod"},{data:"dataod"},{data:"datado"},{data:"opis"},{data:"stan"}],columnDefs:[{width:"25%",targets:5}],info:!1,stateSave:!0,lengthMenu:[10,15,20,100],pageLength:15,createdRow:function(n,t,e){"W KOLEJCE"!=t.stan&&"TWORZENIE"!=t.stan||d(e,t.numer,t.czas),$(n).attr("id","tr_"+t.numer),"DOSTARCZONY"==t.stan&&$("td",n).eq(6).addClass("hl_green"),"NIE WYSŁANY"!=t.stan&&"NIE PRZYJĘTY"!=t.stan&&"BŁĄD WYSYŁKI"!=t.stan||$("td",n).eq(6).addClass("hl_red"),console.log(t.numer,t.bledy),"error"==t.bledy&&$("td",n).eq(6).addClass("hl_bledy"),"warn"==t.bledy&&$("td",n).eq(6).addClass("hl_warn")},order:[[0,"desc"]]})}],firmy:["firmy",function(){return $("#firmy").DataTable({language:{url:"/static/DataTables/Polish.json"},ajax:"/ajax/firmy/",columns:[{data:"oznaczenie"},{data:"nazwa"},{data:"kod"},{data:"okres"},{data:"opis"},{data:"stan"}],columnDefs:[{width:"5%",targets:0}],info:!1,stateSave:!0,lengthMenu:[10,15,20,100],pageLength:20,order:[[0,"asc"]]})}],fakturyl:["faktury",function(){return $("#fakturyl").DataTable({language:{url:"/static/DataTables/Polish.json"},ajax:"/bra/ajax/faktury/",columns:[{data:"faktura"},{data:"daty"},{data:"nip"},{data:"nazwa"},{data:"adres"},{data:"sprzedaz23"},{data:"sprzedaz8"},{data:"sprzedaz5"},{data:"sprzedaz0zw"},{data:"naleznosc"},{data:"rodzaj"}],columnDefs:[{width:"40px",targets:1},{width:"20%",targets:[3,4]},{sClass:"ar",targets:[5,6,7,8,9]}],info:!1,stateSave:!0,lengthMenu:[10,15,20,100],pageLength:10,order:[[0,"asc"]]})}]};var f=function(n){var t=new RegExp("^([0-9]{4})-([0-9]{2})-([0-9]{2})$").exec(n);if(!t)return!1;var e=new Date(t[1],t[2]-1,t[3]);return e.getMonth()==t[2]-1&&e.getDate()==t[3]&&e.getFullYear()==t[1]};e(0);$(function(){function n(){$(".alert").slideDown("slow",function(){var n=this,t=$(this).data("timeout")||2e3;setTimeout(function(){$(n).slideUp("slow",function(){return $(n).remove()})},t)}),$(".alert").click(function(){var n=this;$(this).slideUp("slow",function(){return $(n).remove()})})}!function(){for(var n in p)if($("#"+n).length){var t=p[n];window[t[0]]=t[1]()}}(),$("#jpk tbody").on("click",'tr[role="row"]',function(){o(this)}),$("#firmy tbody").on("click",'tr[role="row"]',function(){var n=$(this).closest("tr"),t=firmy.row(n).data();window.location.href="/"+t.oznaczenie+"/"}),$("#jpk_wb").click(function(){$("#rachunki").toggle()}),$("#jpk_mag").click(function(){$("#magazyny").toggle()}),$("#przeplywy").click(function(){$("#metoda_przeplywow").toggle()}),$("#jpk_sf").click(function(){if($("#sprawozdanie").toggle(),$("#sprawozdanie").is(":visible")){var n=(new Date).getFullYear()-1,t=new Date(n+"-01-01"),e=new Date(n+"-12-31");$("#dataod").val(t.toISOString().substring(0,10)),$("#datado").val(e.toISOString().substring(0,10))}}),$(".naglowek-paczki").first().next().toggle(),$("span.tog").click(function(){$(this).parent().next().toggle()}),$(document).on("click",".dodaj-paczke",function(){var n=$(this).data("paczka");$(".modal-body #paczka").val(n),$("#plik-modal").modal("show")}),$(document).on("click",".jpk-przygotuj",function(){$("#initupload-modal").modal("hide");var n=$(this).parent().find("#initupload_jpk_id").val(),t=table.row($("#tr_"+n));setTimeout(function(){!function(n){$.ajax({dataType:"json",url:"/jpk/"+n.data().numer+"/refresh/",success:function(t){n.data(t),n.invalidate()}})}(t),a(t)},2e3)}),$(document).on("click",".plik-upload",function(){var n=$(this).data("jpk_id");$("#jpk_id").val(n),$("#upload-modal").modal("show")}),$(document).on("click",".sf-upload",function(){var n=$(this).data("jpk_id");$("#sf-jpk_id").val(n),$("#sf-modal").modal("show")}),$(document).on("click",".plik-initupload",function(){var n=$(this).data("jpk_id");$("#initupload_jpk_id").val(n),$("#initupload-modal").modal("show")}),$(document).on("click",".jpk-nazwa",function(){$("#nazwa-jpk_id").val($(this).data("jpk_id")),$("#id_nazwa").val($(this).data("nazwa")),$("#nazwa-modal").modal("show")}),$(".modal").on("shown.bs.modal",function(){$(this).find("input:text:visible:first").focus()}),$("#pliki-form").submit(function(n){(function(){var n=$("#dataod").val();if(null==n||""==n)return alert("Podaj datę początku okresu JPK"),!1;if(!f(n))return alert("Niepoprawna data początku okresu: "+n),!1;var t=$("#datado").val();return null==t||""==t?(alert("Podaj datę końca okresu JPK"),!1):!!f(t)||(alert("Niepoprawna data: "+t),!1)})()||n.preventDefault()}),$(document).on("click","li.disabled",function(n){return n.preventDefault(),!1}),n(),$("#initupload-form").on("submit",function(){if(0===$("#id_plik").get(0).files.length)return!1}),$("#oznaczenie").change(function(){$.getJSON("/ajax/"+$("#oznaczenie").val()+"/dane/",function(n){$("#nazwa").val(n.nazwa),$("#nip").val(n.nip)})}),$(document).on("click","input.cancel",function(){window.location.href=$(this).data("url")}),$("#konto_kon").change(function(){$("#konto_kon").val()?$.getJSON("/bra/ajax/"+$("#id_firma").val()+"/konto/"+$("#konto_kon").val()+"/",function(n){n.errors?$("#konto_spr-div").addClass("has-error"):$("#konto_spr-div").removeClass("has-error"),$("#konto_kon-help").html(n.nazwa)}):$("#konto_kon-help").html("")}),$("#konto_spr").change(function(){$.getJSON("/bra/ajax/"+$("#id_firma").val()+"/konto/"+$("#konto_spr").val()+"/",function(n){n.errors?$("#konto_spr-div").addClass("has-error"):$("#konto_spr-div").removeClass("has-error"),$("#konto_spr-help").html(n.nazwa)})}),$(window).on("beforeunload",function(n){if(window.app&&window.app.zapisane&&!window.app.zapisane())return"Dane nie zostały zapisane"}),window.jpk_log=function(t,e,a){$(".main-container").prepend('<div class="alert alert-'.concat(e,'" role="alert" data-timeout="').concat(a,'">').concat(t,"</div>")),n()},window.jpk_error=function(n,t){jpk_log("".concat(n,": ").concat(t),"danger",4e3)},window.jpk_info=function(n){jpk_log(n,"success",2e3)}})}]);