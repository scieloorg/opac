"use strict";

var JournalListAlpha = {
  page: 1,
  url: null,
  template_row_selector: null,
  template_result_body_selector: null,
  query_input_selector: null,
  query_filter_name: null,
  loading_selector: null,
  has_next: false,
  next_num: 0,

  error_msg_selector: null,
  empty_msg_selector: null,

  error_template_compiled: null,
  empty_template_compiled: null,

  clear_list:function(){
    $(this.template_result_body_selector).empty();
  },

  search: function(clear){
    if (clear) {
      this.page = 1;
    }

    var is_loading = $(this.loading_selector).css('display') != 'none';
    if (is_loading) {
      return;
    }

    var self = this;
    var page = this.page;
    var query = $.trim(
      $(this.query_input_selector).val()
    );
    var query_filter = $.trim(
      $('input[name="' + this.query_filter_name +'"]').filter(":checked").val()
    );
    $(this.loading_selector).show();
    $.getJSON(self.url, {
      page: page,
      query: query,
      query_filter: query_filter
    }).done(function(data){
      self.render_results(data, clear);
    }).fail(function(){
      $(self.loading_selector).hide();
      self.render_error_msg();
    });
  },

  search_next_page: function(){
    if (this.has_next) {
      this.page = this.next_num;
      this.search(false);
    }
  },

  render_results: function(result_data, clear){
    this.page = result_data['current_page'];
    $('.collectionListTotalInfo').text('(total '+ result_data['total'] + ')');
    this.has_next = result_data['has_next'];
    this.next_num = result_data['next_num'];

    this.render_list(result_data['journals'], clear);

    $(this.loading_selector).hide();
    $('[data-toggle="tooltip"]').tooltip();
  },

  render_list: function(result_list, clear){
    if (clear){
      this.clear_list();
    }
    if (result_list.length == 0) {
      this.render_empty_list();
    } else {
      for (var i = 0; i < result_list.length; i++) {
        this.render_row(result_list[i]);
      }
    }
  },

  render_row: function(result_row){
    var compiled = _.template($(this.template_row_selector).html());
    var row_html = compiled({'journal': result_row});
    $(this.template_result_body_selector).append(row_html);
  },

  render_empty_list: function(){
    var self = this;
    this.clear_list();
    $(this.template_result_body_selector).append(
      self.empty_template_compiled
    );
  },

  render_error_msg: function(){
    var self = this;
    this.clear_list();
    $(this.template_result_body_selector).append(
      self.error_template_compiled
    );
  },

  initialize: function(url, template_row_selector, template_result_body_selector,
                       query_input_selector, query_filter_name, loading_selector,
                       error_msg_selector, empty_msg_selector){
    this.url = url;
    this.template_row_selector = template_row_selector;
    this.template_result_body_selector = template_result_body_selector;
    this.query_input_selector = query_input_selector;
    this.query_filter_name = query_filter_name;
    this.loading_selector = loading_selector;

    this.error_msg_selector = error_msg_selector;
    this.empty_msg_selector = empty_msg_selector;

    this.error_template_compiled = _.template($(this.error_msg_selector).html());
    this.empty_template_compiled = _.template($(this.empty_msg_selector).html());

    var self = this;
    $(this.query_input_selector).on("keyup", function(){
      if (this.value.length >= 3 || $.trim(this.value).length === 0) {
        self.search(true);
      }
    });
    $('input[name="' + this.query_filter_name + '"]').change(function(){
      self.search(true);
    });

    $(window).on("scroll",function() {

      var st = Math.max(document.documentElement.scrollTop, document.body.scrollTop);
      if((st + document.documentElement.clientHeight) >= document.documentElement.scrollHeight){
        self.search_next_page();
      }
    });
    return this
  }
}


var JournalCategorizedList = {

  url: '/',
  template_results_selector: '#template_collection_list_table',
  filter: 'areas',
  query_filter_name: null,
  results_container_selector: null,
  query_input_selector:  null,
  loading_selector: null,

  error_msg_selector: null,
  empty_msg_selector: null,

  error_template_compiled: null,
  empty_template_compiled: null,

  main_label: 'Periódico',
  grouper_name_plural: 'temas',

  clear_list:function(){
    $(this.results_container_selector).empty();
  },

  search: function(){
    var self = this;
    var query = $.trim(
      $(this.query_input_selector).val()
    );
    var query_filter = $.trim(
      $('input[name="' + this.query_filter_name +'"]').filter(":checked").val()
    );
    this.clear_list();
    $(this.loading_selector).show();

    $.getJSON(self.url, {
      query: query,   /* the text from input */
      query_filter: query_filter, /* the radio button selected */
      filter: this.filter, /* arear or WoS listing */
    }).done(function(data){
      self.render_results(data);
      $(self.loading_selector).hide();
    }).fail(function(){
      self.render_error_msg();
      $(self.loading_selector).hide();
    });

  },

  render_results: function(result_data){

    if (!_.has(result_data, 'meta')){
      this.render_error_msg();
      return;
    } else if (result_data['meta']['total'] === 0) {
      this.render_empty_list();
      return;
    }

    var compiled = _.template($(this.template_results_selector).html());
    var collection_list_table_html = compiled({
      'data': result_data,
      'main_label': this.main_label,
      'grouper_name_plural': this.grouper_name_plural,
    });
    $(this.results_container_selector).html(collection_list_table_html);

    $('[data-toggle="tooltip"]').tooltip();

    this.collaps_expand_rows();

    $(this.results_container_selector).trigger('results_loaded');

  },

  render_empty_list: function(){

    var self = this;
    this.clear_list();

    $(this.results_container_selector).html(
      self.empty_template_compiled
    );

  },

  render_error_msg: function(){
    var self = this;
    this.clear_list();

    $(this.results_container_selector).html(
      self.error_template_compiled
    );

  },

  collaps_expand_rows: function(){

    $('.collapseTitleBlock').off('click').on('click', function(event) {
      event.preventDefault();
      var $this = $(this);
      var target_id = $this.data('target-id');

      if ($this.hasClass('closed')) {
        $this.removeClass('closed');
        $('#' + target_id).slideDown();
      } else {
        $this.addClass('closed');
        $('#' + target_id).slideUp();
      }
    });

  },

  initialize: function(results_container_selector, query_input_selector, query_filter_name,
                       loading_selector, filter, url, error_msg_selector, empty_msg_selector,
                       main_label, grouper_name_plural){

    this.results_container_selector = results_container_selector;
    this.query_input_selector = query_input_selector;
    this.query_filter_name = query_filter_name;
    this.loading_selector = loading_selector;
    this.filter = filter;

    this.url = url;
    this.error_msg_selector = error_msg_selector;
    this.empty_msg_selector = empty_msg_selector;

    this.error_template_compiled = _.template($(this.error_msg_selector).html());
    this.empty_template_compiled = _.template($(this.empty_msg_selector).html());

    this.main_label = main_label;
    this.grouper_name_plural = grouper_name_plural;

    var self = this;
    $(this.query_input_selector).on("keyup", function(){
      if (this.value.length >= 3 || $.trim(this.value).length === 0) {
        self.search();
      }
    });
    $('input[name="' + this.query_filter_name + '"]').change(function(){
      self.search();
    });
    return this;

  }
}

/* download links with query */
function open_download_url(target_url, query_input_selector) {
  var query = $(query_input_selector).val();
  if ($.trim(query) !== '') {
    target_url += '?query=' + encodeURIComponent(query)
  }
  window.location = target_url;
}
