$(function() {
  // inicializamos os dropdowns tooltips:
  $('.dropdown-toggle').dropdown();
  $('[data-toggle="tooltip"], .dropdown-tooltip').tooltip();

  // Caso exista erro ao tentar carregar a imagem subistitui por uma imagem de
  // fallback para as tags imgs que estão com o class="image".
  $( ".image" ).on("error", function() {
      this.src = "/static/img/fallback_image.png"
  });

});
