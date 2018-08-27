$(document).ready(function () {
    collection = {
        init: function () {

            collection.createList();
            collection.eventDeleteCollection();

            $(".shareCollection").on('click', function () {

                var title = $('meta[name=citation_title]').prop("content");
                var url = $('meta[name=citation_pdf_url]').prop("content");

                // verifica se tem dados
                var articleCollection = localStorage.getItem('collection');

                if (articleCollection === null) {

                    var collectionJson = {
                        name: "",
                        items: [
                            {
                                title: title,
                                url: url
                            }
                        ]
                    };

                    // Não tem uma lista, então cria
                    localStorage.setItem('collection', JSON.stringify(collectionJson));

                } else {

                    // Cria um objeto json
                    var json = $.parseJSON(articleCollection);
                    // flag para saber se ja existe no array
                    var exists = false;

                    $.each(json.items, function (i, v) {
                        // Se existir no array marca a flag
                        if (this.title === title) {
                            exists = true;
                        }
                    });
                    // Se não existe inclui
                    if (exists === false) {
                        json.items.push({ title: title, url: url });
                        localStorage.setItem('collection', JSON.stringify(json));
                    }
                }
            });

        },
        eventDeleteArticle: function () {

            $(".item-action-button").on("click", function () {

                var url = $(this).data("url");

                // verifica se tem dados
                var articleCollection = localStorage.getItem('collection');

                if (articleCollection !== null) {

                    // Cria um objeto json
                    var json = $.parseJSON(articleCollection);
                    var indice = -1;
                    $.each(json.items, function (i, v) {
                        // Se existir no array marca a flag
                        if (this.url === url) {
                            indice = i;
                        }
                    });

                    if (indice >= 0) {
                        json.items.splice(indice, 1);
                        localStorage.setItem('collection', JSON.stringify(json));
                        collection.createList();
                    }
                }

            });
        },
        eventDeleteCollection() {

            $(".delete-button").on("click", function () {
                window.localStorage.clear();
                collection.createList();
            });
        },
        createList: function () {

            // verifica se tem dados
            var articleCollection = localStorage.getItem('collection');

            if (articleCollection === null || $.parseJSON(articleCollection).items.length === 0) {

                var html =
                    "<li>" +
                    "    <div class='col-md-12'>" +
                    "        <span class='item-description'>Nao existem artigos na colecao</span>" +
                    "    </div>" +
                    "</li>";

                $(".article-list").empty().append(html);
            } else {

                // Cria um objeto json
                var json = $.parseJSON(articleCollection);
                var html = "";

                $.each(json.items, function (i, v) {

                    html +=
                        "<li>" +
                        "    <div class='col-md-10'>" +
                        "        <span class='item-description'>" + this.title + "</span>" +
                        "    </div>" +
                        "    <div class='col-md-2  item-action'>" +
                        "        <button type='button' class='btn item-action-button' data-url=" + this.url + ">" +
                        "            <span class='glyphicon glyphicon-trash'></span>" +
                        "        </button>" +
                        "    </div>" +
                        "</li>";
                });

                html +=
                    "<li>" +
                    "    <div class='col-md-12'>" +
                    "        <button type='button' class='btn redirect-button'>" +
                    "            <span class='glyphicon glyphicon-eye-open'></span> Visualizar colecao" +
                    "        </button>" +
                    "        <button type='button' class='btn delete-button' style='font-size:12px'>" +
                    "            <span class='glyphicon glyphicon-eye-open'></span> Excluir colecao" +
                    "        </button>" +
                    "    </div>" +
                    "</li>";

                $(".article-list").empty().append(html);
            }

            collection.eventDeleteArticle();
        }
    }

    collection.init();
});