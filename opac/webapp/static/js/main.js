var isOldIE = $("html").is(".lt-ie9");
var Portal = {
		MenuOpened: false,
		Init: function() {
			$(".showTooltip").each(function() {
				var data = $(this).data(),
					pContainer = typeof data.container != "undefined" ? data.container : 'body',
					pPlacement = typeof data.placement != "undefined" ? data.placement : 'top';

				$(this).tooltip({
					container: pContainer,
					placement: pPlacement
				});
			}); 

			$(".mainNav .menu").on("click",function(e) {
				e.preventDefault();

				var t = $(this),
					d = t.data("rel");

				d = $(d,".mainNav");
				
				if(d.is(":visible")) {
					t.removeClass("opened");
					d.slideUp("fast",function() {
						Portal.MenuOpened = false;		
					});
					
				} else {
					t.addClass("opened");
					d.slideDown("fast",function() {
						Portal.MenuOpened = true;	
					});
				}
			});

			$(".shareFacebook,.shareTwitter,.shareDelicious,.shareGooglePlus,.shareLinkedIn,.shareReddit,.shareStambleUpon,.shareCiteULike,.shareMendeley").on("click",function(e) {
				e.preventDefault();

				var url = escape(this.href),
					links = {
						"facebook": "https://www.facebook.com/sharer/sharer.php?u=",
						"twitter": "https://twitter.com/intent/tweet?text=",
						"delicious": "https://delicious.com/save?url=",
						"googleplus": "https://plus.google.com/share?url=",
						"linkedin": "http://www.linkedin.com/shareArticle?mini=true&url=",
						"reddit": "http://www.reddit.com/submit?url=",
						"stambleupon": "http://www.stumbleupon.com/submit?url=",
						"citeulike": "http://www.citeulike.org/posturl?url=",
						"mendeley": "http://www.mendeley.com/import/?url="
					},
					go2 = "";
				if($(this).is(".shareFacebook"))
					go2 = links.facebook + url;
				else if($(this).is(".shareTwitter"))
					go2 = links.twitter + url;
				else if($(this).is(".shareDelicious"))
					go2 = links.delicious + url;
				else if($(this).is(".shareGooglePlus"))
					go2 = links.googleplus + url;
				else if($(this).is(".shareLinkedIn"))
					go2 = links.linkedin + url;
				else if($(this).is(".shareReddit"))
					go2 = links.reddit + url;
				else if($(this).is(".shareStambleUpon"))
					go2 = links.stambleupon + url;
				else if($(this).is(".shareCiteULike"))
					go2 = links.citeulike + url;
				else if($(this).is(".shareMendeley"))
					go2 = links.mendeley + url;

				window.open(go2,'share');
			});

			$(".slider").each(Portal.Slider);

			$(".sendViaMail").on("click",function(e) {
				e.preventDefault();
				$("#SendViaEmail").modal("show");
			});

			$(".showBlock").on("click",function() {
				var t = $(this),
					rel = t.data("rel"),
					hide = t.data("hide");

				$(rel).find("input:text,textarea").val("");
				$(rel).slideDown("fast");
				$(hide).hide();
			});

			$(".showFloatInfo").on("click",function() {
				var cmd = $(this).data("rel");
				cmd = cmd.split(";");

				$("a",cmd[0]).removeClass("selected");
				$(cmd[2]).hide();

				if(cmd[1] != "null") {
					$(this).addClass("selected");
					$(cmd[1]).fadeIn("fast");
				}			
			});

			$(".alternativeHeader").each(function() {
				var menu = $(".mainMenu nav ul").html();
				$(this).find("nav ul").html(menu);
			});

			var headerHeight = $("header").outerHeight();
			$(window).on("scroll",function() {
				var y = window.scrollY > 0 ? window.scrollY : (window.pageYOffset > 0 ? window.pageYOffset : document.documentElement.scrollTop);

				if(y > headerHeight) {
					$(".alternativeHeader").stop(true,false).animate({
						top: "0"
					},200,function() {
						if($("#mainMenu").is(":visible"))
							$(".menu:eq(0)").trigger("click");
					});
				} else {
					$(".alternativeHeader").stop(true,false).animate({
						top: "-60px"
					},200,function() {
						if($(this).find(".mainMenu").is(":visible"))
							$(this).find(".menu").trigger("click");
					});
				}
			}).on("keydown",function(e) {
				if(e.keyCode == 27 && $("a.menu").is(".opened"))
					$("a.menu").trigger("click");
			});

			$("body").on("click",function (e) {
				var dest = e.target;

				if(!$(dest).is(".menu") && Portal.MenuOpened == true) {
					var t = $("a.menu"),
						d = ".mainMenu";

					t.removeClass("opened");
					$(d).slideUp("fast",function() {
						Portal.MenuOpened = false;		
					});
				}
			});

			$(".expandCollapseContent").on("click",function(e) {
				e.preventDefault();

				var idx = $("#issueIndex"),
					info = $("#issueData"),
					t = this;

				idx.css("float","right");

				if(info.is(":visible")) {
					info.fadeOut("fast",function() {
						idx.animate({
							width: "100%"
						},300);
						$(t).find(".glyphBtn").removeClass("opened").addClass("closed");
					});
				} else {
					idx.animate({
						width: "75%"
					},300,function() {
						info.fadeIn("fast");
						$(t).find(".glyphBtn").removeClass("closed").addClass("opened");
					});
				}
				
				$(t).tooltip("hide");

			});

			$(".collapse-title").on("click",function() {
				var t = $(this),
					ctt = t.next(".collapse-content");

				if(ctt.is(":visible")) {
					ctt.slideUp("fast");
					t.addClass("closed");
				} else {
					ctt.slideDown("fast");
					t.removeClass("closed");
				}
			});

			$(".goto").on("click",function(e) {
				e.preventDefault();

				var d = $(this).attr("href");
				d = d.replace("#","");

				var p = $("a[name="+d+"]").offset();

				$("html,body").animate({
					scrollTop: (p.top-60)
				},500);
			});

			
			$(".trigger").on("click",function(e) {
				e.preventDefault();
				var obj = $(this).data("rel");

				$(obj).click();
			});

			$("input[name='link-share']").focus(function() {
				$(this).select();
				if (window.clipboardData && clipboardData.setData) {
					clipboardData.setData('text', $(this).text());
				} 
			}).mouseup(function(e) {
				e.preventDefault();
			});

			$(".levelMenu .dropdown-container").on("mouseenter mouseleave",function(e) {
				var menu = $(this).find(".dropdown-menu"),
					toggle = $(this).find(".dropdown-toggle");

				if(e.type == "mouseenter") {
					menu.show();
					toggle.addClass("hover");
				} else {
					menu.hide();
					toggle.removeClass("hover");
				}
			});

			$(".nav-tabs a").click(function(e) {
  				e.preventDefault()
  				$(this).tab("show");
			});

			$(".translateAction").on("click",function(e) {
				e.preventDefault();
				$("#translateArticleModal").modal("show");			
			});
			
			/*if(typeof ZeroClipboard != "undefined") {
				client = new ZeroClipboard($(".copyLink"));

				client.on("aftercopy",function(event) {
					var t = $(event.target);

					t.off("mouseover mouseenter mouseout mouseup blur");

					if(t.is(".copyLink")) {
						t.addClass("copyFeedback");
						setTimeout(function() {
							t.removeClass("copyFeedback");
						},2000);
					}
				});
			}*/

			if(typeof Clipboard != "undefined") {
				var clipboard = new Clipboard('.copyLink');

				clipboard.on('success', function(e) {
					var t = $(e.trigger);

					t.addClass("copyFeedback");
					setTimeout(function() {
						t.removeClass("copyFeedback");
					},2000);

				    e.clearSelection();
				});
			}


			//Include share links
			var linkArticle = "",
				html 		= "",
				results 	= $(".results .item");
			
			for (var i = 0; i < results.length; i++) { 
				var article = $(results[i]).parent();
				linkArticle = article[0].children[i].children[1].children[0].children[0].href;
				
				html = '<br class="visible-xs visible-sm"/><span class="socialLinks articleShareLink">\
					<a href="" class="articleAction sendViaMail" data-toggle="tooltip" data-placement="top" title="Enviar link por e-mail">Enviar por e-mail</a>\
					<a target="_blank" href="https://www.facebook.com/sharer/sharer.php?u='+linkArticle+'" class="articleAction shareFacebook" data-toggle="tooltip" data-placement="top" title="Compartilhar no Facebook">Facebook</a>\
					<a target="_blank" href="https://twitter.com/intent/tweet?text='+linkArticle+'" class="articleAction shareTwitter" data-toggle="tooltip" data-placement="top" title="Compartilhar no Twitter">Twitter</a>\
					<a target="_blank" href="https://delicious.com/save?url='+linkArticle+'" class="articleAction shareDelicious" data-toggle="tooltip" data-placement="top" title="Compartilhar no Delicious">Delicious</a>\
					<a href="" class="showTooltip dropdown-toggle" data-toggle="dropdown" data-placement="top" data-placement="top" title="Compartilhar em outras redes"><span class="glyphBtn otherNetworks"></span></a>\
					<ul class="dropdown-menu articleShare">\
						<li class="dropdown-header">Outras redes sociais</li>\
						<li><a target="_blank" href="https://plus.google.com/share?url='+linkArticle+'" class="shareGooglePlus"><span class="glyphBtn googlePlus"></span> Google+</a></li>\
						<li><a target="_blank" href="https://www.linkedin.com/shareArticle?mini=true&url='+linkArticle+'" class="shareLinkedIn"><span class="glyphBtn linkedIn"></span> LinkedIn</a></li>\
						<li><a target="_blank" href="https://www.reddit.com/login?dest='+linkArticle+'" class="shareReddit"><span class="glyphBtn reddit"></span> Reddit</a></li>\
						<li><a target="_blank" href="http://www.stumbleupon.com/submit?url='+linkArticle+'" class="shareStambleUpon"><span class="glyphBtn stambleUpon"></span> StambleUpon</a></li>\
						<li><a target="_blank" href="http://www.citeulike.org/posturl?url='+linkArticle+'" class="shareCiteULike"><span class="glyphBtn citeULike"></span> CiteULike</a></li>\
						<li><a target="_blank" href="https://www.mendeley.com/import/?url='+linkArticle+'" class="shareMendeley"><span class="glyphBtn mendeley"></span> Mendeley</a></li>\
					</ul>\
				</span>';

				var b = i+1;

				$(".results .item:nth-child("+b+") div .line.articleResult").append(html);

			}
		},
		Slider: function() {
			var id = $(this).attr("id"),
				el = $("#"+id),
				container = el,
				itens = $(".slide-item", container),
				wrapper = $(".slide-wrapper", container),
				prev = $(".slide-back", container),
				next = $(".slide-next", container),
				itemProps = {
					w: itens.eq(0).outerWidth(),
					h: itens.eq(0).outerHeight()
				},
				wrapperWidth = (itens.length*itemProps.w)+100,
				containerWidth = $(".slide-container", container).outerWidth();

			wrapper.width(wrapperWidth);
			$(".slide-container", container).height(itemProps.h);
			
			prev.css("top",(itemProps.h/2)+"px");
			next.css("top",(itemProps.h/2)+"px");

			prev.hide();
			if(wrapper.width() <= container.width())
				next.hide();
			else
				next.show();

			prev.off().on("click",function(e) {
				e.preventDefault();
				var left = wrapper.css("left") == "auto" ? 0 : parseInt(wrapper.css("left"));

				wrapper.animate({
					left: "+="+itemProps.w
				},300,function() {
					var nLeft = wrapper.css("left") == "auto" ? 0 : parseInt(wrapper.css("left"));
					if(nLeft == 0) 
						prev.hide();
				});
				next.show();
			
			});

			next.off().on("click",function(e) {
				e.preventDefault();
				var left = wrapper.css("left") == "auto" ? 0 : parseInt(wrapper.css("left"));

				wrapper.animate({
					left: "-="+itemProps.w
				},300,function() {
					var nLeft = wrapper.css("left") == "auto" ? 0 : parseInt(wrapper.css("left"));
					if(nLeft <= -(wrapperWidth-containerWidth-100)) 
						next.hide();
				});
				prev.show();
			});

		}
	},
	SearchForm = {
		SearchHistory: "",
		Init: function() {
			var p = "form.searchForm";

			SearchForm.SearchHistory = Cookie.Get("searchHistory");

			$("input.trigger").off("click").on("click",function() {
				var cmd = $(this).data("rel");
				eval(cmd);
			});

			$(p).on("submit",function(e) {
				var expr = $("input[name='q[]']",p),
					connector = $("select[name='bool[]']",p),
					idx = $("select[name='index[]']",p),
					searchQuery = "";

				for(var i=0,l=expr.length;i<l;i++) {
					var v = $(expr[i]).val();
					if(v != "") {
						var ci = $("option:selected",idx[i]).val();

						if(i >= 1) {
							var b = $("option:selected",connector[i-1]).val();
							searchQuery += " "+b+" ";
						}
						if(ci != "") {
							searchQuery += "("+ci+":("+v+"))";
						} else {
							searchQuery += (l == 2 ? v : "("+v+")");
						}
					}
				}

				/*
				if(searchQuery != "") {
					var cHistory = SearchForm.SearchHistory,
						dHistory = [];

					if(cHistory !== "") {
						dHistory = JSON.parse(cHistory);
					}

					dHistory.splice(0, 0, searchQuery)
					dHistory = dHistory.slice(0,10);

					Cookie.Set("searchHistory",JSON.stringify(dHistory),1);
				} */

				return true;
			});

			/*
			if(SearchForm.SearchHistory != "") {
				var shObj = JSON.parse(SearchForm.SearchHistory),
					shDropdown = $("#searchHistory",p);

				if(shObj.length > 0) {
					var inc = "";

					inc += "<li><strong>"+shDropdown.data("title")+"</strong> <a href='javascript:;' class='inline cleanSearchHistory'></a></li>";

					for(var i=0,l=shObj.length;i<l;i++) {
						inc += '<li><a href="javascript:;" class="searchItem"><span>#'+(i+1)+':</span> '+shObj[i]+'</a></li>';
					}

					shDropdown.append(inc);
				}
			}

			$("#searchHistory").on("click","a.searchItem",function(e) {
				e.preventDefault();
				var ref = $("#searchHistory").data("rel");
				SearchForm.SearchHistoryClick(this,ref);
			}).on("click","a.cleanSearchHistory",function(e) {
				e.preventDefault();
				SearchForm.SearchHistory = "";
				Cookie.Set("searchHistory","",0);
				$("#searchHistory").empty();
			});
			*/

			/*
			$("input[name='q[]']").on("focus",function() {
				SearchForm.SearchHistoryFocusIn(this);
			}).on("blur",function() {
				SearchForm.SearchHistoryFocusOut(this);
			});
			*/

			//$("textarea.form-control:visible",p);
			$("textarea.form-control",p).on("keyup",SearchForm.TextareaAutoHeight).trigger("keyup").on('keypress', function(e) {
				if(e.which == 13 && ! e.shiftKey) {
					$(p).submit();
				}
			});
			$("textarea.form-control",p)
			$("a.clearIptText",p).on("click",SearchForm.ClearPrevInput);

		
			if($(".searchActions",p).length)
				window.searchActionsStart = $(".searchActions",p).offset().top;
			
			$(".newSearchField",p).on("click",function(e) {
				e.preventDefault();
				SearchForm.InsertNewFieldRow(this,"#searchRow-matriz .searchRow",".searchForm .searchRow-container");
			});

			$("select.setMinValue").on("change",function() {
				var v = $(this).val(),
					d = $(this).data("rel");

				var dv = $(d).val();
				v = parseInt(v);
				dv = parseInt(dv);

				if(dv < v)
					$(d).val("0");

				$("option",d).each(function() {
					var iv = parseInt($(this).text());
					if(iv <= v)
						$(this).prop("disabled",true);
					else
						$(this).prop("disabled",false);
				});
			});

			$("a.action",p+" .collapseBlock .title").on("click",function() {
				var t = $(this),
					ctt = t.parent().next(".content");

				if(ctt.is(":visible")) {
					ctt.slideUp("fast");
					t.addClass("closed").removeClass("opened");
					t.parent().addClass("closed");
				} else {
					ctt.slideDown("fast");
					t.addClass("opened").removeClass("closed");
					t.parent().removeClass("closed");
				}
			});

			$(".collapseBlock .filterCollapsedList",p).each(function() {
				var t = $(this),
					chd = t.find(".filterItem"),
					showAll = $(".showAll",t);

				if(chd.length > 5) {
					showAll.show();
				}
			});

			$(".collapseBlock .showAll",p).on("click",function() {
				var t = $(this),
					pt = t.parent(),
					txtToggle = t.data("texttoggle"),
					txt = t.text();

				if(pt.outerHeight() > 200) {
					pt.removeClass("opened");
				} else {
					pt.addClass("opened");
				}
				t.text(txtToggle).data("texttoggle",txt);
			});

			$(".articleAction, .searchHistoryItem, .colActions .searchHistoryIcon",p).tooltip();

			$(".selectAll",p).on("click",function() {
				var t = $(this),
					itens = $(".results .item input.checkbox",p),
					selCount = $("#selectedCount",p),
					selCountInt = parseInt(selCount.text());

				if(t.is(":checked")) {
					itens.each(function() {
						$(this).prop("checked",true);
					});
					t.data("all","1");
				} else {
					itens.each(function() {
						$(this).prop("checked",false);
					});
					t.data("all","0");
				}
				SearchForm.CountCheckedResults("#selectedCount",".results .item input.checkbox:checked");
			});

			$(".clusterSelectAll").on("click",function() {
				var t = $(this),
					itens = $("#selectClusterItens .filterBody input.checkbox");

				if(t.is(":checked")) {
					itens.each(function() {
						$(this).prop("checked",true);
					});
					t.data("all","1");
				} else {
					itens.each(function() {
						$(this).prop("checked",false);
					});
					t.data("all","0");
				}
			});

			$(".results .item input.checkbox",p).on("change",function() {
				var t = $(this),
					selAll = $(".selectAll",p),
					selCount = $("#selectedCount",p),
					selCountInt = parseInt(selCount.text());

				if(!t.is(":checked")) {
					var all = selAll.data("all");
					if(all == "1") {
						selAll.prop("checked",false).data("all","0");
					}
				}

				// Executar aqui ações para adicionar item à "sua lista"

				SearchForm.CountCheckedResults("#selectedCount",".results .item input.checkbox:checked");
			});

			$("a.orderBy",p).on("click",function() {
				var t = $(this),
					field = t.data("field"),
					container = $(t.data("rel")),
					sort = [];

				$(".filterItem",container).each(function() {
					var ti = $(this),
						val = ti.data(field),
						arr = [];

					if(!isNaN(parseInt(val))) {
						val = parseInt(val);
					}
					arr.push(val);
					arr.push(ti);
					sort.push(arr);
					ti.remove();
				});

				if(typeof sort[0][0] === "number")
					sort.sort(function(a, b){return b[0]-a[0]});
				else
					sort.sort();

				for(var i=0;i<sort.length;i++) {
					container.append(sort[i][1]);
				}
			});


			$(".openNewWindow").on("click",function(e) {
				e.preventDefault();
				
				window.open(this.href,'print','width=760,height=550');
			});

			$(".openStatistics",p).on("click",function(e) {
				e.preventDefault();

				var t = $(this),
					title = t.data("cluster"),
					chartType = t.data("type"),
					csvLink = t.data("csv"),
					chartSource = t.data("chartsource");

				$("#Statistics").data({
					"title": title,
					"charttype": chartType,
					"csvlink": csvLink,
					"chartsource": chartSource
				}).modal({
					"show": true
				});
			});

			$(".openSelectItens",p).on("click",function(e) {
				e.preventDefault();

				var t = $(this),
					rel = t.data("rel"),
					mod = $("#selectClusterItens"),
					modContainer = $(".filterBody",mod),
					modTitle = $(".modal-title",mod);

				modTitle.html(t.text());
				modContainer.empty();
				
				var c = $(".filterItem",rel).clone();
				modContainer.append(c);
				modContainer.find(".checkbox").each(function() {
					var cId = $(this).attr("id"),
						nId = cId+"cf";

					$(this).attr("id",nId);
					modContainer.find("label[for='"+cId+"']").attr("for",nId);
				});

				mod.modal("show");

			});

			$("#selectClusterItens").on("shown.bs.modal",function() {
				var container = this;
				$(".filterBody input.checkbox",container).on("click",function() {
					var t = $(this),
						selAll = $(".clusterSelectAll",container),
						itensCount = $(".itensCount",container);

					if(!t.is(":checked")) {
						var all = selAll.data("all");
						if(all == "1") {
							selAll.prop("checked",false).data("all","0");
						}
					}

					
				});
			});

			$("#Statistics").on("shown.bs.modal",function() {
				var t = $(this),
					chartBlock = $(".chartBlock",this),
					title = t.data("title"),
					chartType = t.data("charttype"),
					csvLink = t.data("csvlink"),
					chartSource = t.data("chartsource");


				t.find(".modal-title .cluster").text(title);
				t.find(".link a").attr("href",csvLink);

				chartBlock.html('<canvas id="chart" width="550" height="400"></canvas>');
				
				var canvas = $("#chart").get(0);

				if(isOldIE) {
	 				canvas = G_vmlCanvasManager.initElement(canvas);
				}

				var ctx = canvas.getContext("2d");
				ctx.clearRect(0,0,550,400);


				$.ajax({
					url: chartSource,
					type: "POST",
					dataType: "json",
					beforeSend: function() {
						chartBlock.addClass("loading");
					}
				}).done(function(data) {
					chartBlock.removeClass("loading");
					switch(chartType) {
						case "doughnut":
							window.graph = new Chart(ctx).Doughnut(data,{
								scaleGridLineWidth : 1
							});
							break;
						case "bar":
							window.graph = new Chart(ctx).Bar(data,{
								scaleGridLineWidth : 1
							});
							break;
						case "line":
							window.graph = new Chart(ctx).Line(data,{
								scaleGridLineWidth : 1
							});
							break;
						case "pie":
							window.graph = new Chart(ctx).Pie(data,{
								scaleGridLineWidth : 1
							});
							break;
						default:
							window.graph = new Chart(ctx).Pie(data,{
								scaleGridLineWidth : 1
							});
							break;
					}
				});
			}).on("hidden.bs.modal",function() {
				window.graph.clear().destroy();
				$(".chartBlock canvas",this).remove();
			});

			$("#SendViaEmail,#Export").on("shown.bs.modal",function() {
				var t = $(this),
					selection = parseInt($("#selectedCount").text());

				t.find("input:eq(0)").focus();

				if(selection > 0) {
					t.find(".selection").show();
					t.find(".selection strong").text(selection);
				} else {
					t.find(".selection").hide();
				}
			});

			$("form.validate").on("submit",function() {
				var rtn = true; 
				
				$("input.valid",this).each(function() {
					var ti = $(this);

					if(ti.is(".multipleMail")) {
						if(Validator.MultipleEmails(ti.val(),";") === false) {
							ti.parent().addClass("has-error");
							rtn = false;
						} else 
							ti.parent().removeClass("has-error");
					} else {
						if(ti.val() === "") {
							ti.parent().addClass("has-error");
							rtn = false;
						} else
							ti.parent().removeClass("has-error");
					}
				});

				return rtn;
			});

			$(".searchHistoryIcon.add",p).on("click",function() {
				$("html, body").animate({ scrollTop: 0 }, "fast");
				SearchForm.InsertSearchHistoryItem(this);
			});
			$(".searchHistoryIcon.search",p).on("click",function() {
				$("#iptQuery").empty();
				SearchForm.InsertSearchHistoryItem(this);
				$("#searchHistoryForm").submit();
			});
			$(".searchHistoryIcon.erase",p).on("click",function(e) {
				e.preventDefault();
				var $item = $(this).data("item");
				$("#confirmEraseItem span.item").text($item);
				$("#confirmEraseItem input.item").val($item);

				$("#confirmEraseItem").modal("show");			
			});
			$(".searchHistoryIcon.eraseAll",p).on("click",function(e) {
				e.preventDefault();
				
				$("#confirmEraseAll").modal("show");			
			});

			$("#iptQuery").on("keypress",function(e) {
				if(e.keyCode == 13)
					$("#searchHistoryForm").submit();
			});

			$("#searchHistoryForm").on("submit",function() {
				var q = $.trim($("#iptQuery").text()),
					ipt = $("#query");
				
				ipt.val(q);

				return true;
			});

			$(".showTooltip").tooltip({
				container: 'body'
			});

			$("input[data-show!=''],input[data-hide!='']").on("click",function() {
				var s = $(this).data("show"),
					h = $(this).data("hide");

				if(typeof s != "undefined")
					$(s).slideDown("fast").find("input[type='radio']:eq(0)").trigger("click");

				if(typeof h != "undefined")
					$(h).slideUp("fast");

			});

			$(".searchModal").on("click",function() {
				var d = $(this).data("modal"),
					expr = $(this).data("expr");

				$(".searchExpression",d).text(expr);
				$("#clipboardSearchExpression").val(expr);

				$(d).modal("show");
			});

			$(".editQuery").on("click",function() {
				var d = $(this).data("modal"),
					expr = $(this).data("expr"),
					q = $("#iptQuery");

				q.append(expr).focus();
				$(this).effect("transfer", { to: q }, 1000);
				SearchForm.PlaceCaretToEnd(document.getElementById("iptQuery"));
			});

			if(typeof ZeroClipboard != "undefined") {
				var client = new ZeroClipboard( document.getElementById("CopyToClipboard"));
				client.on("ready", function( readyEvent ) {
					client.on( "aftercopy", function( event ) {
						$("#CopyToClipboard").addClass("success");
						var t = setTimeout(function() {
							$("#CopyToClipboard").removeClass("success");
						},2000);
					});
				});
			}

			$(".openCitationModal").on("click",function() {
				var modal = $("#CitationModal"),
					title = $(this).data("title");
					citationContainer = $("#CitationModal-Citations"),
					downloadContainer = $("#CitationModal-Downloads"),
					citation = $(this).data("citation"),
					citationCtt = "",
					download = $(this).data("download"),
					downloadCtt = "";

				if(typeof citation != "undefined" && typeof download != "undefined") {
					citation = citation.split(";;");
					for(var i=0,l=citation.length;i<l;i++) {
						citation[i] = citation[i].split("::");
						citation[i][1] = citation[i][1].replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/\[b\]/g,"<strong>").replace(/\[\/b\]/g,"</strong>");

						citationCtt += '<div class="modal-body searchExpression">';
						citationCtt += '	<label>'+citation[i][0]+'</label>';
						citationCtt += '	<div>'+citation[i][1]+'</div>';
						citationCtt += '</div>';
					}

					download = download.split(";;");
					for(var i=0,l=download.length;i<l;i++) {
						download[i] = download[i].split("::");
						
						downloadCtt += '<a href="'+download[i][1]+'" target="_blank" class="download">'+download[i][0]+'</a> ';
					}

					citationContainer.html(citationCtt);
					downloadContainer.html(downloadCtt);

					modal.find(".modal-title strong").html(title);
					modal.modal("show");
				}
			});

			$("input.onlyNumbers").on("keydown",function(e) {
				if($.inArray(e.keyCode, [46, 8, 9, 27, 13, 110]) !== -1 ||
					// Ctrl+A
					(e.keyCode == 65 && e.ctrlKey === true) || 
					// Ctrl+V
					(e.keyCode == 86 && e.ctrlKey === true) || 
					// Ctrl+R
					(e.keyCode == 82 && e.ctrlKey === true) || 
					// home, end, left, right
					(e.keyCode >= 35 && e.keyCode <= 39) ||
					// macosX keycodes
					(!e.shiftKey && (e.keyCode >= 48 && e.keyCode <= 57))
					) {
						return;
				} else {
					e.preventDefault();
				}
			}).on("blur",function() {
				var v = $(this).val();
				v = v.replace(/[A-Za-z$-.\/\\\[\]=_@!#^<>;"]/g, "");

				$(this).val(v);
			});

			$(window).scroll(function() {
				if($(window).scrollTop() > window.searchActionsStart)
					$(".searchForm .searchActions").addClass("fixed");
				else 
					$(".searchForm .searchActions").removeClass("fixed");
			});
		},
		InsertSearchHistoryItem: function(obj) {
			var $item = $(obj).data("item"),
				$ctt = $(obj).parent().parent().find(".colSearch").text(),
				q = $("#iptQuery"),
				shItem = '&#160;<div class="searchHistoryItem" contenteditable="false"  data-toggle="tooltip" data-placement="top" title="'+$ctt+'">#'+$item+'</div> AND&#160;';

			q.append(shItem).focus();
			q.find(".searchHistoryItem").tooltip();
			$(obj).effect("transfer", { to: q.find(".searchHistoryItem:last-child") }, 1000);
			SearchForm.PlaceCaretToEnd(document.getElementById("iptQuery"));
		},
		InsertNewFieldRow: function(t,matrix,container) {
			t = $(t);
			matrix = $(matrix).clone();
			container = $(container);

			var c = t.data("count");

			matrix.attr("id","searchRow-"+c);
			matrix.find(".eraseSearchField").data("rel",c);

			matrix.find(".eraseSearchField").on("click",function(e) {
				e.preventDefault();
				SearchForm.EraseFieldRow(this);
			});

			if(SearchForm.SearchHistory != "") {
				matrix.find("input[name='q[]']").on("focus",function() {
					SearchForm.SearchHistoryFocusIn(this);
				}).on("blur",function() {
					SearchForm.SearchHistoryFocusOut(this);
				});
			}

			matrix.appendTo(container).slideDown("fast");

			matrix.find("textarea.form-control:visible").on("keyup",SearchForm.TextareaAutoHeight).trigger("keyup");
			matrix.find("a.clearIptText").on("click",SearchForm.ClearPrevInput);
			matrix.find(".showTooltip").tooltip({
				container: 'body'
			});

			c = parseInt(c);
			c++;
			t.data("count",c);
		},
		TextareaAutoHeight: function() {
			$(this).css("height","auto");
			$(this).height(this.scrollHeight);
			if(this.value != "")
				$(this).next("a").fadeIn("fast");
			else
				$(this).next("a").fadeOut("fast");
		},
		ClearPrevInput: function() {
			$(this).prev("input,textarea").val("").trigger("keyup");
		},
		EraseFieldRow: function(t) {
			t = $(t);

			var i = t.data("rel");

			$("#searchRow-"+i).slideUp("fast",function() {
				$(this).remove();
			});
		},
		CountCheckedResults: function(t,r) {
			t = $(t);
			var	preSelected = parseInt(t.data("preselected")),
				selResults = parseInt($(r+":checked").length),
				c = preSelected + selResults;

			t.text(c);
			if(c > 0) {
				t.addClass("highlighted");
			} else
				t.removeClass("highlighted");
		},
		SearchHistoryFocusIn: function(t) {
			if(SearchForm.SearchHistory != "") {
				var pos = $(t).offset();

				$("#searchHistory").data("rel",t).css({
					"top": (pos.top+50)+"px",
					"left": (pos.left)+"px"
				}).slideDown("fast");
			}
		},
		SearchHistoryFocusOut: function(t) {
			if(SearchForm.SearchHistory != "") {
				setTimeout(function() {
					$("#searchHistory").slideUp("fast");
				},100);
			}
		},
		SearchHistoryClick: function(txt,t) {
			var txt = $(txt).text();
				txt = txt.substr((txt.indexOf(": ")+2),txt.length);
			
			$(t).val(txt).focus();
		},
		PlaceCaretToEnd: function(el) {
			el.focus();
		    if (typeof window.getSelection != "undefined" && typeof document.createRange != "undefined") {
				var range = document.createRange();
				range.selectNodeContents(el);
				range.collapse(false);
				
				var sel = window.getSelection();
				sel.removeAllRanges();
				sel.addRange(range);
			} else if (typeof document.body.createTextRange != "undefined") {
				var textRange = document.body.createTextRange();
				textRange.moveToElementText(el);
				textRange.collapse(false);
				textRange.select();
		    }
		},
		SubmitForm: function(t) {
			var action = $(".searchForm").attr("action");
			$(".searchForm").attr("action",action+"?filter="+t).submit();
		}
	},
	Article = {
		TopBinder: [],
		Init: function() {
			var articleText = $("#articleText"),
				articleTextP = articleText.offset(),
				articleMenuW = $(".articleMenu").width(),
				p = $(".articleSection",articleText);
			
			/*for(var i = 0, l = p.length; i<l; i++) {
				var c = $("p",p[i]).outerHeight(), r = $(".refList",p[i]), rh = r.outerHeight();
				if(rh > c) {
					r.addClass("outer").css("height",c);
				} 
			}*/

			$(".ref",p).on("mouseenter mouseleave",function(e) {
				var t = $(this),
					s = $(".xref",t),
					d = s.next("span:eq(0)"),
					p = t.position(),
					supHeight = s.outerHeight(),
					supPositionLeft = p.left;

				/*if(c.indexOf(" ") >= 0) {
					c = c.split(" ");
					c = "div." + c.join(",div.");
					b = $(c);
					p = b.parent().find("sup");
				}*/ 
				if(e.type === "mouseenter") {
					d.removeClass("closed").addClass("opened").css({
						"left": supPositionLeft > 300 ? -supPositionLeft/3 : 0
					}).fadeIn("fast");
				} else {
					d.removeClass("opened").addClass("closed");
				}
			});
			/*$(".refList li",p).on("mouseenter mouseleave",function(e) {
				var p = $(this).parent("ul");
				if(e.type === "mouseenter") {
					p.addClass("full");
					$(this).addClass("highlight").find(".opened").fadeIn("fast");
				} else {
					p.removeClass("full");
					$(this).removeClass("highlight").find(".opened").hide();
				}
			});*/

			$(".thumb").on("mouseenter mouseleave",function(e) {
				var p = $(this).parent().parent().find(".preview");
				if(e.type == "mouseenter") {
					p.fadeIn("fast");
				} else if(e.type == "mouseleave") {
					p.fadeOut("fast");
				} 
			});

			$(".ModalTables").on("shown.bs.modal",function() {
				var check = $("table td[colspan], table td[rowspan]",this).length;
				if(check == 0)
					$("table",this).addClass("table-hover");
			});

			$(".collapseTitle").on("click",function() {
				var ctt = $(this).next(),
					ico = $(this).find(".collapseIcon");

				if(ctt.is(":visible")) {
					ctt.slideUp("fast");
					ico.removeClass("opened");
				} else {
					ctt.slideDown("fast");
					ico.addClass("opened");
				}
			});

			$(".expandReduceText").on("click",function(e) {
				e.preventDefault();
				var ref = $("#articleText .ref"),
					txt = $("#articleText .text"),
					s = $(this).data("expandreducetext"),
					tw = $(this).data("defaultwidth");

				if(typeof tw == "undefined") 
					$(this).data("defaultwidth",txt.outerWidth());

				if(s == true) {
					ref.hide();
					txt.outerWidth("100%");
					
					/*
					ref.stop(true,true).fadeOut(100,function() {
						txt.animate({
							width: "100%"
						},200,function() {
							Article.ArticleStructureBuilder();
						});
					});
					*/
					$(this).data("expandreducetext",false);
				} else {
					txt.width("");
					ref.show();
					
					/*
					txt.stop(true,true).animate({
						width: tw
					},200,function() {
						ref.fadeIn(100);
						Article.ArticleStructureBuilder();
					});
					*/
					$(this).data("expandreducetext",true);
				}

				var t = $(window).scrollTop();
				setTimeout(function() {
					Article.ArticleStructureBuilder();
					Article.ArticleStructureSelect(t);	
				},100);
				
			
			});

			$(".articleTxt .xref:not(.big)").on("click",function() {
				var c = $(this).text(),
					d = $(".ref-list");

				if(c.indexOf(",") == -1) {
					parseInt(c);
					c--;
				} else {
					c = c.split(",");
					c = c[0];

					parseInt(c);
					c--;
				}
			});

			articleTextP.top = articleTextP.top - 25;
			var articleTextH = articleText.outerHeight(),
				articleMenuH = $(".articleMenu").height();

			window.setTimeout(function() {
				articleMenuH = $(".articleMenu").height();
			},200);

			$(window).scroll(function() {
				var t = $(window).scrollTop();
				if(
					t > articleTextP.top
				) {
					$(".articleMenu").addClass("fixed").width(articleMenuW);	
					if(t > (articleTextH + articleTextP.top - articleMenuH - 46)) {
						$(".articleMenu").addClass("fixedBottom");
					} else {
						$(".articleMenu").removeClass("fixedBottom");
					}
				} else 
					$(".articleMenu").removeClass("fixed");

				Article.ArticleStructureSelect(t);

				$(".alternativeHeader").stop(false,false);
			});

			$("#ModalTablesFigures #tables a").on("click",function(){
				$("#ModalTablesFigures").modal('toggle');
			});

			if(window.location.hash != "") {
				var hash = window.location.hash,
					scrollY = window.scrollY;
				
				$(hash).modal("toggle").on("hidden.bs.modal",function() {
        			window.location.hash = '';
        			
        			$("body,html").scrollTop(scrollY);
    			});
			}

			$("[data-toggle='modal']").on("click",function() {
				var t = $(this),
					target = t.data("target"),
					scrollY = window.scrollY;

				if(target != "undefined" || target != "")
					window.location.hash = target;

				$(target).on("hidden.bs.modal",function () {
	        		window.location.hash = '';
	        		
	        		$("body,html").scrollTop(scrollY);
	    		});
			});

			var downloadOpt = $(".downloadOptions li.group"),
				downloadOptW = 100/downloadOpt.length;
		
			downloadOpt.css("width",downloadOptW+"%");

			Article.ArticleStructureBuilder();
		},
		ArticleStructureBuilder: function() {
			var structure = $(".articleMenu"),
				content = $("#articleText .articleSection"),
				idx = 0,
				ctt = '';

			Article.TopBinder = [];

			content.each(function() {
				var t = $(this).data("anchor"),
					h = $(this).find("h1"),
					offset = $(this).offset();

				if(idx == 0)
					Article.TopBinder.push(0);
				else
					Article.TopBinder.push(offset.top);

				if(typeof t == "undefined") return true;

				ctt += '<li '+(idx == 0 ? 'class="selected"' : '')+'>';
				ctt += '	<a href="#articleSection'+idx+'">'+t+'</a>';

				if(h.length > 1) {
					var iidx = 0;
					ctt += '<ul>';
					h.each(function() {
						var ooffset = $(this).offset();
						Article.TopBinder.push(ooffset.top);

						ctt += '<li>';
						ctt += '	<a href="#as'+idx+'-heading'+iidx+'">'+$(this).text()+'</a>';
						ctt += '</li>';

						iidx++;
					});
					ctt += '</ul>';
				}
				ctt += '</li>';

				idx++;
			});

			structure.html(ctt);

			$("a",structure).on("click",function(e) {
				e.preventDefault();

				var d = $(this).attr("href");
				d = d.replace("#","");

				var p = $("a[name="+d+"]").offset();

				$("html,body").animate({
					scrollTop: (p.top-60)
				},500);
			});
		},
		ArticleStructureSelect: function(pos) {
			var structure = $(".articleMenu"),
				idx = 0;

			for(var i=0,l=Article.TopBinder.length;i<l;i++) {
				if(pos <= (Article.TopBinder[i]-100)) {
					structure.find("li").removeClass("selected");
					structure.find("li:eq("+(i-1)+")").addClass("selected");
					break;
				}
			}

		}
	},
	Collection = {
		Init: function() {
			var start = $(".collectionListStart");

			start.each(function() {
				var t = $(this),
					method = t.data("method"),
					rp = t.data("perpage"),
					labels = t.data("labels"),
					search = $(".collectionSearch",t),
					download = $(".collectionListDownloadXLS,.collectionListDownloadCSV",t),
					loading = $(".collectionListLoading",t),
					scroll = false,
					param = "";
			
				window.timer;

				if(typeof t.data("action") !== "undefined") {
					labels = labels.split(";");
					search.val("");

					$(".collectionCurrentPage",t).val("1");

					if(method == "alphabetic") {
						param = "method=alphabetic&rp="+rp;
						scroll = true;
					} else if(method == "theme") {
						var param = "method=theme";
					} else if(method == "publisher") {
						var param = "method=publisher";
					} else if(method == "collection") {
						var param = "method=collection";
					}
					
					Collection.JournalListFinder(param,loading,t,labels,true,scroll);

				}

				search.on("keyup change",function() {
					var tt = $(this),
						param = "method="+method+"&rp="+rp,
						duringKeyChange = true;

					clearTimeout(window.timer);
					window.timer = setTimeout(function() {
						var v = tt.val();
						param += "&query="+v
						$(".collectionCurrentPage",t).val("1");

						Collection.JournalListFinder(param,loading,t,labels,true,true);
						duringKeyChange = false;
						
					},300);
				});

				download.on("click",function(e) {
					e.preventDefault();

					var output = $(this).is(".collectionListDownloadXLS") ? "xls" : "csv",
						action = t.data("action"),
						param = "?method=alphabetic"+"&output="+output+(search.val() != "" ? "&query="+search.val() : "");

					window.open(action+param);
				});
			});	
		},
		JournalListFinder: function(param,loading,container,labels,empty,scroll,callback,htmlFill) {
			var currentPage = $(".collectionCurrentPage",container),
				totalPages = $(".collectionTotalPages",container),
				totalInfo = $(".collectionListTotalInfo",container),
				action = $(container).data("action");

			if(typeof htmlFill != "undefined")
				loading = htmlFill.next(".collectionListLoading");

			if(typeof empty === "undefined") empty = false;

			param += "&page="+currentPage.val();

			$.ajax({
				url: action,
				type: "POST",
				data: param,
				dataType: "json",
				beforeSend: function () {
					loading.show();
				}
			}).done(function(data) {
				loading.hide();
				if(typeof data.journalList !== "undefined") {
					if(param.indexOf("&theme=") == -1 && param.indexOf("&publisher=") == -1) {
						totalInfo.html(labels[11].replace("{total}",data.total));
						totalPages.val(data.totalPages);
					}

					var ctt = Collection.JournalListFill(data,labels);
					if(typeof htmlFill != "undefined") {
						if(empty) $(htmlFill).find("tbody").empty();
						$(htmlFill).find("tbody").append(ctt).find(".showTooltip").tooltip({
							container: 'body'
						});
					} else {
						if(empty) $(container).find("tbody").empty();
						$(container).find("tbody").append(ctt).find(".showTooltip").tooltip({
							container: 'body'
						});
					}

					if(scroll) Collection.ScrollEvents(container,loading,labels);
				}
				if(typeof data.themeList !== "undefined") {
					totalInfo.html(labels[11].replace("{total}",data.total).replace("{totalTheme}",data.totalThemes));
					var ctt = Collection.ThemeListFill(data,labels,container.attr("id"));

					if(typeof htmlFill != "undefined") {
						if(empty) $(htmlFill).find("tbody").empty();
						$(htmlFill).find("tbody").append(ctt).find(".showTooltip").tooltip({
							container: 'body'
						});
					} else {
						if(empty) $(container).find("tbody").empty();
						$(container).find("tbody").append(ctt).find(".showTooltip").tooltip({
							container: 'body'
						});
					}
					Collection.CollapseEvents(container,labels);
				}
				if(typeof data.publisherList !== "undefined") {
					totalInfo.html(labels[11].replace("{total}",data.total).replace("{totalPublisher}",data.totalPublisher));
					var ctt = Collection.PublisherListFill(data,labels,container.attr("id"));

					if(typeof htmlFill != "undefined") {
						if(empty) $(htmlFill).find("tbody").empty();
						$(htmlFill).find("tbody").append(ctt).find(".showTooltip").tooltip({
							container: 'body'
						});
					} else {
						if(empty) $(container).find("tbody").empty();
						$(container).find("tbody").append(ctt).find(".showTooltip").tooltip({
							container: 'body'
						});
					}
					Collection.CollapseEvents(container,labels);
				}
				if(typeof data.collectionList !== "undefined") {
					totalInfo.html(labels[11].replace("{total}",data.total).replace("{totalCollection}",data.totalCollection));
					var ctt = Collection.CollectionListFill(data,labels,container.attr("id"));

					if(typeof htmlFill != "undefined") {
						if(empty) $(htmlFill).find("tbody").empty();
						$(htmlFill).find("tbody").append(ctt).find(".showTooltip").tooltip({
							container: 'body'
						});
					} else {
						if(empty) $(container).find("tbody").empty();
						$(container).find("tbody").append(ctt).find(".showTooltip").tooltip({
							container: 'body'
						});
					}
				}

				if(typeof callback !== "undefined") {
					eval(callback);
				}

			}).error(function(data) {
				loading.hide();
				console.warn("Error #001: Error found on loading journal list");
			});
		},
		JournalListFill: function(list,labels) {
			var ctt = "";

			for(var i=0,l=list.journalList.length;i<l;i++) {
				var c = list.journalList[i];
				c.Last = c.Last.split(";");
				c.Publisher = c.Publisher.split(";");

				ctt += 	'\
						<tr>\
							<td class="actions">\
								<a href="'+c.Links[0]+'" class="showTooltip" title="'+labels[5]+'"><span class="glyphBtn home"></span></a> \
								<a href="'+c.Links[1]+'" class="showTooltip" title="'+labels[6]+'"><span class="glyphBtn submission"></span></a> \
								<a href="'+c.Links[2]+'" class="showTooltip" title="'+labels[7]+'"><span class="glyphBtn authorInstructions"></span></a> \
								<a href="'+c.Links[3]+'" class="showTooltip" title="'+labels[8]+'"><span class="glyphBtn about"></span></a> \
								<a href="'+c.Links[4]+'" class="showTooltip" title="'+labels[9]+'"><span class="glyphBtn contact"></span></a> \
							</td>\
							<td>\
								<a href="'+c.Links[0]+'" class="collectionLink '+(c.Active == false ? 'disabled' : '')+'">\
									<strong class="journalTitle">'+c.Journal+'</strong>,\
									<strong class="journalIssues">'+c.Issues+' '+labels[0]+'</strong>,\
									'+labels[1]+'\
									'+(c.Last[0] != '' ? '<span class="journalLastVolume"><em>'+labels[2]+'</em> '+c.Last[0]+'</span>' : '')+'\
									'+(c.Last[1] != '' ? '<span class="journalLastNumber"><em>'+labels[3]+'</em> '+c.Last[1]+'</span>' : '')+'\
									'+(c.Last[2] != '' ? '<span class="journalLastSuppl"><em>'+labels[4]+'</em> '+c.Last[2]+'</span>' : '')+'\
									- \
									'+(c.Last[3] != '' ? '<span class="journalLastPubDate">'+c.Last[3]+'</span>' : '')+' \
									'+(c.Active == false ? labels[10] : '')+' \
								</a>\
							</td>';
							if(c.Collection) {
								ctt += ' \
								<td>\
									<span class="glyphFlags '+c.Collection+'"></span> '+Collection.PortalCollectionNameFill(c.Collection)+'\
								</td>';
							}
							ctt += '\
						</tr>';
			}

			return ctt;
		},
		PortalCollectionNameFill: function(id) {
			var rtn = "";
			if(window.collections) {
				for (var i = 0,l=window.collections.length; i < l;i++) {
					if(window.collections[i].id==id)
						rtn = window.collections[i].name;
				}
			}
			return rtn;
		},
		ThemeListFill: function(data,labels,id) {
			var ctt = '	<tr>\
							<td class="collapseContainer">';
			for(var i=0,l=data.themeList.length;i<l;i++) {
				ctt += '		<div class="themeItem">\
									<a href="javascript:;" id="'+id+'-collapseTitle-'+i+'" \
									class="collapseTitleBlock '+(typeof data.themeList[i].journalList === "undefined" ? 'closed' : '')+'" data-id="'+data.themeList[i].id+'">\
										<strong>'+data.themeList[i].Area+'</strong>\
										('+data.themeList[i].Total+')\
									</a> \
									<div class="collapseContent" id="'+id+'-collapseContent-'+i+'" '+(typeof data.themeList[i].journalList === "undefined" ? 'style="display: none;"' : '')+'>';
				for(var x=0,lx=data.themeList[i].SubAreas.length;x<lx;x++) {
					ctt += '			<a href="javascript:;" id="'+id+'-collapseTitle-'+i+'-sub-'+x+'" \
											class="collapseTitle '+(typeof data.themeList[i].SubAreas[x].journalList === "undefined" ? 'closed' : '')+'" data-id="'+data.themeList[i].SubAreas[x].id+'">\
											<strong>'+data.themeList[i].SubAreas[x].Area+'</strong>\
												('+data.themeList[i].SubAreas[x].Total+')\
										</a>\
										<div class="collapseContent" id="'+id+'-collapseContent-'+i+'-sub-'+x+'" '+(typeof data.themeList[i].SubAreas[x].journalList === "undefined" ? 'style="display: none;"' : '')+'>\
											<table> \
												<thead> \
													<tr> \
														<th class="actions"></th> \
														<th>'+labels[12]+'</th> \
														'+(data.collection ? "<th class='flags'>"+labels[14]+"</th>" : "")+' \
													</tr> \
												</thead> \
												<tbody>';
					if(typeof data.themeList[i].SubAreas[x].journalList !== "undefined")
						ctt += Collection.JournalListFill(data.themeList[i].SubAreas[x],labels);

				ctt += '						</tbody>\
											</table> \
										</div> \
										<div class="collapseContent collectionListLoading" style="display: none;"></div>\
										';
				}
				ctt += '			</div>';
			}

			ctt += '		</td>\
						</tr>';

			return ctt;
		},
		PublisherListFill: function(data,labels,id) {
			var ctt = '	<tr>\
							<td class="collapseContainer">';

			for(var i=0,l=data.publisherList.length;i<l;i++) {
				ctt += '		<div class="themeItem">\
									<a href="javascript:;" id="'+id+'-collapseTitle-'+i+'" class="collapseTitle '+(typeof data.publisherList[i].journalList === "undefined" ? 'closed' : '')+'"><strong>'+data.publisherList[i].Publisher+'</strong> ('+data.publisherList[i].Total+')</a> \
									<div class="collapseContent" id="'+id+'-collapseContent-'+i+'" '+(typeof data.publisherList[i].journalList === "undefined" ? 'style="display: none;"' : '')+'> \
										<table> \
											<thead> \
												<tr> \
													<th class="actions"></th> \
													<th>'+labels[12]+'</th> \
													'+(data.collection ? "<th class='flags'>"+labels[14]+"</th>" : "")+' \
												</tr> \
											</thead> \
											<tbody>';
				if(typeof data.publisherList[i].journalList !== "undefined")
					ctt += Collection.JournalListFill(data.publisherList[i],labels);

				ctt += '					</tbody> \
										</table> \
									</div> \
									<div class="collapseContent collectionListLoading" style="display: none;"></div>\
								</div>';
			}

			ctt += '		</td>\
						</tr>';

			return ctt;
		},
		CollectionListFill: function(data,labels,id) {
			var ctt = '	<tr>\
							<td class="collapseContainer">';

			for(var i=0,l=data.collectionList.length;i<l;i++) {
				ctt += '		<div class="themeItem collectionBold">\
								<a href="'+data.collectionList[i].link+'" class="collapseTitle closed" target="_blank"><span class="glyphFlags '+data.collectionList[i].id+'"></span> <strong>'+data.collectionList[i].name+'</strong> ('+data.collectionList[i].Total+')</a> \
							</div>';
			}

			ctt += '		</td>\
						</tr>';

			return ctt;

		},
		ScrollEvents: function(container,loading,labels) {
			var currentPage = $(".collectionCurrentPage",container),
				totalPages = $(".collectionTotalPages",container),
				query = $(".collectionSearch",container),
				rp = $(container).data("perpage"),
				method = $(container).data("method"),
				param = "method=alphabetic&rp="+rp+(query.val() != "" ? "&query="+query.val() : "");

			$(window).off("scroll").on("scroll",function() {
				if(currentPage.val() < totalPages.val()) {
					$("footer").hide();
					if($(window).scrollTop() + $(window).height() == $(document).height()) {
						var page = parseInt(currentPage.val());
						page++;
						currentPage.val(page);
						param += "&page="+page;

						Collection.JournalListFinder(param,loading,container,labels,false,false);
					}
				} else {
					$("footer").show();		
				}
			});
		},
		CollapseEvents: function(container,labels) {
			var method = $(container).data("method"),
				query = $(".collectionSearch",container),
				param = "method=alphabetic"+(query.val() != "" ? "&query="+query.val() : ""),
				collapseTitle = $(".collapseTitle,.collapseTitleBlock",container);

			collapseTitle.on("click",function() {
				var t = $(this),
					p = t.parent(),
					loading = p.find(".collectionListLoading"),
					content = t.next(".collapseContent"),
					cached = content.find("table tbody tr").length;

				if(content.is(":visible")) {
					content.slideUp("fast");
					$(this).addClass("closed");
				} else {
					if(t.is(".collapseTitleBlock")) {
						content.slideDown("fast");
						loading.hide();
						$(this).removeClass("closed");
					} else {
						if(cached == 0) {
							var str = typeof t.data("id") != "undefined" ? t.data("id") : $("strong",this).text();
							param += "&"+method+"="+str;
							Collection.JournalListFinder(param,loading,container,labels,true,false,"Collection.CollapseOpen('#"+content.attr("id")+"','#"+t.attr("id")+"')",content);
						} else {
							content.slideDown("fast");
							loading.hide();
							$(this).removeClass("closed");
						}	
					}
					
				}
			});
		},
		CollapseOpen: function(content,title) {
			$(content).slideDown("fast");
			$(title).removeClass("closed");
		}
	};

var Validator = {
	MultipleEmails: function(val,delimiter) {
		var delimiter = delimiter || ';';
		var filter  = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
		var error = true;

		var aEmails = val.split(delimiter);
		
		for(var i = 0; i < aEmails.length; i++) {
			aEmails[i] = aEmails[i].trim();
			if(aEmails[i] == '' || filter.test(aEmails[i]) == false)
				error = false;
		}

		return error;
	}
};

var Cookie = {
	Get: function(cookieName,path) {
		if(typeof path === "undefined") path = "";
		else path = path+"/";
		cookieName = path+cookieName;
		if (document.cookie.length > 0) {
	        c_start = document.cookie.indexOf(cookieName + "=");
	        if (c_start != -1) {
	            c_start = c_start + cookieName.length + 1;
	            c_end = document.cookie.indexOf(";", c_start);
	            if (c_end == -1) {
	                c_end = document.cookie.length;
	            }
	            return unescape(document.cookie.substring(c_start, c_end));
	        }
	    }
	    return "";
	},
	Set: function(cookieName, value, days, path) {
		var expires;
		if(typeof days !== "undefined") {
	        var date = new Date();
	        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
	        expires = "; expires=" + date.toGMTString();
	    } else
	    	expires = "";
	    if(typeof path === "undefined") path = "";
	    else path = path + "/";
	    
	    if(Cookie.Get(cookieName) != "") {
	    	document.cookie = path+cookieName + "=" + value + "expires=Thu, 01 Jan 1970 00:00:01 GMT" + "; path=/";
	    }
	    document.cookie = path+cookieName + "=" + value + expires + "; path=/";
	}
};

$(function() {
	Portal.Init();
	
	if($("form.searchForm").length)
		SearchForm.Init();

	if($("#articleText").length)
		Article.Init();

	if($("body.collection, body.portal").length)
		Collection.Init();

	if($("body.portal.home").length)
		$('.portal .twitter').twittie({
			dateFormat: '%b. %d, %Y',
			template: '<span>{{date}}</span><div class="info">{{tweet}}</div><div class="tShare"><a href="https://twitter.com/intent/tweet?in_reply_to={{twitterId}}" target="_blank" class="showTooltip" data-placement="top" title="" data-original-title="Compartilhar no Twitter"><span class="glyphBtn tShare"></span></a><a href="https://twitter.com/intent/retweet?tweet_id={{twitterId}}" target="_blank" class="showTooltip" data-placement="top" title="" data-original-title="Atualizar"><span class="glyphBtn tReload"></span></a><a href="https://twitter.com/intent/favorite?tweet_id={{twitterId}}"  target="_blank" class="showTooltip" data-placement="top" title="" data-original-title="Adicionar as favoritos no Twitter"><span class="glyphBtn tFavorite"></span></a></div>',
			count: 3,
			loadingText: 'Carregando...',
			dateFormat: '%d de %B',
		});

	if($(".portal .collectionList").length)
		var hash = window.location.hash;
		$('.portal .collection .nav-tabs a[href="' + hash + '"]').tab('show');

});

