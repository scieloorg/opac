$(function() {
  // inicializamos os dropdowns tooltips:
  $('.dropdown-toggle').dropdown();
  $('[data-toggle="tooltip"], .dropdown-tooltip').tooltip();

  // Caso exista erro ao tentar carregar a imagem subistitui por uma imagem de
  // fallback para as tags imgs que estão com o class="image".
  $(".image" ).on("error", function() {
      this.src = "/static/img/fallback_image.png"
  });

  $(".collapseAbstractBlock").on("click", function(e) {
    e.preventDefault();
    var t = $(this),
        id = '#' + t.data("id"),
        content = $(id);

    if(content.is(":visible")) {
        content.slideUp();
        t.removeClass("opened");
    } else {
        content.slideDown();
        t.addClass("opened");
    }

  });

  $('.modal').on('hidden.bs.modal', function (e) {
    $(this)
      .find("input[type=text], textarea, select")
         .val('')
         .end()
      .find("input[type=checkbox], input[type=radio]")
         .prop("checked", "")
         .end();
  });

});
