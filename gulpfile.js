// include gulp  and path modules:
var path = require('path');
var gulp = require('gulp');

// include plug-ins: gulp-concat, gulp-uglify, gulp-strip-debug, gulp-less
var concat = require('gulp-concat');
var stripDebug = require('gulp-strip-debug');
var uglify = require('gulp-uglify');
var less = require('gulp-less');
var minifyCSS = require('gulp-minify-css');

gulp.task('default', function() {
  console.log('\nTasks para processar os JS:');
  console.log('\t- process-scielo-bundle-js: para gerar o scielo-bundle.js');
  console.log('\t- process-scielo-article-js: para gerar o scielo-article.js');
  console.log('\t- process-scielo-article-standalone-js: para gerar o scielo-bundle.js');
  console.log('\t- process-all-js: para processar todas as tasks (JS) anteriores num paso só.');
  console.log('\nTasks para processar os LESS e gerar os CSS:');
  console.log('\t- process-scielo-bundle-less: para gerar o scielo-bundle.less');
  console.log('\t- process-scielo-article-less: para gerar o scielo-article.js');
  console.log('\t- process-scielo-article-standalone-less: para gerar o scielo-article-standalone.less');
  console.log('\t- process-scielo-bundle-print-less: para gerar o scielo-bundle-print.less');
  console.log('\t- process-all-less: para processar todas as tasks (less) anteriores num paso só.');
  console.log('\nTasks para processar TUDO:');
  console.log('\t- process-all: chama as tasks: "process-all-js" e "process-all-less"');
  console.log('\nTasks para monitorar (watch) arquivos LESS e JS:');
  console.log('\t- watch-all: cada mudança de arquivos *.less e *.js (da pasta /static/) e chama: "process-all-less" e "process-all-js" respectivamente');
});

// caminho da pasta 'opac/webapp/static/'
var static_folder_path = path.join(__dirname, 'opac/webapp/static/');
console.info('[INFO] [gulpfile.js] path da pasta static:\t', static_folder_path);

var paths = {
    // caminho relativo da pasta 'static/js/'
    'static_js': path.join(static_folder_path, 'js/'),
    // caminho relativo da pasta 'static/less/'
    'static_less': path.join(static_folder_path, 'less/'),
    // caminho relativo da pasta 'static/css/'
    'static_css': path.join(static_folder_path, 'css/'),
}

console.info('[INFO] [gulpfile.js] path da pasta static/js:\t', paths['static_js']);
console.info('[INFO] [gulpfile.js] path da pasta static/less:\t', paths['static_less']);
console.info('[INFO] [gulpfile.js] path da pasta static/css:\t', paths['static_css']);

