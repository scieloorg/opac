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