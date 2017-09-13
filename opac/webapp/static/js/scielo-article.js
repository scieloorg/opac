var Article = {
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

		$(".ModalTables").on("shown.bs.modal",function() {
			var modalBody = $(".modal-body",this),
				table = $("table",modalBody),
				modalBodyWidth = modalBody.outerWidth(),
				tableWidth = table.outerWidth();

			if(!modalBody.is("cached")) {
				table.addClass("table");

				if(tableWidth > modalBodyWidth) {
					table.addClass("autoWidth");
				} else {
					table.removeClass("autoWidth");
				}
			}

			modalBody.addClass("cached");
		});

		$(".ref").on("mouseenter mouseleave",function(e) {
			var t = $(this),
				s = $(".xref",t),
				d = s.next("span:eq(0)"),
				p = t.position(),
				supHeight = s.outerHeight(),
				supPositionLeft = p.left,
				li = t.closest("li");

			/*if(c.indexOf(" ") >= 0) {
				c = c.split(" ");
				c = "div." + c.join(",div.");
				b = $(c);
				p = b.parent().find("sup");
			}*/
			if(e.type === "mouseenter") {
				if(li.length > 0)
					li.addClass("zindexFix");

				d.removeClass("closed").addClass("opened").css({
					"left": supPositionLeft > 300 ? -supPositionLeft/3 : 0
				}).fadeIn("fast");
			} else {
				if(li.length > 0)
					li.removeClass("zindexFix");

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

		Article.ArticleStructureBuilder();

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

		/*$("#ModalTablesFigures #tables a").on("click",function(){
			$("#ModalTablesFigures").modal('toggle');
		});*/

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

		Article.fechaAutores();

		// Global variable shared on mouseenter event and clipboard
		var hasEncodedTheURL = false;

		$('.short-link').mouseenter(function(event) {

			// Verify if the ajax request has already been made
			if(!hasEncodedTheURL) {

				var urlAtual = window.location.href;
				// var urlAtual = "http://www.scielo.br";
	        	$.ajax({
		            type: "GET",
		            async: false,
		            url: 'http://ref.scielo.org/api/v1/shorten',
		            data: 'url=' + encodeURI(urlAtual),
		            dataType: "jsonp",
		            success: function(data) {
		            	result = data;
		            	hasEncodedTheURL = true;
	            	}
	            	//error:
	        	});
			}

	    });

		var clipboard = new Clipboard('.short-link', {
        text: function(trigger) {
            	return result;
            }
        });

	    clipboard.on('success', function(e) {

	        console.log('Sucess: ' + e);

        	var t = $(e.trigger);
			t.addClass("copyFeedback");

			setTimeout(function() {
				t.removeClass("copyFeedback");
			},2000);
	    });

	    clipboard.on('error', function(e) {
	    	console.log('Error: ' + e);

	    	var t = $(e.trigger);
			t.addClass("copyFeedbackError");

			setTimeout(function() {
				t.removeClass("copyFeedbackError");
			},2000);
	    });

	},


	ArticleStructureBuilder: function() {
		var structure = $(".articleMenu"),
			content = $("#articleText .articleSection"),
			idx = 0,
			ctt = '';

		Article.TopBinder = [];

		content.each(function() {
			var t = $(this).data("anchor"),
				h = $(this).find(".articleSectionTitle"),
				offset = $(this).offset();

			if($(this).find("a[name='articleSection"+idx+"']").length == 0) {
				$(this).prepend("<a name='articleSection"+idx+"'></a>");
			}

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

					if($(this).prev("a[name='as"+idx+"-heading"+iidx+"']").length == 0) {
						$(this).before("<a name='as"+idx+"-heading"+iidx+"'></a>");
					}

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

		//ctt+='<li class="link-to-top"><a href="#top"><span class="circle"><span class="sci-ico-top"></span></span> Ir para o topo</a></li>';

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
			if(i == l-1 && pos >= Article.TopBinder[i]-100) {
				structure.find("li").removeClass("selected");
				structure.find("li:eq("+i+")").addClass("selected");
				break;
			} else {
				if(pos <= (Article.TopBinder[i]-100)) {
					structure.find("li").removeClass("selected");
					structure.find("li:eq("+(i-1)+")").addClass("selected");
					break;
				}
			}

		}

	},


	Bindings: function(ctn) {
		if(typeof ctn == "undefined") ctn = ".article";
	},

	fechaAutores: function(){

		var autoresGrupo = $(".contribGroup");
		var autores = $(".contribGroup .dropdown");
		var qtdAutores = autores.length;

		if(qtdAutores >= 10) {

			var AuthorsQTDTooltip = null;

			var btnSobre = $(".outlineFadeLink");
			var primeiro = autores[0];
			var ultimo = autores[qtdAutores -1];

			// Code added to control authors quantity tooltip
			var authorsQTDToShowInsideBracktes = qtdAutores - 2;

			var linkToggleOn = $('<a data-toggle="tooltip" data-placement="top" title="+'+authorsQTDToShowInsideBracktes+'"></a>');

			linkToggleOn.text("[...]");
			//style
			linkToggleOn.css({ padding : "10px" , cursor : "pointer" });

			var boxToggleOff = $('<div></div>');
			var linkToggleOff = $('<a></a>');

			linkToggleOff.addClass("btn-fechar");

			var spanOff = $('<span></span>');
			spanOff.addClass("sci-ico-floatingMenuClose");

			linkToggleOff.append(spanOff);
			boxToggleOff.append(linkToggleOff);

			var autoresResumo = $('<div></div>');
			autoresResumo.append(primeiro);
			autoresResumo.append(linkToggleOn);
			autoresResumo.append(ultimo);
			autoresResumo.append(btnSobre);

			//substitui o conteudo pelo resumo
			autoresGrupo.text("");
			autoresGrupo.append(autoresResumo);

			linkToggleOn.on("click",function() {
				AuthorsQTDTooltip.tooltip('disable')

				autoresGrupo.textContent = "";
				for (var i = 0; i < qtdAutores; i++){
					autoresGrupo.append(autores[i]);
				}

				autoresGrupo.append(btnSobre);
				autoresGrupo.append(boxToggleOff);
			});

			linkToggleOff.on("click",function() {
				AuthorsQTDTooltip.tooltip('enable');

				Article.fechaAutores();
			});

			// Initialize tooltip
			AuthorsQTDTooltip = $('[data-toggle="tooltip"]').tooltip();
		}
		autoresGrupo.css("opacity","1");

	}
};

$(function() {

	if($("body.article").length)
		Article.Init();
});
