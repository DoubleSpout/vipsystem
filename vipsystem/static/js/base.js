function getQuery(url){
	  var no_q = 1,
	  now_url = url && (url.split('?')[1] || no_q) || document.location.search.slice(1) || no_q;
	  if(now_url === no_q) return false;
	  var q_array = now_url.split('&'),
		  q_o = {},
		  v_array; 
		for(var i=0;i<q_array.length;i++){
			  v_array = q_array[i].split('=');
			  try{
				q_o[v_array[0]] = decodeURIComponent(v_array[1]);
			  }
			  catch(e){
				q_o[v_array[0]] = null;
			  }
		};
		return q_o;
}




//处理商品的数组
if(window["_gooslist"] && vipgoods ){
	var qsename = getQuery()['ename']
	window['curGoods']=false
	window["_gooslist"] =  window["_gooslist"].data
 	var len = window["_gooslist"].length;
 	var len2 = window["vipgoods"].length;

 	for(var i =0;i<len;i++){
 		var ename = window["_gooslist"][i]['EName'];

 		for(var j=0;j<len2;j++){
 			if(window["vipgoods"][j]==0) continue;
 			if(ename == window["vipgoods"][j]['ename']){
 				window["_gooslist"][i]['name'] = window["vipgoods"][j]['name']
 				window["_gooslist"][i]['tips'] = window["vipgoods"][j]['tips']
 				window["_gooslist"][i]['specification'] = window["vipgoods"][j]['specification']
 				window["_gooslist"][i]['iorder'] = window["vipgoods"][j]['iorder'] - 0
 				window["_gooslist"][i]['picture'] = window["vipgoods"][j]['picture']
 				window["_gooslist"][i]['type'] = window["vipgoods"][j]['type']
 				break;
 			}
 		}
 		if(qsename && qsename == ename){
 			window['curGoods'] = window["_gooslist"][i]
 		}

 	}

 	window["_gooslist"].sort(function(a,b){
 		if(b.iorder>=a.iorder) return 1
 		else return -1
 	})
 	//console.log(window["_gooslist"],window['curGoods'])
}



function putGoodsList(list){
	if(!list) list = window['_gooslist']
	var len = list.length;
	var tmpStr = ''
	for(var k=0;k<len;k++){
		tmpStr += '<li><div class="comm_l_img"><a href="/vip/goods/info?ename='+list[k].EName+'"><img src="http://www.6998.com'+list[k].picture+'" ></a></div>'+
                  '<div class="comm_l_font"><h3>'+list[k].name+'</h3><span class="h">积分：'+list[k].Price+'</span>'+
                  '<span class="h">库存：'+list[k].Inventory+'</span><a class="icon go_money" href="/vip/goods/info?ename='+list[k].EName+'" title="兑换">兑 换</a></div></li>' 
	}
	return tmpStr
}


function fix(){
	$('.pro_cont ul li:last').css('border-bottom','none');
	$('.comm_contlist ul li:eq(0)').css('border-top','none');
	$('.comm_contlist ul li:eq(1)').css('border-top','none');
	$('.comm_contlist ul li:eq(1)').css('border-right','none');
	$('.comm_contlist ul li:eq(3)').css('border-right','none');
	$('.comm_list ul li:eq(0)').css('border-top','none');
	$('.comm_list ul li:eq(1)').css('border-top','none');
	$('.comm_list ul li:eq(2)').css('border-top','none');
	$('.comm_list ul li:eq(0)').css('border-left','none');
	$('.comm_list ul li:eq(3)').css('border-left','none');
	$('.comm_list ul li:eq(6)').css('border-left','none');
	$('.comm_list ul li:eq(9)').css('border-left','none');
	$('.comm_list ul li:eq(12)').css('border-left','none');
	$('.comm_list ul li:eq(15)').css('border-left','none');
	$('.comm_list ul li:eq(2)').css('border-right','none');
	$('.comm_list ul li:eq(5)').css('border-right','none');
	$('.comm_list ul li:eq(8)').css('border-right','none');
	$('.comm_list ul li:eq(11)').css('border-right','none');
	$('.comm_list ul li:eq(14)').css('border-right','none');
	$('.comm_list ul li:eq(17)').css('border-right','none');
	$('.comm_list ul li:eq(20)').css('border-right','none');
	$('.comm_list ul li:eq(23)').css('border-right','none');
}


function initDiv(){
	$('#err_ic_wrong').hide()
	$('#err_ic_right').hide()
	$('#confirm_exchange').hide()
	$('#confirm').hide()
	$('#goods_result').empty()

}