var target_src = {
    'js': {
        'scielo-bundle': [
            // instruções do CodeKit (designer) no arquivo: scielo-bundle.js
            // @codekit-prepend "./vendor/jquery-1.11.0.min.js";
            // @codekit-prepend "./vendor/bootstrap.js";
            // @codekit-prepend "./vendor/jquery-ui.min.js";
            // @codekit-prepend "./plugins.js";
            // @codekit-prepend "./main.js";
            path.join(paths['static_js'], 'vendor/jquery-1.11.0.min.js'),
            path.join(paths['static_js'], 'vendor/bootstrap.js'),
            path.join(paths['static_js'], 'vendor/jquery-ui.min.js'),
            path.join(paths['static_js'], 'plugins.js'),
            path.join(paths['static_js'], 'main.js'),
            // nossos JS:
            path.join(paths['static_js'], 'common.js'),
            path.join(paths['static_js'], 'moment.js'),
            path.join(paths['static_js'], 'moment_locale_pt_br.js'),
            path.join(paths['static_js'], 'moment_locale_es.js'),
            path.join(paths['static_js'], 'recaptcha-api.js'),
        ],
        'scielo-article': [
            path.join(paths['static_js'], 'scielo-article.js'),
        ],
        'scielo-article-standalone': [
            // instruções do CodeKit (designer) no arquivo: scielo-article-standalone.js
            // @codekit-prepend "./vendor/jquery-1.11.0.min.js";
            // @codekit-prepend "./vendor/bootstrap.js";
            // @codekit-prepend "./vendor/jquery-ui.min.js";
            // @codekit-prepend "./plugins.js";
            // @codekit-prepend "./scielo-article.js";
            path.join(paths['static_js'], 'vendor/jquery-1.11.0.min.js'),
            path.join(paths['static_js'], 'vendor/bootstrap.js'),
            path.join(paths['static_js'], 'vendor/jquery-ui.min.js'),
            path.join(paths['static_js'], 'plugins.js'),
            path.join(paths['static_js'], 'scielo-article.js'),
        ],
    },
    'less': {
        'scielo-bundle': [
            path.join(paths['static_less'], 'scielo-bundle.less'),
            path.join(paths['static_less'], 'style.less')
        ],
        'scielo-article': [
            path.join(paths['static_less'], 'scielo-article.less')
        ],
        'scielo-article-standalone': [
            path.join(paths['static_less'], 'scielo-article-standalone.less')
        ],
        'scielo-bundle-print': [
            path.join(paths['static_less'], 'scielo-bundle-print.less')
        ],
    }
}

var output = {
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
}

// Task para gerar o scielo-bundle.js
gulp.task('process-scielo-bundle-js', function() {
    var source_file = target_src['js']['scielo-bundle'];
    var output_file = output['js']['scielo-bundle'];
    var output_folder = output['js']['folder'];
    console.info('[INFO] [task: process-scielo-bundle-js] - source file:\t', source_file);
    console.info('[INFO] [task: process-scielo-bundle-js] - output file:\t', output_file);
    console.info('[INFO] [task: process-scielo-bundle-js] - output folder:\t', output_folder);
    gulp.src(source_file)
        .pipe(concat(output_file))
        .pipe(stripDebug())
        .pipe(uglify())
        .pipe(gulp.dest(output_folder)
    );
});

// Task para gerar o scielo-article.js
gulp.task('process-scielo-article-js', function() {
    var source_file = target_src['js']['scielo-article'];
    var output_file = output['js']['scielo-article'];
    var output_folder = output['js']['folder'];
    console.info('[INFO] [task: process-scielo-article-js] - source file:\n', source_file);
    console.info('[INFO] [task: process-scielo-article-js] - output file:\t', output_file);
    console.info('[INFO] [task: process-scielo-article-js] - output folder\t:', output_folder);
    gulp.src(source_file)
        .pipe(concat(output_file))
        .pipe(stripDebug())
        .pipe(uglify())
        .pipe(gulp.dest(output_folder)
    );
});

// Task para gerar o scielo-article-standalone.js
gulp.task('process-scielo-article-standalone-js', function() {
    var source_file = target_src['js']['scielo-article-standalone'];
    var output_file = output['js']['scielo-article-standalone'];
    var output_folder = output['js']['folder'];
    console.info('[INFO] [task: process-scielo-article-standalone-js] - source file:\n', source_file);
    console.info('[INFO] [task: process-scielo-article-standalone-js] - output file:\t', output_file);
    console.info('[INFO] [task: process-scielo-article-standalone-js] - output folder:\t', output_folder);
    gulp.src(source_file)
        .pipe(concat(output_file))
        .pipe(stripDebug())
        .pipe(uglify())
        .pipe(gulp.dest(output_folder)
    );
});

// Task para rodar as tasks: "process-scielo-*-js" num paso só
gulp.task('process-all-js',
    [
        'process-scielo-bundle-js',
        'process-scielo-article-js',
        'process-scielo-article-standalone-js',
    ],
    function() {}
);

