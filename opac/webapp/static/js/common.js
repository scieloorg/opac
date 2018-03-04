$(function() {
  // inicializamos os dropdowns tooltips:
  $('.dropdown-toggle').dropdown();
  $('[data-toggle="tooltip"], .dropdown-tooltip').tooltip();

  // Caso exista erro ao tentar carregar a imagem subistitui por uma imagem de
  // fallback para as tags imgs que estão com o class="image".
  $(".image" ).on("error", function() {
      this.src = "/static/img/fallback_image.png"
  });

  collapseAbstract = $(".collapseAbstract,.collapseAbstractBlock");

  collapseAbstract.on("click", function(e) {
    e.preventDefault();
    var t = $(this);
        id = '#' + $(this).attr("data-id");
        content = $(id)

    if(content.is(":visible")) {
        content.slideUp("show");
        $(this).addClass("collapseAbstractBlock");
        $(this).removeClass("collapseAbstract");
    } else {
        content.slideDown("show");
        $(this).removeClass("collapseAbstractBlock");
        $(this).addClass("collapseAbstract");
    }

  });


});
