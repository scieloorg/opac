const { src, dest, watch, series, parallel } = require('gulp');
const path = require('path');
const less = require('gulp-less');
const cleanCSS = require('gulp-clean-css');
const uglify = require('gulp-uglify');
const sourceMaps = require('gulp-sourcemaps');
const connect = require('gulp-connect');
const gutil = require('gulp-util');
const rename = require('gulp-rename');
const concat = require('gulp-concat');
const minifyCSS = require('gulp-minify-css');


// caminho da pasta 'node_modules/bootstrap'
let node_folder_path = path.join(__dirname, 'node_modules/');
console.info('[INFO] [gulpfile.js] path da pasta node_modules:\t', node_folder_path);

// caminho da pasta 'opac/webapp/static/'
let static_folder_path = path.join(__dirname, 'opac/webapp/static/');
console.info('[INFO] [gulpfile.js] path da pasta static:\t', static_folder_path);

let paths = {

    // caminho relativo da pasta 'bootstrap/js/ dentro do node_modules, fora do projeto'
    'bootstrap_js': path.join(node_folder_path, 'bootstrap/dist/js/'),
    // caminho relativo da pasta 'jquery/dist/ dentro do node_modules, fora do projeto'
    'jquery_js': path.join(node_folder_path, 'jquery/dist/'),
    // caminho relativo da pasta 'jquery-typeahead/dist/ dentro do node_modules, fora do projeto'
    'jquery-typeahead_js': path.join(node_folder_path, 'jquery-typeahead/dist/'),

    // caminho relativo da pasta 'static/js/'
    'static_js': path.join(static_folder_path, 'js/'),
    // caminho relativo da pasta 'static/less/'
    'static_less': path.join(static_folder_path, 'less/'),
    // caminho relativo da pasta 'static/css/'
    'static_css': path.join(static_folder_path, 'css/'),
};

console.info('[INFO] [gulpfile.js] path da pasta bootstrap/js:\t', paths['bootstrap_js']);
console.info('[INFO] [gulpfile.js] path da pasta bootstrap/less:\t', paths['bootstrap_less']);
console.info('[INFO] [gulpfile.js] path da pasta bootstrap/css:\t', paths['bootstrap_css']);

console.info('[INFO] [gulpfile.js] path da pasta static/js:\t', paths['static_js']);
console.info('[INFO] [gulpfile.js] path da pasta static/less:\t', paths['static_less']);
console.info('[INFO] [gulpfile.js] path da pasta static/css:\t', paths['static_css']);

let target_src = {
    'js': {
        'scielo-bundle': [
            // instruções JS (designer)
            path.join(paths['jquery_js'], 'jquery.js'),
            path.join(paths['bootstrap_js'], 'bootstrap.js'),
            path.join(paths['jquery-typeahead_js'], 'jquery.typeahead.min.js'),
            path.join(paths['static_js'], 'plugins.js'),
            path.join(paths['static_js'], 'main.js'),
            
            // instruções JS (equipe scielo)
            path.join(paths['static_js'], 'common.js'),
            path.join(paths['static_js'], 'moment.js'),
            path.join(paths['static_js'], 'moment_locale_pt_br.js'),
            path.join(paths['static_js'], 'moment_locale_es.js'),
            path.join(paths['static_js'], 'modal_forms.js'),
        ],
        'scielo-article': [
            path.join(paths['static_js'], 'scielo-article.js')

        ],
        'scielo-article-standalone': [
            path.join(paths['jquery_js'], 'jquery.js'),
            path.join(paths['bootstrap_js'], 'bootstrap.js'),
            path.join(paths['static_js'], 'plugins.js'),
            path.join(paths['static_js'], 'scielo-article.js'),
        ],
    },
    'less': {
        'scielo-bundle': [
            path.join(paths['static_less'], 'scielo-bundle.less'),
            path.join(paths['static_less'], 'style.less'),
            path.join(paths['static_less'], 'jquery.typeahead.less')
        ],
        'scielo-article': [
            path.join(paths['static_less'], 'scielo-article.less')
        ],
        'bootstrap': [
            path.join(paths['static_less'], 'bootstrap.less')
        ],
        'scielo-article-standalone': [
            path.join(paths['static_less'], 'scielo-article-standalone.less')
        ],
        'scielo-bundle-print': [
            path.join(paths['static_less'], 'scielo-bundle-print.less')
        ],
    }
};

let output = {
    'js': {
        'folder': paths['static_js'],
        // caminho dos arquivos JS para salvar os resultados
        'scielo-bundle': 'scielo-bundle-min.js',
        'scielo-article': 'scielo-article-min.js',
        'scielo-article-standalone': 'scielo-article-standalone-min.js',
    },
    'css': { // caminho dos arquivos CSS para salvar os resultados
        'folder': paths['static_css'],
        'scielo-bundle': 'scielo-bundle.css',
        'scielo-article': 'scielo-article.css',
        'scielo-article-standalone': 'scielo-article-standalone.css',
        'scielo-bundle-print': 'scielo-bundle-print.css',
    }
};

function processScieloBundleLess(){
    return src(target_src['less']['scielo-bundle'])
    .pipe(
        sourceMaps.init()
    )
    .pipe(
        less().on('error', function(err) {
            gutil.log(err);
            this.emit('end');
        }))
    .pipe(
        cleanCSS()
    )
    .pipe(
        minifyCSS()
    )
    .pipe(
        dest(output['css']['folder'])
    )
    .pipe(
        connect.reload()
    );
}

function processScieloArticleLess(){
    return src(target_src['less']['scielo-article'])
    .pipe(
        sourceMaps.init()
    )
    .pipe(
        less().on('error', function(err) {
            gutil.log(err);
            this.emit('end');
        }))
    .pipe(
        cleanCSS()
    )
    .pipe(
        minifyCSS()
    )
    .pipe(
        dest(output['css']['folder'])
    )
    .pipe(
        connect.reload()
    );
}

function watchProcessScieloBundleLess() {
    return watch(paths['static_less'], processScieloBundleLess);
}

function watchProcessScieloArticleLess() {
    return watch(paths['static_less'], processScieloArticleLess);
}

exports.watch = series(
    processScieloBundleLess,
    processScieloArticleLess,
    
    parallel(
        watchProcessScieloBundleLess,
        watchProcessScieloArticleLess
    )
)


exports.default = series(
    processScieloArticleLess
);