// Task para gerar o scielo-bundle.less
gulp.task('process-scielo-bundle-less', function(){
    var source_file = target_src['less']['scielo-bundle'];
    var output_file = output['css']['scielo-bundle'];
    var output_folder = output['css']['folder'];
    console.info('[INFO] [task: process-scielo-bundle-less] - source file:\n', source_file);
    console.info('[INFO] [task: process-scielo-bundle-less] - output file:\t', output_file);
    console.info('[INFO] [task: process-scielo-bundle-less] - output folder:\t', output_folder);

    gulp.src(source_file)
        .pipe(concat(output_file))
        .pipe(less(output_file))
        .pipe(minifyCSS())
        .pipe(gulp.dest(output_folder)
    );
});

// Task para gerar o scielo-article.less
gulp.task('process-scielo-article-less', function(){
    var source_file = target_src['less']['scielo-article'];
    var output_file = output['css']['scielo-article'];
    var output_folder = output['css']['folder'];
    console.info('[INFO] [task: process-scielo-article-less] - source file:\n', source_file);
    console.info('[INFO] [task: process-scielo-article-less] - output file:\t', output_file);
    console.info('[INFO] [task: process-scielo-article-less] - output folder:\t', output_folder);

    gulp.src(source_file)
        .pipe(concat(output_file))
        .pipe(less(output_file))
        .pipe(minifyCSS())
        .pipe(gulp.dest(output_folder)
    );
});

// Task para gerar o scielo-article-standalone.less
gulp.task('process-scielo-article-standalone-less', function(){
    var source_file = target_src['less']['scielo-article-standalone'];
    var output_file = output['css']['scielo-article-standalone'];
    var output_folder = output['css']['folder'];
    console.info('[INFO] [task: process-scielo-article-standalone-less] - source file:\n', source_file);
    console.info('[INFO] [task: process-scielo-article-standalone-less] - output file:\t', output_file);
    console.info('[INFO] [task: process-scielo-article-standalone-less] - output folder:\t', output_folder);

    gulp.src(source_file)
        .pipe(concat(output_file))
        .pipe(less(output_file))
        .pipe(minifyCSS())
        .pipe(gulp.dest(output_folder)
    );
});

// Task para gerar o scielo-bundle-print.less
gulp.task('process-scielo-bundle-print-less', function(){
    var source_file = target_src['less']['scielo-bundle-print'];
    var output_file = output['css']['scielo-bundle-print'];
    var output_folder = output['css']['folder'];
    console.info('[INFO] [task: process-scielo-bundle-print-less] - source file:\n', source_file);
    console.info('[INFO] [task: process-scielo-bundle-print-less] - output file:\t', output_file);
    console.info('[INFO] [task: process-scielo-bundle-print-less] - output folder:\t', output_folder);

    gulp.src(source_file)
        .pipe(concat(output_file))
        .pipe(less(output_file))
        .pipe(minifyCSS())
        .pipe(gulp.dest(output_folder)
    );
});

// Task para rodar as tasks: "process-scielo-*-less" num paso só
gulp.task('process-all-less',
    [
        'process-scielo-bundle-less',
        'process-scielo-article-less',
        'process-scielo-article-standalone-less',
        'process-scielo-bundle-print-less',
    ],
    function() {}
);

// Task para rodar as tasks: "process-scielo-*-js" e "process-scielo-*-less" num paso só
gulp.task('process-all',
    [
        'process-all-js',
        'process-all-less',
    ],
    function() {}
);

gulp.task('watch-all', function () {
    // LESS
    var less_files_glob = paths['static_less'] + '*.less';
    console.info('[INFO] [task: watch-all] criando um watch para arquivos LESS:\t', less_files_glob);
    var watcher_less = gulp.watch(less_files_glob, ['process-all-less']);

    // JS
    var js_files_glob = paths['static_js'] + '*.js';
    console.info('[INFO] [task: watch-all] criando um watch para arquivos JS:\t', js_files_glob);
    var watcher_js = gulp.watch(js_files_glob, ['process-all-js']);
});
