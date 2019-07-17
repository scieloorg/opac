var Article = {
	TopBinder: [],
	Init: function() {

		Article.SetScreen();

		var articleText = $("#articleText"),
			articleTextP = articleText.offset(),
			articleMenuW = $(".articleMenu").width(),
			p = $(".articleSection",articleText);

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


		var RefToolTip = {

			open: function(t) {

				var s = $(".xref",t),
					d = s.next("span:eq(0)"),
					p = t.position(),
					supHeight = s.outerHeight(),
					supPositionLeft = p.left,
					li = t.closest("li");

				if(li.length > 0)
					li.addClass("zindexFix");

				d.removeClass("closed").addClass("opened").css({
					"left": (supPositionLeft > 300) ? (-supPositionLeft/3) : 0
				}).fadeIn("fast");

			},
			close: function(t) {

				var s = $(".xref",t),
					d = s.next("span:eq(0)"),
					li = t.closest("li");

				if(li.length > 0)
					li.removeClass("zindexFix");

				d.removeClass("opened").addClass("closed");
			}
		};

		// Tablet or Mobile
		if(Article.IsTablet || Article.IsMobile) {

			var isTooltipOpen = false;
			var actualOpened = null;

			$('html').on('touchstart', function(e) {

				$(".ref").each(function() {

					var t = $(this);
					RefToolTip.close(t);

					isTooltipOpen = false;
				});

			});

			$(".ref").on('touchstart',function(e) {
			    e.stopPropagation();

			  	var t = $(this);

			  	if(actualOpened !== null && t.get(0) === actualOpened.get(0)) {

			  		if(!isTooltipOpen) {

						actualOpened = t;

						RefToolTip.open(t);
		  			    isTooltipOpen = true;

		  			/*
					} else if(isTooltipOpen) {
						//Fecha tooltip ao clicar sobre ele
						RefToolTip.close(t);
						isTooltipOpen = false;
					*/
					}

			  	} else {

			  		if(actualOpened !== null) RefToolTip.close(actualOpened);

					actualOpened = t;

					RefToolTip.open(t);
		  			isTooltipOpen = true;
			  	}

			});

		    $("ul.floatingMenuMobile").on('click', function() {

		    	$(this).find('.fm-button-child').each(function() {
		    		$(this).addClass('tooltip-mobile-on');
		    	});

		    });



		// Desktop
		} else {

			$(".ref").on("mouseenter mouseleave",function(e) {
				e.preventDefault();

				var t = $(this);

				if(e.type === "mouseenter") {

					RefToolTip.open(t);

				} else {

					RefToolTip.close(t);
				}
			});
		}


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

				$(this).data("expandreducetext",false);
			} else {
				txt.width("");
				ref.show();

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

			hbodyText = $(".articleTxt").height();
			vbodyText = hbodyText + 100  + "px";
			vbodyTextMobile = hbodyText + 150  + "px";

		window.setTimeout(function() {
			articleMenuH = $(".articleMenu").height();
		},200);

		if(hbodyText < 750){
			$(".floatingMenu, .floatingMenuItem, .floatingMenuMobile").css({
				"bottom": "auto",
				"top": Article.IsTablet ? vbodyTextMobile : vbodyText
			});
		}
		window.setTimeout(function() {
			$(".floatingMenu, .floatingMenuItem, .floatingMenuMobile").css({
				"opacity": "1"
			});
		},200);

		$(window).scroll(function() {
			var t = $(window).scrollTop();

			if(Article.isScrolledIntoView('.floatingMenuCtt')){

				$('.floatingMenuItem').css({position: 'absolute'});
				$('.floatingMenu').css({position: 'absolute'});

			}else{

				$('.floatingMenuItem').css({position: 'fixed'});
				$('.floatingMenu').css({position: 'fixed'});
			}

			if(t > articleTextP.top) {

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

				if(urlAtual.indexOf('localhost') !== -1) { // Localhost
					var urlAtual = "http://www.scielo.br";
				}

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

	    $("ul.floatingMenuMobile").on('click', function() {

	    	$(this).find('.fm-button-child').each(function() {
	    		$(this).addClass('tooltip-mobile-on');
	    	});
	    });

	    var isFloatingMenuMobileClosed = true;

	    $("ul.floatingMenuMobile").on('focusout click', function(e) {

	    	if(isFloatingMenuMobileClosed) { // Open menu

	    		if(e.type === 'focusout') {
	    			return;
	    		}

	    		isFloatingMenuMobileClosed = false;
	    		$(this).find('.fm-list').children('li').removeAttr('style');
	    		$(this).find('.fm-button-main').addClass('fm-button-main-mobile-open');

	    	} else {

	    		isFloatingMenuMobileClosed = true; // Close menu
	    		
	    		$(this).find('.fm-list').children('li').css({'opacity': 0});
	    		$(this).find('.fm-button-main').removeClass('fm-button-main-mobile-open');

	    	}
	    });
	},

	isScrolledIntoView: function(elem){
	    var docViewTop = $(window).scrollTop();
	    var docViewBottom = docViewTop + $(window).height();
	    var elemTop = $(elem).offset().top;
	    var elemBottom = elemTop + $(elem).height();
	    return ((elemBottom <= docViewBottom) && (elemTop >= docViewTop));
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

		// ctt+='<li class="floatingMenuCtt">colocar botao aqui</li>';

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
	fechaAutores: function() {

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

	},
	IsMobile: false,
	IsTablet: false,
	IsTabletPortrait: false,
	IsDesktop: false,
	IsHD: false,
	isOldIE: false,
	DetectMobile: function(userAgent) {
		var mobile = {};

		// valores do http://detectmobilebrowsers.com/
	    mobile.detectMobileBrowsers = {
	        fullPattern: /(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i,
	        shortPattern: /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i
	    };

	    return mobile.detectMobileBrowsers.fullPattern.test(userAgent) ||
        	mobile.detectMobileBrowsers.shortPattern.test(userAgent.substr(0,4));
	},
	DetectTablet: function(userAgent) {
		var tablets = {};

		// valores do http://detectmobilebrowsers.com/
	    tablets.detectMobileBrowsers = {
	        tabletPattern: /android|ipad|playbook|silk/i
	    };

		return tablets.detectMobileBrowsers.tabletPattern.test(userAgent);
	},
	SetScreen: function() {
		var w = $(window).innerWidth(),
			orientation = window.matchMedia("(orientation: portrait)").matches;

		if(w > 990) Article.IsDesktop = true;
		if(w > 1206) Article.IsHD = true;

		if(Article.DetectMobile(navigator.userAgent))
			Article.IsMobile = true;

		if(Article.DetectTablet(navigator.userAgent)) {
			Article.IsTablet = true;

			if(orientation)
				Article.IsTabletPortrait = true;
			else
				Article.IsTabletPortrait = false;

			window.addEventListener("orientationchange", function() {
			    if(screen.orientation.angle == 0)
			    	Article.IsTabletPortrait = true;
			    else
			    	Article.IsTabletPortrait = false;
			});
		}

		if(navigator.appVersion.indexOf("MSIE 8") > -1) {
			Article.IsMobile = false;
			Article.IsTablet = false;
			Article.IsDesktop = true;
			Article.IsOldIE = true;
			Article.IsHD = false;
		}
	},
};

$(function() {

	if($("body.article").length)
		Article.Init();
});