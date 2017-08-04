// @codekit-prepend "./vendor/jquery-1.11.0.min.js";
// @codekit-prepend "./vendor/bootstrap.js";
// @codekit-prepend "./vendor/jquery-ui.min.js";
// @codekit-prepend "./plugins.js";
// @codekit-prepend "./scielo-article.js";

$(function() {
	Article.Init(); 

	$(".goto").on("click",function(e) {
		e.preventDefault();

		var d = $(this).attr("href");
		d = d.replace("#","");

		var p = $("a[name="+d+"]").offset();

		$("html,body").animate({
			scrollTop: (p.top-60)
		},500);
	});

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
});