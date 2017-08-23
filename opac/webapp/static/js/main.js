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
						top: "-65px"
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
					ctt = $(".collapse-content");
 
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

			if(typeof Clipboard != "undefined") {
				var clipboard = new Clipboard('.copyLink');

				clipboard.on('success', function(e) {
					var t = $(e.trigger);

					t.addClass("copyFeedback");
					
					setTimeout(function() {
						t.removeClass("copyFeedback");
					},2000);

				    //e.clearSelection();
				}).on('error',function(e) {
					console.error('Action:', e.action);
    				console.error('Trigger:', e.trigger);
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

				wrapper.stop(false,true).animate({
					left: "+="+itemProps.w
				},100,function() {
					var nLeft = wrapper.css("left") == "auto" ? 0 : parseInt(wrapper.css("left"));
					if(nLeft == 0) 
						prev.hide();
				});
				next.show();
			
			});

			next.off().on("click",function(e) {
				e.preventDefault();
				var left = wrapper.css("left") == "auto" ? 0 : parseInt(wrapper.css("left"));

				wrapper.stop(false, true).animate({
					left: "-="+itemProps.w
				},100,function() {
					var nLeft = wrapper.css("left") == "auto" ? 0 : parseInt(wrapper.css("left"));
					if(nLeft <= -(wrapperWidth-containerWidth)) 
						next.hide();
				});
				prev.show();
			});

		}
	},
	SearchForm = {
		SearchHistory: "",
		Init: function() {
			var p = ".searchForm";

			$("input.trigger").off("click").on("click",function() {
				var cmd = $(this).data("rel");
				eval(cmd);
			});

			$(p).on("submit",function(e) {
				e.preventDefault();

				var expr = $("*[name='q[]']",p),
					connector = $("select[name='bool[]']",p),
					idx = $("select[name='index[]']",p),
					searchQuery = "";

				for(var i=0,l=expr.length;i<l;i++) {
					if ( $(expr[i]).attr('id') == 'iptQuery' ){
						var v = $(expr[i]).text();
					}else{
						var v = $(expr[i]).val();
					}
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

				var where = $("input[name='collection']:checked",p).val();
				if (where !== undefined && where != ''){
					// check if filter by collection is not defined
					if ( $("input[name='filter[in][]']").length == 0){
						initial_filter_in = $('<input>').attr({type: 'hidden', name: 'filter[in][]', value:where}).appendTo('#searchForm');
					}
				}

				var search_by_year = $("input[name='publicationYear']:checked",p).val();
				if (search_by_year == "1"){
					var pub_year_start =  $("select[name='y1Start'] option:selected",p).val();
					if (pub_year_start != ''){
						searchQuery += ' AND publication_year:[' + pub_year_start + ' TO *]';
					}
				} else if(search_by_year == "2"){
					var pub_year_start =  $("select[name='y2Start'] option:selected",p).val();
					var pub_year_end =  $("select[name='y2End'] option:selected",p).val();
					if (pub_year_start != '' && pub_year_end != ''){
						searchQuery += ' AND publication_year:[' + pub_year_start + ' TO ' + pub_year_end + ']';
					}
				}

				// remove boolean operators from begining or end of query
				searchQuery = searchQuery.replace(/^AND|AND$|^OR|OR$/g, "");

				if (searchQuery == ''){
					searchQuery = '*';
				}
				searchQuery = $.trim(searchQuery);

				var total = 0;
				var form = document.searchForm;
				var form_action = form.action;
				var form_params = 'q=' + searchQuery;

				var searchForm = document.searchForm;
				$("input[name='q']").val(searchQuery);
				searchForm.submit();

				return true;
			});

			//$("textarea.form-control:visible",p);
			$("textarea.form-control",p).on("keyup",SearchForm.TextareaAutoHeight).trigger("keyup").on('keypress', function(e) {
				var t = $(this),
					v = this.value;

				if(v != "") 
					t.next().fadeIn("fast");
				else 
					t.next().fadeOut("fast");
				
				if(e.which == 13 && ! e.shiftKey) {
					$(p).submit();
				}
			});

			$("a.clearIptText",p).on("click",SearchForm.ClearPrevInput);
			
			$(".newSearchField",p).on("click",function(e) {
				e.preventDefault();
				SearchForm.InsertNewFieldRow(this,"#searchRow-matriz .searchRow",".searchForm .searchRow-container");
			});

			$(".articleAction, .searchHistoryItem, .colActions .searchHistoryIcon",p).tooltip();

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
	Collection = {
		Init: function() {
			var start = $(".collectionListStart");

			start.each(function() {
				var t = $(this),
					method = t.data("method"),
					rp = t.data("perpage"),
					labels = t.data("labels"),
					search = $(".collectionSearch",t),
					//download = $(".collectionListDownloadXLS,.collectionListDownloadCSV",t),
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

				/*
				download.on("click",function(e) {
					e.preventDefault();

					var output = $(this).is(".collectionListDownloadXLS") ? "xls" : "csv",
						action = t.data("action"),
						param = "?method=alphabetic"+"&output="+output+(search.val() != "" ? "&query="+search.val() : "");

					window.open(action+param);
				});
				*/
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
								<a href="'+c.Links[5]+'" class="showTooltip" title="'+labels[12]+'"><span class="glyphBtn editorial"></span></a> \
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
	}

	Journal = {
		Init: function() {
			
			$("#sortBy").change(function(){
				$("#sortBy option:selected" ).each(function() {
      				var str = "";
      				str += $(this).val() + " ";
      				Journal.publicationSort(str);
    			});
			})
			
		},
		Bindings: function(ctn) {
			if(typeof ctn == "undefined") ctn = ".journal";
		},
		publicationSort: function(el){

			var elemento = el;
			var valor = $("#"+ elemento +" option:selected").val();

			var listas = $(".issueIndent>ul.articles");
			var qtdlista = listas.length;
			
			for(var t=0; t<=qtdlista; t++){
				
				var ul = listas[t];
				var li = $(ul).children();

				if(valor == "YEAR_ASC"){
					$(li).sort(function(a,b){
		    			return new Date($(a).attr("data-date")) < new Date($(b).attr("data-date"));
					}).each(function(){
						$(ul).prepend(this);
					})
				}else{
					$(li).sort(function(a,b){
		    			return new Date($(a).attr("data-date")) > new Date($(b).attr("data-date"));
					}).each(function(){
						$(ul).prepend(this);
					})					
				}
			}
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
	
	if($(".searchForm").length)
		SearchForm.Init();

	if($("body.journal").length)
		Journal.Init();

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