$(function(){

	//vip商城的轮播html
	if($('#shop_pic_box').length>0 && vippictures){
		var templatePic = '<a target="_blank" href="{link}" style="{show}"><img src="http://www.6998.com{pic}"></a>';
		var templateBtn = '<a href="javascript:;" class="{sel}"></a>'
		var len = vippictures.length;
		var picStr = ''
		var btnStr = ''
		for(var i=0;i<len;i++){
			var str1=templatePic
			var str2=templateBtn
			if(vippictures[i] == 0) continue;
			if(i==0){
				var s = ''
				var c = 'sel'
			}
			else{
				s = 'display: none;'
				c = ''
			}

			str1 = str1.replace('{link}',vippictures[i]['link'])
					   .replace('{show}',s)
					   .replace('{pic}',vippictures[i]['vipurl'])

			str2 = str2.replace('{sel}',c)

			picStr+=str1
			btnStr+=str2
		}

		$('#imgBox').html(picStr)
		$('#picBtn').html(btnStr)
	}

	//vip商城的轮播html
	if($('#vip_pic_box').length>0 && vippictures){
		var templatePic = '<a target="_blank" href="{link}" style="{show}"><img src="http://www.6998.com{pic}"></a>';
		var templateBtn = '<a href="javascript:;" class="{sel}"></a>'
		var len = vippictures.length;
		var picStr = ''
		var btnStr = ''
		for(var i=0;i<len;i++){
			var str1=templatePic
			var str2=templateBtn
			if(vippictures[i] == 0) continue;
			if(i==0){
				var s = ''
				var c = 'sel_2'
			}
			else{
				s = 'display: none;'
				c = ''
			}

			str1 = str1.replace('{link}',vippictures[i]['link'])
					   .replace('{show}',s)
					   .replace('{pic}',vippictures[i]['url'])

			str2 = str2.replace('{sel}',c)

			picStr+=str1
			btnStr+=str2
		}

		$('#imgBox_2').html(picStr)
		$('#picBtn_2').html(btnStr)
	}



	if($('#goods_index_box').length>0 ){
		var si_str1 = '<li>'+_gooslist[0].name+'</li>'+
					   '<li class="comm_f">'+_gooslist[0].Price+'积分</li><li class="m_t">'+
					   '<a href="/goods/info?ename='+_gooslist[0].EName+'"><img src="http://www.6998.com'+_gooslist[0].picture+'" ><i>新</i></a></li>'
		$('#shop_index_box_1').html(si_str1)

		var si_str2 = ''
		for(var k=1;k<5;k++){
			si_str2 += '<li><div class="comm_l_img"><a href="/vip/goods/info?ename='+_gooslist[k].EName+'"><img src="http://www.6998.com'+_gooslist[k].picture+'" ></a></div>'+
                       '<div class="comm_l_font"><h3>'+_gooslist[k].name+'</h3><span class="h">积分：'+_gooslist[k].Price+'</span><span class="h">库存：'+_gooslist[k].Inventory+'</span>'+
                       '<a class="icon go_money" href="/vip/goods/info?ename='+_gooslist[k].EName+'" title="兑换">兑 换</a></div></li>'
		}
		$('#shop_index_box_2').html(si_str2)
		fix()
	}

	if($('#goods_list_box').length>0){
		$('#goods_list_box').html(putGoodsList())
		fix()

		var filtera = $('a[name="scoreFilter"]')
		filtera.click(function(){
			var that = $(this);
			if(that.hasClass('cho_red')){
				//filtera.removeClass('cho_red')
				//$('#goods_list_box').html(putGoodsList())
				//fix()
				return false;
			}

			filtera.removeClass('cho_red')
			that.addClass('cho_red')
			var min = that.attr('min')-0
			var max = that.attr('max')-0
			var tempArray = []
			var len = window['_gooslist'].length
			for(var i=0;i<len;i++){
				if(window['_gooslist'][i].Price >= min && window['_gooslist'][i].Price <= max){
					tempArray.push(window['_gooslist'][i])
				}
			}
			$('#goods_list_box').html(putGoodsList(tempArray))
			fix()
			return false;
		})
	
	}

	$('#sign_in').click(function(){
		$('#day_frame').attr('src', '/sign/index')
		$(window).scrollTop(0);
			$('#day_box').dialog({
				width:590,
				height:650,
				modal:true,
				close:function(){
					if(window['_hasTodaySign']){
						location.href = location.href
						return false;
					}
					$('#day_frame').attr('src','');
				}
		})
	})


	if($('#goods_detail_title').length>0){

		 $('#goods_detail_title').html(curGoods.name);
		 $('#goods_detail_title2').html(curGoods.name);
		 $('#goods_detail_picture').attr('src', 'http://www.6998.com'+curGoods.picture)
		 $('#goods_detail_price').html(curGoods.Price);
		 $('#goods_detail_inventory').html(curGoods.Inventory);
		 $('#goods_detail_specification').html(curGoods.specification);
		 $('#goods_detail_tips').html(curGoods.tips);

		 if(curGoods.Inventory <= 0){
		 	$('#no_inventory').show()
		 }
		 else{
		 	$('#sub_exchange').show()
		 }

		 $('#sub_exchange').click(function(){
			$(window).scrollTop(0);
			$('#goods_box').dialog({
					width:400,
					height:280,
					modal:true,
					close:function(){
						if(window.mustRefresh){
							location.href = location.href
							return false;
						}
					}
				})

			initDiv();
			var tempStr = '<p>您选择兑换礼品为：<b>'+curGoods.name+'</b></p><p>扣除积分：<b>'+curGoods.Price+'</b> 分</p>'
			if(curGoods.Type == 'gameCard'){
				tempStr+='<p><span>该礼包每帐号限用一次</span></p>'
			}
			
			$('#goods_result').html(tempStr)
			$('#confirm_exchange').show()
	        return false;
		})

		window.exchanging = false;
		$('#confirm_exchange').click(function(){
			if(window.exchanging) return false;
			window.exchanging = true
			$.post('/goods/exchange',{ename:curGoods.EName},function(d){
				$('#confirm_exchange').hide()
				if(d.error == 1){
					$('#err_ic_wrong').show()
					$('#goods_result').html('<p><span>操作失败</span></p><p>'+d.data+'</p>')
				}
				else{
					$('#err_ic_right').show()
					var codeStr = ''
					if(d.data && d.data.type == 'gameCard'){
						codeStr = '<p><b>您的礼品卡号为：'+d.data.code+'</b></p>' 
					}
					$('#goods_result').html('<p><b>恭喜您兑换成功</b></p>'+codeStr)
					
					$('#confirm').click(function(){
						location.href = location.href 
					})
					$('#confirm').show()
					window.mustRefresh = true
				}
				window.exchanging = false
			},'json')
		})

	}




	
	//常见问题页面 信息展开和关闭
	$('.prob_cont h2:first').addClass('close_but');
	$('.prob_cont .open_font:not(:first)').hide();
	$('.prob_cont h2').click(function(){
		$(this).next('.open_font').slideToggle()
				.siblings('.open_font').slideUp();
		$(this).toggleClass('close_but')
				.siblings('.prob_cont h2').removeClass('close_but');
		});
		
		
	//VIP特权选项卡切换
	$('.vip_ct:gt(0)').hide();
	var vip_lab = $('.vipcen_labtit ul li');
	vip_lab.hover(function(){
		$(this).addClass('vipcen_titover')
				.siblings().removeClass('vipcen_titover');
		$('.vip_ct').eq(vip_lab.index(this)).show()
					.siblings().hide();
	});
	

	var posid = getQuery()['pos']
	if($('#qa_box').length>0 &&  posid && posid != 1){
		jqPos = $('#pos'+posid)
		if(jqPos.length>0){
			jqPos.click();
		}
	}

	$('#get_salary').click(function(){

		$.post('/salary/get',{t:Math.random()},function(d){
			if(d.error){
				return alert(d.data)
			}
			alert('操作成功,请到充值中心体现')
			setTimeout(function(){
				location.href = location.href
			},500)
		},'json')

	})


	var pic1 = function(){		//幻灯1
				var picBtna = $('#picBtn').find('a'),
					imgobj = $('#imgBox a'),
					len = $('#imgBox a').length,
					st,
					snum = 0,
					goshow = function(num){
						var n = num;
						if(n>=len) n=0;
						else if(n<0) n=0;
						imgobj.hide().eq(n).show();
						picBtna.removeClass('sel').eq(n).addClass('sel');
						snum=n;
						loopgo();
					},
					loopgo=function(){
						st = setTimeout(function(){goshow(snum+1);},5000)
						return arguments.callee;			
						}();
					picBtna.click(function(){
						var num = $(this).index();	
						clearTimeout(st);
						goshow(num)
				});
		}()

		//幻灯2
	var pic2 = function(){	
	var picBtna = $('#picBtn_2').find('a'),
			imgobj = $('#imgBox_2 a'),
				len = $('#imgBox_2 a').length,
				st,
				snum = 0,
				goshow = function(num){
					var n = num;
					if(n>=len) n=0;
					else if(n<0) n=0;
					imgobj.hide().eq(n).show();
					picBtna.removeClass('sel_2').eq(n).addClass('sel_2');
					snum=n;
					loopgo();
				},
				loopgo=function(){
					st = setTimeout(function(){goshow(snum+1);},5000)
					return arguments.callee;			
					}();
				picBtna.click(function(){
					var num = $(this).index();	
					clearTimeout(st);
					goshow(num)
			});
		}()
          $('a[name="minilogin"]').click(function(){
			$(window).scrollTop(0);
			$('#mini_login_box').dialog({
					width:500,
					height:340,
					modal:true,
				})
                        var backurl = encodeURIComponent(location.href)
			$('#mini_login_iframe').attr('src', '/vip/login?jumpto='+backurl)
			$('#mini_login_box').show()
	        return false;
	  })
});
	
	






